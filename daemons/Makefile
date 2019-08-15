include ../common.mk

AWS_DAEMONS := \
    dds-delete

deploy: $(AWS_DAEMONS)

$(AWS_DAEMONS):
	./terraform_daemon.sh $@
	./package_daemon.sh $@
	./build_deploy_config.sh $@
	cd $@ && domovoi deploy --stage $(DDS_DEPLOYMENT_STAGE)

.PHONY: deploy $(AWS_DAEMONS)
