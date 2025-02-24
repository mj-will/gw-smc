#!/usr/bin/env bash

BASE=injections/uniform_chirp_mass_mass_ratio/
PRIOR_FILE=bbh_priors.prior
INJECTIONS=bbh_injections_uniform_chirp_mass.hdf5
ASDS='H1:psds/aligo_O3actual_H1.txt,L1:psds/aligo_O3actual_L1.txt,V1:psds/avirgo_O3actual.txt'

python generate_injections.py ${PRIOR_FILE} ${INJECTIONS}

START_TIME=1364342418
DURATION=512
END_TIME=$((START_TIME + DURATION))

python make_frames.py \
    --seed 150912 \
    --start-time $START_TIME \
    --end-time $END_TIME  \
    --frame-duration $DURATION \
    --outdir $BASE \
    --injection-file $INJECTIONS \
    --n-injections 100 \
    --inject \
    --psd-dict ${ASDS} \
    --exclude-calibration \
    --waveform-approximant IMRPhenomXPHM \
    --channel-name GWSMC \
    --log-level INFO
