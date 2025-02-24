#!/usr/env python
import os
from argparse import ArgumentParser
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal.windows import tukey
from tqdm.auto import trange

import gwpy.timeseries as ts
from gwpy.detector import Channel

import lalsimulation as lalsim
import lal

import bilby
from bilby.core.prior import Uniform, PriorDict
from bilby.core.utils import check_directory_exists_and_if_not_mkdir, logger
from bilby.gw.conversion import (
    convert_to_lal_binary_black_hole_parameters,
    convert_to_lal_binary_neutron_star_parameters,
)
from bilby.gw.detector import InterferometerList, PowerSpectralDensity
from bilby.gw.detector.calibration import CubicSpline
from bilby.gw.prior import BBHPriorDict, CalibrationPriorDict
from bilby.gw.source import (
    lal_binary_black_hole,
    lal_binary_neutron_star,
)
from bilby.gw.waveform_generator import WaveformGenerator
from bilby_pipe.utils import convert_string_to_dict


def create_parser():
    parser = ArgumentParser(description="Create frame files with injections")
    parser.add_argument("--start-time", type=int)
    parser.add_argument("--end-time", type=int)
    parser.add_argument("--frame-duration", type=int, default=4096)
    parser.add_argument("--sampling-frequency", type=float, default=4096)
    parser.add_argument("--channel-name", type=str, required=True)
    parser.add_argument(
        "--format",
        type=str,
        default="hdf5",
        help="Format to save data in, default is hdf5.",
    )
    parser.add_argument("--outdir", type=str, default=".")
    parser.add_argument(
        "--interferometers",
        default=["H1", "L1", "V1"],
        nargs="*",
        help="IFOs to make data for.",
    )
    parser.add_argument("--inject", dest="inject", action="store_true")
    parser.add_argument(
        "--n-injections", type=int, default=0, help="Number of injections to add."
    )
    parser.add_argument(
        "--injection-prior",
        type=str,
        default=None,
        help="Prior to draw injections from.",
    )
    parser.add_argument(
        "--injection-file",
        type=str,
        default="injections.json",
        help="File to load injections from.",
    )
    parser.add_argument(
        "--psd-dict",
        type=str,
        default="default",
        help="PSD dictionary in bilby_pipe format. Default will use Bilby built in defaults.",
    )
    parser.add_argument(
        "--calibration-dict",
        type=str,
        default="default",
        help="Calibration envelope dictionary in bilby_pipe format. Default will use no miscalibration.",
    )
    parser.add_argument(
        "--exclude-calibration",
        action="store_true",
        help="Exclude calibration from the injections.",
    )
    parser.add_argument(
        "--waveform-approximant",
        type=str,
        default="IMRPhenomXPHM",
        help="Waveform approximant to use."
    )
    parser.add_argument("--seed", type=int)
    parser.add_argument(
        "--zero-noise",
        action="store_true",
        help="Create zero noise data instead of using PSDs.",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        help="Log level to use.",
    )
    parser.set_defaults(inject=False)
    return parser


def td_waveform(params, args):
    approx = params.get("waveform_approximant", "IMRPhenomXPHM")
    if approx == "IMRPhenomXPHM":
        conversion = convert_to_lal_binary_black_hole_parameters
        fdsm = lal_binary_black_hole
    else:
        logger.warning("Assuming a BNS waveform")
        conversion = convert_to_lal_binary_neutron_star_parameters
        fdsm = lal_binary_neutron_star
    params_new, _ = conversion(params)
    chirp_time = lalsim.SimInspiralChirpTimeBound(
        10,
        params_new["mass_1"] * lal.MSUN_SI,
        params_new["mass_2"] * lal.MSUN_SI,
        params_new["a_1"] * np.cos(params_new["tilt_1"]),
        params_new["a_2"] * np.cos(params_new["tilt_2"]),
    )
    chirp_time = max(2 ** (int(np.log2(chirp_time)) + 1), 4)
    wfg = WaveformGenerator(
        duration=chirp_time,
        sampling_frequency=args.sampling_frequency,
        start_time=params["geocent_time"] + 0.2 - chirp_time,
        frequency_domain_source_model=fdsm,
        parameter_conversion=conversion,
        waveform_arguments=dict(
            minimum_frequency=10.0,
            waveform_approximant=approx,
        ),
    )

    wf_pols = wfg.time_domain_strain(params)
    window = tukey(len(wfg.time_array), alpha=0.2 / chirp_time)
    wf_pols["plus"] = (
        np.roll(wf_pols["plus"], -int(args.sampling_frequency * 0.2)) * window
    )
    wf_pols["cross"] = (
        np.roll(wf_pols["cross"], -int(args.sampling_frequency * 0.2)) * window
    )
    return wf_pols, wfg.time_array


def load_injections(args):
    load_functions = dict(
        txt=pd.read_csv,
        dat=pd.read_csv,
        json=pd.read_json,
        hdf5=pd.read_hdf,
        hdf=pd.read_hdf,
        h5=pd.read_hdf,
        pkl=pd.read_pickle,
        pickle=pd.read_pickle,
    )
    if os.path.isfile(args.injection_file):
        ext = Path(args.injection_file).suffix[1:]
        injections = load_functions[ext](
            args.injection_file, key="injections"
        ).iloc[: args.n_injections]
    elif args.injection_prior is not None:
        injection_prior = BBHPriorDict(filename=args.injection_prior)
        injection_prior["geocent_time"] = Uniform(args.start_time, args.end_time)
        injections = pd.DataFrame(injection_prior.sample(args.n_injections))
        injections = injections.sort_values("geocent_time")
        injections.to_json(args.injection_file)
    else:
        logger.info("Failed to load injection set.")
        args.inject = False
        injections = None
    return injections


def do_injection(ifos, injection, channels, strain, args):
    strain_with_inj = strain.copy()
    print(injection)
    parameters = dict(injection)
    parameters["waveform_approximant"] = args.waveform_approximant
    logger.debug(parameters)
    wf_pols, times = td_waveform(parameters, args)
    for ifo in ifos:
        ifo_strain = strain_with_inj[ifo.name]
        channel_name = channels[ifo.name]
        channel = Channel(channel_name)
        time_delay = ifo.time_delay_from_geocenter(
            ra=parameters["ra"],
            dec=parameters["dec"],
            time=parameters["geocent_time"],
        )
        times += time_delay

        signal = np.zeros_like(times)
        for mode in ["plus", "cross"]:
            signal += (
                ifo.antenna_response(
                    ra=parameters["ra"],
                    dec=parameters["dec"],
                    time=parameters["geocent_time"],
                    psi=parameters["psi"],
                    mode=mode,
                )
                * wf_pols[mode]
            )

        inj = ts.TimeSeries(signal, times=times, channel=channel, name=channel_name)
        closest_idx = np.argmin(abs(ifo_strain.xindex.value - inj.xindex.value[0]))
        delta_time = ifo_strain.xindex.value[closest_idx] - inj.xindex.value[0]
        times += delta_time
        inj = ts.TimeSeries(
            signal, times=times, channel=channel, name=channel_name
        )
        ifo_strain = ifo_strain.inject(inj)
        times -= time_delay + delta_time
        strain_with_inj[ifo.name] = ifo_strain
    return strain_with_inj


def main():
    parser = create_parser()
    args = parser.parse_args()
    check_directory_exists_and_if_not_mkdir(args.outdir)
    np.random.seed(args.seed)

    bilby.core.utils.log.setup_logger(log_level=args.log_level)

    if args.psd_dict == "default":
        psd_dict = dict()
    else:
        # manually add braces because bash can't handle it
        psd_dict = convert_string_to_dict("{" + args.psd_dict + "}")

    cal_priors = PriorDict()
    if args.calibration_dict == "default":
        cal_dict = dict()
    else:
        cal_dict = convert_string_to_dict("{" + args.calibration_dict + "}")

    start_time = args.start_time
    duration = args.frame_duration
    frame_end_time = start_time + duration
    base_channel_name = args.channel_name

    injections = load_injections(args)

    for inj_id, injection in enumerate(injections.to_dict(orient="records")):

        ifos = InterferometerList(args.interferometers)
        for ifo in ifos:
            ifo.minimum_frequency = 10
            if ifo.name in psd_dict:
                method = PowerSpectralDensity.from_amplitude_spectral_density_file
                ifo.power_spectral_density = method(psd_dict[ifo.name])
            if not args.exclude_calibration and ifo.name in cal_dict:
                ifo.calibration_model = CubicSpline(
                    prefix=f"recalib_{ifo.name}_",
                    minimum_frequency=ifo.minimum_frequency,
                    maximum_frequency=ifo.maximum_frequency,
                    n_points=10,
                )
                cal_priors.update(CalibrationPriorDict.from_envelope_file(
                    envelope_file=cal_dict[ifo.name],
                    minimum_frequency=ifo.minimum_frequency,
                    maximum_frequency=ifo.maximum_frequency,
                    n_nodes=10,
                    label=ifo.name,
                ))
            else:
                logger.debug(f"Skipping calibration for {ifo}")
        channels = {ifo.name: ":".join([ifo.name, base_channel_name]) for ifo in ifos}
        strain = dict()

        if not args.exclude_calibration:
            cal_injection_parameters = cal_priors.sample(len(injections))
            for key in cal_injection_parameters:
                injections[key] = cal_injection_parameters[key]
            pd.DataFrame(cal_injection_parameters).to_hdf(args.injection_file, key="calibration")

        if not args.zero_noise:
            ifos.set_strain_data_from_power_spectral_densities(
                sampling_frequency=args.sampling_frequency,
                duration=duration,
                start_time=start_time,
            )
        else:
            logger.debug("Generating zero-noise data")
            ifos.set_strain_data_from_zero_noise(
                sampling_frequency=args.sampling_frequency,
                duration=duration,
                start_time=start_time,
            )
        for ifo in ifos:
            channel_name = channels[ifo.name]
            channel = Channel(channel_name)
            ht = ifo.time_domain_strain
            times = ifo.time_array
            temp = ts.TimeSeries(ht, times=times, channel=channel, name=channel_name)
            try:
                strain[ifo.name] = strain[ifo.name].append(temp, inplace=False)
            except (NameError, ValueError, KeyError):
                strain[ifo.name] = temp

        if args.inject:
            strain = do_injection(
                ifos=ifos,
                injection=injection,
                strain=strain,
                channels=channels,
                args=args,
            )

        for ifo in ifos:
            base_name = f"{args.outdir}/injection_{inj_id}_{ifo.name}_{start_time}_{frame_end_time}"
            file_name = f"{base_name}.{args.format}"
            logger.info(f"Saving {file_name}")
            strain[ifo.name].write(file_name, format=args.format)

if __name__ == "__main__":
    main()
