VENV := ./.venv
PIP := $(VENV)/bin/pip
PIP_COMPILE := $(VENV)/bin/pip-compile
PIP_SYNC := $(VENV)/bin/pip-sync
PLATFORMS := linux.x86_64 linux.armv7 linux.aarch64 darwin.aarch64

.PHONY: setup clean install-% compile-% release-% test-%
setup:
	virtualenv $(VENV) -p python3.12
	$(PIP) install pip-tools

install-%:
	$(PIP_COMPILE) ./requirements/requirements-core.txt \
				   ./requirements/requirements-$*.txt \
		-v --output-file ./requirements.txt
	$(PIP_SYNC) -v
