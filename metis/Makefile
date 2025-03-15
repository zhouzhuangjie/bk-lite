setup:
	virtualenv .venv -p python3.10
	./.venv/bin/pip install pip-tools

release:
	pyarmor gen -O dist -r ./apps
	pyarmor gen -O dist -r ./core
	pyarmor gen -O dist -r ./server.py

install:
	./.venv/bin/pip-compile ./requirements/requirements-core.txt \
							./requirements/requirements-example.txt \
		-v --output-file ./requirements.txt 
	./.venv/bin/pip-sync -v

clean:
	rm -Rf ./dist

compile-example:
	pyarmor gen --platform linux.x86_64 --platform linux.armv7 --platform linux.aarch64 --platform darwin.aarch64 -O dist -r ./server.py
	pyarmor gen --platform linux.armv7 --platform linux.aarch64 --platform darwin.aarch64 -O dist -r ./core
	pyarmor gen --platform linux.armv7 --platform linux.aarch64 --platform darwin.aarch64 -O dist -r ./example

release-example:
	docker build -t metis:example -f ./support-files/release/example/Dockerfile .

test-example:
	docker run -it --rm --name example -p 8001:8001 metis:example
