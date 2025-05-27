include config.mk

.PHONY: submit_all
submit_all : 
	bash submit_all.sh

outdir%/final_result/corner.png: outdir%/final_result/*.hdf5 plot_single_result.py
	bash produce_corner_plot.sh $<


RESULT_FILES := $(wildcard outdir*/final_result/*.hdf5)
CORNER_PLOTS := $(addsuffix corner.png, $(dir $(RESULT_FILES)))

.PHONY: corner_plots
corner_plots: $(CORNER_PLOTS)


.PHONY: compute_jsd
compute_jsd:
	python compute_js.py --outdir $(BNS_JSD_PATH) --samplers dynesty pocomc --n-pool 4 --prefix outdir


bns_results_summary.hdf5:
	python produce_summary.py --filename $(BNS_SUMMARY_FILE)
