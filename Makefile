include common.mk
MODULES=tests

all: lint mypy

lint:
	flake8 $(MODULES) daemons/*/*.py

mypy:
	mypy --ignore-missing-imports $(MODULES)

tests:=$(wildcard tests/test_*.py)

test: $(tests)
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

refresh_all_requirements:
	@echo -n '' >| requirements.txt
	@if [ $$(uname -s) == "Darwin" ]; then sleep 1; fi  # this is require because Darwin HFS+ only has second-resolution for timestamps.
	@touch requirements.txt.in
	@$(MAKE) requirements.txt

requirements.txt: %.txt : %.txt.in
	[ ! -e .requirements-env ] || exit 1
	virtualenv -p $(shell which python3) .$<-env
	.$<-env/bin/pip install -r $@
	.$<-env/bin/pip install -r $<
	echo "# You should not edit this file directly.  Instead, you should edit $<." >| $@
	.$<-env/bin/pip freeze >> $@
	rm -rf .$<-env
#	scripts/find_missing_wheels.py requirements.txt # Disabled by akislyuk (circular dependency issues)

clean:
	git clean -Xdf daemons $(MODULES)

.PHONY: all lint mypy test deploy deploy-daemons infra refresh_all_requirements, requirements.txt
