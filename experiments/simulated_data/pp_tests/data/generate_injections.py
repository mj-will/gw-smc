import glob
from copy import deepcopy

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from attrs import define
from tqdm.auto import trange

import bilby
import sys

prior_file = sys.argv[1]
injection_file = sys.argv[2]

prior = bilby.gw.prior.CBCPriorDict(filename=prior_file)

start_time = 1364342418
injection_time = start_time + 256

# TODO: set correct PSDs
asd_files = {
    "H1": "psds/aligo_O3actual_H1.txt",
    "L1": "psds/aligo_O3actual_L1.txt",
    "V1": "psds/avirgo_O3actual.txt",
}
ifos = bilby.gw.detector.InterferometerList(["H1", "L1", "V1"])
ifos.set_strain_data_from_zero_noise(duration=8, sampling_frequency=4096)
for ifo in ifos:
    ifo.minimum_frequency = 20
    ifo.maximum_frequency = 2048
    ifo.power_spectral_density = bilby.gw.detector.psd.PowerSpectralDensity(
        asd_file=asd_files[ifo.name]
    )

wfg = bilby.gw.waveform_generator.WaveformGenerator(
    duration=8,
    sampling_frequency=4096,
    frequency_domain_source_model=bilby.gw.source.lal_binary_black_hole,
    parameter_conversion=bilby.gw.conversion.convert_to_lal_binary_black_hole_parameters,
    waveform_arguments=dict(
        waveform_approximant="IMRPhenomXPHM",
        reference_frequency=20,
        minimum_frequency=5,
    )
)

n_samples = 100

samples = pd.DataFrame(prior.sample(n_samples))
samples["injection_time"] = injection_time
samples["geocent_time"] = injection_time + np.random.uniform(-0.1, 0.1, size=n_samples)
print(samples)
snrs = {ifo.name: np.zeros(n_samples) for ifo in ifos}

for ii in trange(n_samples):
    params = dict(samples.iloc[ii])
    wf = wfg.frequency_domain_strain(params)
    for ifo in ifos:
        signal = ifo.get_detector_response(
            waveform_polarizations=wf, parameters=params
        )
        snrs[ifo.name][ii] = np.real(ifo.optimal_snr_squared(signal))**0.5
snrs["network"] = np.linalg.norm([snrs[ifo.name] for ifo in ifos], axis=0)

print(
    np.percentile(snrs["network"], 10),
    np.percentile(snrs["network"], 50),
    np.percentile(snrs["network"], 90),
)
for key in snrs:
    samples[f"{key}_snr"] = snrs[key]
samples.to_hdf(injection_file, key="injections")
