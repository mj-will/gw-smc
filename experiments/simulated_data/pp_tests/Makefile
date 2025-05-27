include config.mk

INJ_FILE=$(PP_TEST_INJECTION_FILE)
FIG_FORMAT=pdf
FIG_DIR=figures/

.PHONY: pp_plot_pocomc_3det pp_plot_pocomc_2det pp_plot_dynesty_3det pp_plot_dynesty_2det

pp_plot_pocomc_3det:
	python pp_test.py --result-dir $(POCOCMC_PATH_3DET) --injection-file $(INJ_FILE) --figure-format $(FIG_FORMAT) --filename pp_test_pocomc_3det --outdir $(FIG_DIR) --credible-levels-file $(POCOMC_3DET_CREDIBLE_LEVELS_FILE)

pp_plot_pocomc_2det:
	python pp_test.py --result-dir $(POCOCMC_PATH_2DET) --injection-file $(INJ_FILE) --figure-format $(FIG_FORMAT) --filename pp_test_pocomc_2det  --outdir $(FIG_DIR) --credible-levels-file $(POCOMC_2DET_CREDIBLE_LEVELS_FILE)

pp_plot_dynesty_3det:
	python pp_test.py --result-dir $(DYNESTY_PATH_3DET) --injection-file $(INJ_FILE) --figure-format $(FIG_FORMAT) --filename pp_test_dynesty_3det  --outdir $(FIG_DIR) --credible-levels-file $(DYNESTY_3DET_CREDIBLE_LEVELS_FILE)

pp_plot_dynesty_2det:
	python pp_test.py --result-dir $(DYNESTY_PATH_2DET) --injection-file $(INJ_FILE) --figure-format $(FIG_FORMAT) --filename pp_test_dynesty_2det  --outdir $(FIG_DIR) --credible-levels-file $(DYNESTY_2DET_CREDIBLE_LEVELS_FILE)

.PHONY: pp_plots
pp_plots: pp_plot_pocomc_3det pp_plot_pocomc_2det pp_plot_dynesty_3det pp_plot_dynesty_2det

$(PP_TEST_SUMMARY_FILE):
	python produce_summary.py \
		--input-dirs $(POCOMC_3DET_RESULT) $(POCOMC_2DET_RESULT) $(DYNESTY_3DET_RESULT) $(DYNESTY_2DET_RESULT) \
		--n-injections 100 \
		--filename "$@"
