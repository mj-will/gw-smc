#!/usr/bin/env bash
SAMPLER=pocomc
LABEL=2det_det_frame_updated_settings
python \
    generate_super_dag.py \
    ${SAMPLER}_template.ini \
    --outdir outdir_${SAMPLER}_${LABEL}/ \
    --injection-file data/bbh_injections_uniform_chirp_mass.hdf5 \
    --data-dir data/injections/uniform_chirp_mass_mass_ratio/ \
    --n-injections 100 \
    --prior-file bbh_priors.prior \
    --superdag-name superdag_$SAMPLER \
    --detectors H1 L1 \
    --detector-frame \
    --submit
