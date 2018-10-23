include ../common.mk

AWS_DAEMONS := \
    dds-delete

deploy: $(AWS_DAEMONS)

$(AWS_DAEMONS):
	@for f in $@/*.tf; do \
		if [ -e $$f ]; then \
			echo "Terraforming $@"; \
			rm -rf $@/.terraform/*.tfstate;\
			./build_tf_deploy_config.py $@;\
			(cd $@ ; terraform init);\
			(cd $@ ; TF_VAR_daemon=$@ terraform apply -auto-approve);\
		fi;\
		break;\
	done
	./package_daemon.sh $@
	./build_deploy_config.sh $@
	cd $@ && domovoi deploy --stage $(DDS_DEPLOYMENT_STAGE)

.PHONY: deploy $(AWS_DAEMONS)
