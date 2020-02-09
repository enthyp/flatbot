ROOT_PATH := $(shell pwd)
PACKAGE_PATH := $(ROOT_PATH)/src/flatbot

.PHONY: cert
cert:
	@openssl req -x509 \
		-newkey rsa:2048 \
		-keyout $(ROOT_PATH)/ssl/private.pem \
		-out $(ROOT_PATH)/ssl/cert.pem \
		-days 90 \
		-nodes \
		-subj '/CN=192.168.100.106' \
		-reqexts v3_ca \
		-config $(ROOT_PATH)/ssl/openssl.cnf
	@openssl dhparam \
		-out $(ROOT_PATH)/ssl/dhparam.pem \
		2048	

.PHONY: clean
clean: 
	@rm -rf \
		`find $(ROOT_PATH) -name '__pycache__'`	\
		$(PACKAGE_PATH).egg-info

# Local development #

.PHONY: local-db
local-db:
	@docker run --rm \
	  --name pg \
	  -e POSTGRES_USER=postgres \
	  -e POSTGRES_PASSWORD=postgres \
	  -e POSTGRES_DB=db \
	  --network host \
	  -v $(ROOT_PATH)/data/pgdata:/var/lib/postgresql/data \
	  postgres

# Docker #

.PHONY: docker-build
docker-build:
	docker build -t flatbot:latest .

.PHONY: docker-run
docker-run:
	docker run --rm \
		--name fb \
		--network host \
		flatbot:latest
