include config.mk

.PHONY: pp_plot_dynesty_2det pp_plot_dynesty_3det pp_plot_pocomc_2det pp_plot_pocomc_3det pp_plots

BASE_DATA_RELEASE_DIR := $(dir $(patsubst %/,%,$(DATA_RELEASE_PATH)))

GWTC2p1_DATA_RELEASE_PATH := $(GWTC_DATA_RELEASE_PATH)/GWTC-2.1
GWTC3_DATA_RELEASE_PATH := $(GWTC_DATA_RELEASE_PATH)/GWTC-3

$(DATA_RELEASE_PATH):
	cd $(BASE_DATA_RELEASE_DIR) && $(MAKE) data_release

$(GWTC2p1_DATA_RELEASE_PATH):
	cd $(GWTC_DATA_RELEASE_PATH) && $(MAKE)

$(GWTC3_DATA_RELEASE_PATH):
	cd $(GWTC_DATA_RELEASE_PATH) && $(MAKE)

pp_plot_dynesty_2det: $(DATA_RELEASE_PATH)
	python pp_plot.py \
	--result-dir $(DATA_RELEASE_PATH)/simulated_data/pp_tests/dynesty_2det/ \
	--injection-file $(INJ_FILE) \
	--figure-format $(FIG_FORMAT) \
	--filename pp_test_dynesty_2det \
	--outdir $(FIGURE_DIR)

pp_plot_dynesty_3det: $(DATA_RELEASE_PATH)
	python pp_plot.py \
	--result-dir $(DATA_RELEASE_PATH)/simulated_data/pp_tests/dynesty_3det/ \
	--injection-file $(INJ_FILE) \
	--figure-format $(FIG_FORMAT) \
	--filename pp_test_dynesty_3det \
	--outdir $(FIGURE_DIR)

pp_plot_pocomc_2det: $(DATA_RELEASE_PATH)
	python pp_plot.py \
	--result-dir $(DATA_RELEASE_PATH)/simulated_data/pp_tests/pocomc_2det/ \
	--injection-file $(INJ_FILE) \
	--figure-format $(FIG_FORMAT) \
	--filename pp_test_pocomc_2det \
	--outdir $(FIGURE_DIR)

pp_plot_pocomc_3det: $(DATA_RELEASE_PATH)
	python pp_plot.py \
	--result-dir $(DATA_RELEASE_PATH)/simulated_data/pp_tests/pocomc_3det/ \
	--injection-file $(INJ_FILE) \
	--figure-format $(FIG_FORMAT) \
	--filename pp_test_pocomc_3det \
	--outdir $(FIGURE_DIR)

pp_plots: pp_plot_dynesty_2det pp_plot_dynesty_3det pp_plot_pocomc_2det pp_plot_pocomc_3det

.PHONY: GW150914_plots GW200129_plots event_plots

GW150914_plots: $(DATA_RELEASE_PATH) $(GWTC2p1_DATA_RELEASE_PATH)
	gw_smc_utils_plot_event \
		--results $(DATA_RELEASE_PATH)/real_data/GW150914_bilby_result_pocomc.hdf5 \
		--labels pocomc \
		--data-release-path $(GWTC_DATA_RELEASE_PATH) \
		--SID GW150914

GW200129_plots: $(DATA_RELEASE_PATH) $(GWTC3_DATA_RELEASE_PATH)
	gw_smc_utils_plot_event \
		--results $(DATA_RELEASE_PATH)/real_data/GW200129_bilby_result_pocomc.hdf5 \
		--labels pocomc \
		--data-release-path $(GWTC_DATA_RELEASE_PATH) \
		--SID GW200129

event_plots: GW150914_plots GW200129_plots
