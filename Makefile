include common.mk
MODULES=tests

all: lint mypy

lint:
	flake8 $(MODULES) daemons/*/*.py

mypy:
	mypy --ignore-missing-imports $(MODULES)

tests:=$(wildcard tests/test_*.py)

test: $(tests) daemon-import-test
	coverage combine
	rm -f .coverage.*

$(tests): %.py : mypy lint
	coverage run -p --source=dds $*.py

deploy: deploy-daemons

deploy-daemons:
	$(MAKE) -C daemons deploy

gcp-service-account:
	$(MAKE) -C infra COMPONENT=gcp_service_account apply

plan-infra:
	$(MAKE) -C infra plan-all

infra:
	$(MAKE) -C infra apply-all

clean:
	git clean -Xdf daemons $(MODULES)

.PHONY: all lint mypy test deploy deploy-daemons infra
