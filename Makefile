push:
	git add . && codegpt commit . && git push

start-dev-env:
	docker network create bk-lite || true 
	cd ./support-files/docker-compose && \
	docker-compose -f ./docker-compose.dev.yml up -d 

stop-dev-env:
	cd ./support-files/docker-compose && \
	docker-compose -f ./docker-compose.dev.yml down