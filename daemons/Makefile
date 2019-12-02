include ../common.mk

AWS_DAEMONS := \
    dds-delete

deploy: $(AWS_DAEMONS)

generate-dependencies:
	${DDS_HOME}/scripts/generate_upload_requirements_layer.sh

$(AWS_DAEMONS): generate-dependencies
	./terraform_daemon.sh $@
	./package_daemon.sh $@
	./build_deploy_config.sh $@
	cd $@ && domovoi deploy --stage $(DDS_DEPLOYMENT_STAGE)
	@if [[ $@ == "dds-delete" ]]; then \
        ./invoke_lambda.sh $@ $(DDS_DEPLOYMENT_STAGE) \
        ../tests/daemons/sample_sqs_event.json.template; \
    fi

.PHONY: deploy $(AWS_DAEMONS)
