.PHONY: all
all: build

.PHONY: install
install:
	pip install -r requirements.txt
	cd ../ && pip install .

.PHONY: build
build:
	bash build.sh

.PHONY: clean
clean:
	rm -rf _build
