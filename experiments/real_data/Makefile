include config.mk

.PHONY: all GW150914_plots GW200129_plots
all: GW150914_plots GW200129_plots

GWTC2p1_DATA_RELEASE_PATH := $(GWTC_DATA_RELEASE_PATH)/GWTC-2.1
GWTC3_DATA_RELEASE_PATH := $(GWTC_DATA_RELEASE_PATH)/GWTC-3

$(GWTC2p1_DATA_RELEASE_PATH):
	cd $(GWTC_DATA_RELEASE_PATH) && $(MAKE)

$(GWTC3_DATA_RELEASE_PATH):
	cd $(GWTC_DATA_RELEASE_PATH) && $(MAKE)

.PHONY: fetch_psds
fetch_psds: $(GWTC2p1_DATA_RELEASE_PATH) $(GWTC3_DATA_RELEASE_PATH)
	python fetch_psd.py --SID GW150914 --data-release-path $(GWTC_DATA_RELEASE_PATH)
	python fetch_psd.py --SID GW200129 --data-release-path $(GWTC_DATA_RELEASE_PATH)


GW150914_plots: $(GWTC2p1_DATA_RELEASE_PATH)
	gw_smc_utils_plot_event \
		--results $(GW150914_RESULT) \
		--labels pocomc \
		--data-release-path $(GWTC_DATA_RELEASE_PATH) \
		--SID GW150914

GW200129_plots: $(GWTC3_DATA_RELEASE_PATH)
	gw_smc_utils_plot_event \
		--results $(GW200129_RESULT) \
		--labels pocomc \
		--data-release-path $(GWTC_DATA_RELEASE_PATH) \
		--SID GW200129
