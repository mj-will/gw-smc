include config.mk

BASE_DATA_RELEASE_DIR := $(dir $(patsubst %/,%,$(DATA_RELEASE_PATH)))
BASE_ADDITIONAL_DATA_RELEASE_DIR := $(dir $(patsubst %/,%,$(ADDITIONAL_DATA_RELEASE_PATH)))

GWTC2p1_DATA_RELEASE_PATH := $(GWTC_DATA_RELEASE_PATH)/GWTC-2.1
GWTC3_DATA_RELEASE_PATH := $(GWTC_DATA_RELEASE_PATH)/GWTC-3

NOTEBOOKS := $(wildcard *.ipynb)
MARKERS := $(NOTEBOOKS:.ipynb=.run)

.PHONY: all
all: notebooks event_plots

$(DATA_RELEASE_PATH):
	cd $(BASE_DATA_RELEASE_DIR) && $(MAKE) data_release

$(ADDITIONAL_DATA_RELEASE_PATH):
	cd $(BASE_ADDITIONAL_DATA_RELEASE_DIR) && $(MAKE) data_release_additional

$(GWTC2p1_DATA_RELEASE_PATH):
	cd $(GWTC_DATA_RELEASE_PATH) && $(MAKE)

$(GWTC3_DATA_RELEASE_PATH):
	cd $(GWTC_DATA_RELEASE_PATH) && $(MAKE)


figures/GW150914_intrinsic.pdf figures/GW150914_localization.pdf: $(DATA_RELEASE_PATH) $(GWTC2p1_DATA_RELEASE_PATH)
	gw_smc_utils_plot_event \
		--results $(DATA_RELEASE_PATH)/real_data/GW150914_bilby_result_pocomc.hdf5 \
		--labels pocomc \
		--data-release-path $(GWTC_DATA_RELEASE_PATH) \
		--SID GW150914

figures/GW150914_intrinsic.png figures/GW150914_localization.png: $(DATA_RELEASE_PATH) $(GWTC2p1_DATA_RELEASE_PATH)
	gw_smc_utils_plot_event \
		--results $(DATA_RELEASE_PATH)/real_data/GW150914_bilby_result_pocomc.hdf5 \
		--labels pocomc \
		--data-release-path $(GWTC_DATA_RELEASE_PATH) \
		--SID GW150914 \
		--extension png

figures/GW200129_intrinsic.pdf figures/GW200129_localization.pdf: $(DATA_RELEASE_PATH) $(GWTC3_DATA_RELEASE_PATH)
	gw_smc_utils_plot_event \
		--results $(DATA_RELEASE_PATH)/real_data/GW200129_bilby_result_pocomc.hdf5 \
		--labels pocomc \
		--data-release-path $(GWTC_DATA_RELEASE_PATH) \
		--SID GW200129

figures/GW200129_intrinsic.png figures/GW200129_localization.png: $(DATA_RELEASE_PATH) $(GWTC3_DATA_RELEASE_PATH)
	gw_smc_utils_plot_event \
		--results $(DATA_RELEASE_PATH)/real_data/GW200129_bilby_result_pocomc.hdf5 \
		--labels pocomc \
		--data-release-path $(GWTC_DATA_RELEASE_PATH) \
		--SID GW200129 \
		--extension png

.PHONY: GW150914_plots GW200129_plots
GW150914_plots: figures/GW150914_intrinsic.pdf figures/GW150914_localization.pdf
GW200129_plots: figures/GW200129_intrinsic.pdf figures/GW200129_localization.pdf

.PHONY: event_plots
event_plots: GW150914_plots GW200129_plots

.PHONY: event_plots_png
event_plots_png: figures/GW150914_intrinsic.png figures/GW150914_localization.png figures/GW200129_intrinsic.png figures/GW200129_localization.png

%.run: %.ipynb
	jupyter nbconvert --to notebook --execute --inplace $< && touch $@

.PHONY: notebooks
notebooks: $(MARKERS)

.PHONY: figures
figures: all


figures.zip: figures
	zip -r $@ figures

.PHONY: tables
tables: bns_results.run

tables.zip: tables
	zip -r $@ tables

.PHONY: clean
clean:
	rm -f $(MARKERS)
	rm -rf figures
	rm -rf tables
	rm -f figures.zip
	rm -f tables.zip
