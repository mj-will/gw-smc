.PHONY: all
all: build

.PHONY: install
install:
	pip install -r requirements.txt
	cd ../ && pip install .

.PHONY: real_event_plots
real_event_plots:
	cd ../plotting && make event_plots_png

.PHONY: build
build: real_event_plots
	bash build.sh

.PHONY: clean
clean:
	rm -rf _build
