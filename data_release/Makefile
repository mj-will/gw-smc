include config.mk

REAL_DATA_PATH=../experiments/real_data/
REAL_DATA_CONFIG=$(REAL_DATA_PATH)/config.mk
include $(REAL_DATA_CONFIG)

SIMULATED_DATA_PATH=../experiments/simulated_data/
PP_TESTS_PATH=$(SIMULATED_DATA_PATH)/pp_tests/
PP_TEST_CONFIG=$(PP_TESTS_PATH)/config.mk
include $(PP_TEST_CONFIG)

COPY_CMD=ln -s

GW150914_REAL_PATH=$(realpath $(REAL_DATA_PATH)/$(GW150914_RESULT))
GW200129_REAL_PATH=$(realpath $(REAL_DATA_PATH)/$(GW200129_RESULT))
GW150914_STATE_FILE_REAL_PATH=$(realpath $(REAL_DATA_PATH)/$(GW150914_STATE_FILE))

PP_TEST_JSD_2DET_FULL_PATH=$(realpath $(PP_TESTS_PATH)/$(PP_TEST_JSD_RESULT_2DET))
PP_TEST_JSD_3DET_FULL_PATH=$(realpath $(PP_TESTS_PATH)/$(PP_TEST_JSD_RESULT_3DET))

PP_TEST_INJECTION_FILE_FULL_PATH=$(realpath $(PP_TESTS_PATH)/$(PP_TEST_INJECTION_FILE))
PP_TEST_INJECTION_DATA_PATH_FULL_PATH=$(realpath $(PP_TESTS_PATH)/$(PP_TEST_INJECTION_DATA_PATH))

PP_TEST_SUMMARY_FILE_REAL_PATH=$(realpath $(PP_TESTS_PATH)/$(PP_TEST_SUMMARY_FILE))

DYNESTY_2DET_CREDIBLE_LEVELS_FILE_REAL_PATH=$(realpath $(PP_TESTS_PATH)/$(DYNESTY_2DET_CREDIBLE_LEVELS_FILE))
DYNESTY_3DET_CREDIBLE_LEVELS_FILE_REAL_PATH=$(realpath $(PP_TESTS_PATH)/$(DYNESTY_3DET_CREDIBLE_LEVELS_FILE))
POCOMC_2DET_CREDIBLE_LEVELS_FILE_REAL_PATH=$(realpath $(PP_TESTS_PATH)/$(POCOMC_2DET_CREDIBLE_LEVELS_FILE))
POCOMC_3DET_CREDIBLE_LEVELS_FILE_REAL_PATH=$(realpath $(PP_TESTS_PATH)/$(POCOMC_3DET_CREDIBLE_LEVELS_FILE))

BNS_PATH=$(SIMULATED_DATA_PATH)/bns/
BNS_CONFIG=$(BNS_PATH)/config.mk
include $(BNS_CONFIG)

BNS_SUMMARY_FILE_REAL_PATH=$(realpath $(BNS_PATH)/$(BNS_SUMMARY_FILE))
BNS_JSD_RESULTS_FULL_PATH=$(realpath $(BNS_PATH)/$(BNS_JSD_PATH))

RESULTS_RELEASE_PATH=$(RELEASE_PATH)/results

.PHONY: data_release
data_release: real_data pp_tests jsd_results pp_test_injection_file bns_results
	@echo "Data release is complete. The data is available in $(RELEASE_PATH)."

.PHONY: data_release_additional
data_release_additional: bns_additional_results
	@echo "Additional data release is complete. The additional data is available in $(RELEASE_PATH_ADDITIONAL)."

gw_smc_data_release_core.zip: data_release
	@echo "Creating zip file..."
	zip -r $@ $(RELEASE_PATH)

gw_smc_data_release_data.zip: pp_test_injection_data
	@echo "Creating zip file..."
	zip -r $@ $(RELEASE_PATH_DATA)

gw_smc_data_release_additional_results.zip: data_release_additional
	@echo "Creating additional results zip file..."
	zip -r $@ $(RELEASE_PATH_ADDITIONAL)

.PHONY: zip_files
zip_files: gw_smc_data_release_core.zip gw_smc_data_release_data.zip gw_smc_data_release_additional_results.zip

$(RELEASE_PATH)/real_data/GW150914_bilby_result_pocomc.hdf5:
	mkdir -p $(RELEASE_PATH)/real_data
	$(COPY_CMD) "$(GW150914_REAL_PATH)" "$@"

$(RELEASE_PATH)/real_data/GW200129_bilby_result_pocomc.hdf5:
	mkdir -p $(RELEASE_PATH)/real_data
	$(COPY_CMD) "$(GW200129_REAL_PATH)" "$@"

$(RELEASE_PATH)/real_data/GW150914_pocomc_final_state.state:
	mkdir -p $(RELEASE_PATH)/real_data
	$(COPY_CMD) "$(GW150914_STATE_FILE_REAL_PATH)" "$@"

.PHONY: real_data
real_data: $(RELEASE_PATH)/real_data/GW150914_bilby_result_pocomc.hdf5 $(RELEASE_PATH)/real_data/GW200129_bilby_result_pocomc.hdf5 $(RELEASE_PATH)/real_data/GW150914_pocomc_final_state.state

$(RELEASE_PATH)/simulated_data/pp_tests/credible_levels/pp_test_credible_levels_pocomc_2det.hdf5:
	mkdir -p $(RELEASE_PATH)/simulated_data/pp_tests/credible_levels
	$(COPY_CMD) "$(POCOMC_2DET_CREDIBLE_LEVELS_FILE_REAL_PATH)" "$@"

$(RELEASE_PATH)/simulated_data/pp_tests/credible_levels/pp_test_credible_levels_pocomc_3det.hdf5:
	mkdir -p $(RELEASE_PATH)/simulated_data/pp_tests/credible_levels
	$(COPY_CMD) "$(POCOMC_3DET_CREDIBLE_LEVELS_FILE_REAL_PATH)" "$@"

$(RELEASE_PATH)/simulated_data/pp_tests/credible_levels/pp_test_credible_levels_dynesty_2det.hdf5:
	mkdir -p $(RELEASE_PATH)/simulated_data/pp_tests/credible_levels
	$(COPY_CMD) "$(DYNESTY_2DET_CREDIBLE_LEVELS_FILE_REAL_PATH)" "$@"

$(RELEASE_PATH)/simulated_data/pp_tests/credible_levels/pp_test_credible_levels_dynesty_3det.hdf5:
	mkdir -p $(RELEASE_PATH)/simulated_data/pp_tests/credible_levels
	$(COPY_CMD) "$(DYNESTY_3DET_CREDIBLE_LEVELS_FILE_REAL_PATH)" "$@"


.PHONY: pp_test_credible_levels
pp_test_credible_levels: \
	$(RELEASE_PATH)/simulated_data/pp_tests/credible_levels/pp_test_credible_levels_pocomc_2det.hdf5 \
	$(RELEASE_PATH)/simulated_data/pp_tests/credible_levels/pp_test_credible_levels_pocomc_3det.hdf5 \
	$(RELEASE_PATH)/simulated_data/pp_tests/credible_levels/pp_test_credible_levels_dynesty_2det.hdf5 \
	$(RELEASE_PATH)/simulated_data/pp_tests/credible_levels/pp_test_credible_levels_dynesty_3det.hdf5

$(RELEASE_PATH_ADDITIONAL)/simulated_data/pp_tests/pp_test_dynesty_2det:
	python fetch_and_rename_pp_test_results.py \
		--input-dir $(PP_TESTS_PATH)/$(DYNESTY_PATH_2DET) \
		--output-dir $@ \
		--label bilby_result_pp_test_dynesty_2det

$(RELEASE_PATH_ADDITIONAL)/simulated_data/pp_tests/pp_test_dynesty_3det:
	python fetch_and_rename_pp_test_results.py \
		--input-dir $(PP_TESTS_PATH)/$(DYNESTY_PATH_3DET) \
		--output-dir $@ \
		--label bilby_result_pp_test_dynesty_3det

$(RELEASE_PATH_ADDITIONAL)/simulated_data/pp_tests/pp_test_pocomc_2det:
	python fetch_and_rename_pp_test_results.py \
		--input-dir $(PP_TESTS_PATH)/$(POCOCMC_PATH_2DET) \
		--output-dir $@ \
		--label bilby_result_pp_test_pocomc_2det

$(RELEASE_PATH_ADDITIONAL)/simulated_data/pp_tests/pp_test_pocomc_3det:
	python fetch_and_rename_pp_test_results.py \
		--input-dir $(PP_TESTS_PATH)/$(POCOCMC_PATH_3DET) \
		--output-dir $@ \
		--label bilby_result_pp_test_pocomc_3det

.PHONY: pp_tests
pp_tests: $(RELEASE_PATH_ADDITIONAL)/simulated_data/pp_tests/pp_test_dynesty_2det \
		$(RELEASE_PATH_ADDITIONAL)/simulated_data/pp_tests/pp_test_dynesty_3det \
		$(RELEASE_PATH_ADDITIONAL)/simulated_data/pp_tests/pp_test_pocomc_2det \
		$(RELEASE_PATH_ADDITIONAL)/simulated_data/pp_tests/pp_test_pocomc_3det

$(RELEASE_PATH)/simulated_data/pp_tests/$(PP_TEST_SUMMARY_FILE):
	mkdir -p $(RELEASE_PATH)/simulated_data/pp_tests
	$(COPY_CMD) "$(PP_TEST_SUMMARY_FILE_REAL_PATH)" "$@"

$(RELEASE_PATH)/simulated_data/pp_tests/jsd_results/2det:
	mkdir -p $(RELEASE_PATH)/simulated_data/pp_tests/jsd_results
	$(COPY_CMD) "$(PP_TEST_JSD_2DET_FULL_PATH)" "$@"

$(RELEASE_PATH)/simulated_data/pp_tests/jsd_results/3det:
	mkdir -p $(RELEASE_PATH)/simulated_data/pp_tests/jsd_results
	$(COPY_CMD) "$(PP_TEST_JSD_3DET_FULL_PATH)" "$@"

.PHONY: jsd_results
jsd_results: $(RELEASE_PATH)/simulated_data/pp_tests/jsd_results/2det $(RELEASE_PATH)/simulated_data/pp_tests/jsd_results/3det


$(RELEASE_PATH)/simulated_data/bns_results/$(BNS_SUMMARY_FILE):
	mkdir -p $(RELEASE_PATH)/simulated_data/bns_results
	$(COPY_CMD) $(BNS_SUMMARY_FILE_REAL_PATH) "$@"

$(RELEASE_PATH)/simulated_data/bns_results/jsd_results:
	mkdir -p $(RELEASE_PATH)/simulated_data/bns_results
	$(COPY_CMD) "$(BNS_JSD_RESULTS_FULL_PATH)" "$@"

.PHONY: bns_results
bns_results: $(RELEASE_PATH)/simulated_data/bns_results/$(BNS_SUMMARY_FILE) $(RELEASE_PATH)/simulated_data/bns_results/jsd_results

$(RELEASE_PATH_ADDITIONAL)/simulated_data/bns_results/:
	mkdir -p $(RELEASE_PATH_ADDITIONAL)/simulated_data/bns_results
	python fetch_and_rename_bns_results.py \
		--input-dir $(BNS_PATH)/ \
		--output-dir $(RELEASE_PATH_ADDITIONAL)/simulated_data/bns_results \
		--prefix outdir \
		--label bilby_result_bns_analysis \
		--verbose

.PHONY: bns_additional_results
bns_additional_results: $(RELEASE_PATH_ADDITIONAL)/simulated_data/bns_results/

bns_results.zip: bns_results
	@echo "Creating BNS results zip file..."
	zip -r $@ $(RELEASE_PATH)/simulated_data/bns_results

bns_additional_results.zip: bns_additional_results
	@echo "Creating additional BNS results zip file..."
	zip -r $@ $(RELEASE_PATH_ADDITIONAL)/simulated_data/bns_results

$(RELEASE_PATH)/pp_test_injection_file.hdf5:
	mkdir -p $(RELEASE_PATH)
	@echo $(PP_TEST_INJECTION_FILE_FULL_PATH)
	$(COPY_CMD) "$(PP_TEST_INJECTION_FILE_FULL_PATH)" "$@"

$(RELEASE_PATH_DATA)/pp_test_injection_data:
	mkdir -p $(RELEASE_PATH_DATA)
	$(COPY_CMD) "$(PP_TEST_INJECTION_DATA_PATH_FULL_PATH)" "$@"

.PHONY: pp_test_injection_data
pp_test_injection_data: $(RELEASE_PATH_DATA)/pp_test_injection_data

.PHONY: pp_test_injection_file
pp_test_injection_file: $(RELEASE_PATH)/pp_test_injection_file.hdf5

.PHONY: clean
clean:
	rm -rf $(RELEASE_PATH) $(RELEASE_PATH_DATA) $(RELEASE_PATH_ADDITIONAL)
	rm -f gw_smc_data_release_*.zip
