include config.mk

.PHONY: all GW150914_plots GW200129_plots
all: GW150914_plots GW200129_plots

$(DATA_RELEASE_PATH)/GWTC-2.1:
	zenodo_get $(GWTC2p1_ZENODO_ID) -g "IGWN-GWTC2p1-v2-GW150914_095045_PEDataRelease_mixed_cosmo.h5" -o $(DATA_RELEASE_PATH)/GWTC-2.1 \

$(DATA_RELEASE_PATH)/GWTC-3:
	zenodo_get $(GWTC3_ZENODO_ID) -g "IGWN-GWTC3p0-v1-GW200129_065458_PEDataRelease_mixed_cosmo.h5" -o $(DATA_RELEASE_PATH)/GWTC-3 \


.PHONY: fetch_psds
fetch_psds:
	python fetch_psd.py --SID GW150914 --data-release-path $(DATA_RELEASE_PATH)
	python fetch_psd.py --SID GW200129 --data-release-path $(DATA_RELEASE_PATH)


GW150914_plots: $(DATA_RELEASE_PATH)/GWTC-2.1
	python make_plots.py \
		--results GW150914/outdir_GW150914_pocomc_transforms_no_flow/final_result/pocomc_GW150914_data0_1126259462-391_analysis_H1L1_merge_result.hdf5 \
		--labels pocomc \
		--data-release-path $(DATA_RELEASE_PATH) \
		--SID GW150914

GW200129_plots: $(DATA_RELEASE_PATH)/GWTC-3
	python make_plots.py \
	--results /home/michael.williams/git_repos/gw-smc/experiments/real_data/GW200129/outdir_GW200129_pocomc_transforms_no_flow_settings_phenom_version/final_result/pocomc_GW200129_data0_1264316116-433214_analysis_H1L1V1_merge_result.hdf5 \
	--labels pocomc \
	--SID GW200129
