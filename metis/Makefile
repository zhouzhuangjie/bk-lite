# Configuration
VENV := ./.venv
PIP := $(VENV)/bin/pip
PIP_COMPILE := $(VENV)/bin/pip-compile
PIP_SYNC := $(VENV)/bin/pip-sync
PYARMOR := pyarmor
DIST_DIR := dist
RUNTIME_DIR := runtime

# Supported platforms for runtime
PLATFORMS := linux.x86_64 linux.armv7 linux.aarch64 darwin.aarch64

.PHONY: setup clean install-% compile-% release-% test-%

# Development environment setup
setup:
	virtualenv $(VENV) -p python3.12
	$(PIP) install pip-tools

# Cleanup
clean:
	rm -Rf ./$(DIST_DIR)

# Package installation targets
install-%: ./requirements/requirements-%.txt
	$(PIP_COMPILE) ./requirements/requirements-core.txt \
				   ./requirements/requirements-$*.txt \
		-v --output-file ./requirements.txt
	$(PIP_SYNC) -v

# Runtime generation
gen-runtime:
	$(PYARMOR) gen runtime $(foreach platform,$(PLATFORMS),--platform $(platform)) -O $(RUNTIME_DIR)

# Compilation targets
compile-%: clean
	$(PYARMOR) gen --use-runtime $(RUNTIME_DIR) -O $(DIST_DIR) -r ./server.py
	$(PYARMOR) gen --use-runtime $(RUNTIME_DIR) -O $(DIST_DIR) -r ./core
	$(PYARMOR) gen --use-runtime $(RUNTIME_DIR) -O $(DIST_DIR) -r ./apps
	find ./$(DIST_DIR)/apps -mindepth 1 -maxdepth 1 -type d -not -name '$*' -exec rm -rf {} +
	cp -Rf ./$(RUNTIME_DIR)/* ./$(DIST_DIR)

# Release targets
release:
	$(PYARMOR) gen -O $(DIST_DIR) -r ./apps
	$(PYARMOR) gen -O $(DIST_DIR) -r ./core
	$(PYARMOR) gen -O $(DIST_DIR) -r ./server.py

release-%:
	docker build -t $(or $(DOCKER_REGISTRY)/metis:$*,metis:$*) -f ./support-files/release/$*/Dockerfile .

# Test targets
test-%:
	docker run -it --rm --name $* -p 8001:8001 metis:$*