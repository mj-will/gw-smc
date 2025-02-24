#!/usr/bin/env bash
SAMPLER=dynesty
python \
    generate_super_dag.py \
    ${SAMPLER}_template.ini \
    --outdir outdir_${SAMPLER}_3det_sky_frame_uniform_chirp_mass_settings/ \
    --injection-file data/bbh_injections_uniform_chirp_mass.hdf5 \
    --data-dir data/injections/uniform_chirp_mass_mass_ratio/ \
    --n-injections 100 \
    --prior-file bbh_priors.prior \
    --superdag-name superdag_$SAMPLER \
    --submit
