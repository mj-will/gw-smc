.PHONY: all GW150914_plots GW200129_plots

all: GW150914_plots GW200129_plots

GW150914_plots:
	python make_plots.py \
		--results GW150914/outdir_GW150914_pocomc_transforms_no_flow/final_result/pocomc_GW150914_data0_1126259462-391_analysis_H1L1_merge_result.hdf5 \
		--labels pocomc \
		--SID GW150914

GW200129_plots:
	python make_plots.py \
	--results /home/michael.williams/git_repos/gw-smc/experiments/real_data/GW200129/outdir_GW200129_pocomc_transforms_no_flow_settings_phenom_version/final_result/pocomc_GW200129_data0_1264316116-433214_analysis_H1L1V1_merge_result.hdf5 \
	--labels pocomc \
	--SID GW200129
