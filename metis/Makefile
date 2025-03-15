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

gen-runtime:
	pyarmor gen runtime --platform linux.x86_64 --platform linux.armv7 --platform linux.aarch64 --platform darwin.aarch64  -O runtime

compile-example:
	rm -Rf ./dist
	pyarmor gen --use-runtime runtime -O dist -r ./server.py
	pyarmor gen --use-runtime runtime -O dist -r ./core
	pyarmor gen --use-runtime runtime -O dist -r ./apps
	find ./dist/apps -mindepth 1 -maxdepth 1 -type d -not -name 'example' -exec rm -rf {} +
	cp -Rf ./runtime/* ./dist

release-example:
	docker build -t metis:example -f ./support-files/release/example/Dockerfile .

test-example:
	docker run -it --rm --name example -p 8001:8001 metis:example
