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
		-subj "/CN=192.168.100.106" \
		-reqexts v3_ca \
		-config $(ROOT_PATH)/ssl/openssl.cnf
	@openssl dhparam \
		-out $(ROOT_PATH)/ssl/dhparam.pem \
		2048	

# Local development #

.PHONY: test-db
test-db:
	@ROOT_PATH=$(ROOT_PATH) bash scripts/db/run_test_db.sh
	@sleep 2
	@(export CONFIG_PATH=$(TEST_CONFIG_PATH); \
		python scripts/db/setup_db.py && \
		python scripts/db/add_user.py user password)

.PHONY: clean
clean:
	@rm -rf \
		`find $(ROOT_PATH) -name '__pycache__'`	\
		$(PACKAGE_PATH).egg-info
	@docker stop pg-test


# Docker #
.PHONY: docker-add-user
docker-add-user:
	@docker-compose exec server /flatbot/scripts/add_user.py kuba haslo

.PHONY: docker-run
docker-run:
	@docker-compose up .
