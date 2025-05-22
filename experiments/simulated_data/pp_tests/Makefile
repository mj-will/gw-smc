
INJ_FILE=data/bbh_injections_uniform_chirp_mass.hdf5
FIG_FORMAT=pdf
FIG_DIR=figures/

POCOMC_3DET_RESULT=outdir_pocomc_3det_det_frame_updated_settings/
POCOMC_2DET_RESULT=outdir_pocomc_2det_det_frame_updated_settings/

DYNESTY_3DET_RESULT=outdir_dynesty_3det_det_frame_uniform_chirp_mass/
DYNESTY_2DET_RESULT=outdir_dynesty_2det_det_frame_uniform_chirp_mass/

.PHONY: pp_plot_pocomc_3det pp_plot_pocomc_2det pp_plot_dynesty_3det pp_plot_dynesty_2det

pp_plot_pocomc_3det:
	python pp_test.py --result-dir $(POCOMC_3DET_RESULT) --injection-file $(INJ_FILE) --figure-format $(FIG_FORMAT) --filename pp_test_pocomc_3det --outdir $(FIG_DIR)

pp_plot_pocomc_2det:
	python pp_test.py --result-dir $(POCOMC_2DET_RESULT) --injection-file $(INJ_FILE) --figure-format $(FIG_FORMAT) --filename pp_test_pocomc_2det  --outdir $(FIG_DIR)

pp_plot_dynesty_3det:
	python pp_test.py --result-dir $(DYNESTY_3DET_RESULT) --injection-file $(INJ_FILE) --figure-format $(FIG_FORMAT) --filename pp_test_dynesty_3det  --outdir $(FIG_DIR)

pp_plot_dynesty_2det:
	python pp_test.py --result-dir $(DYNESTY_2DET_RESULT) --injection-file $(INJ_FILE) --figure-format $(FIG_FORMAT) --filename pp_test_dynesty_2det  --outdir $(FIG_DIR)

.PHONY: pp_plots
pp_plots: pp_plot_pocomc_3det pp_plot_pocomc_2det pp_plot_dynesty_3det pp_plot_dynesty_2det