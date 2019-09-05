ROOT_PATH := /home/jlanecki/AGH/python/flatbot
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
		$(ROOT_PATH)/__pycache__ \
		$(PACKAGE_PATH)/__pycache__ \
		$(PACKAGE_PATH)/api/__pycache__ \
		$(PACKAGE_PATH)/bot/__pycache__ \
		$(ROOT_PATH)/tests/__pycache__
