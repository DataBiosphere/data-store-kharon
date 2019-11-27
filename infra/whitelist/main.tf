locals {
  common_tags = "${map(
    "managedBy" , "terraform",
    "Name"      , "${var.DDS_INFRA_TAG_SERVICE}-whitelist",
    "project"   , "${var.DDS_INFRA_TAG_PROJECT}",
    "env"       , "${var.DDS_DEPLOYMENT_STAGE}",
    "service"   , "${var.DDS_INFRA_TAG_SERVICE}",
    "owner"     , "${var.DDS_INFRA_TAG_OWNER}"
  )}"
}

resource "aws_dynamodb_table" "whitelist" {
  name           = "dds-whitelist-${var.DDS_DEPLOYMENT_STAGE}"
  read_capacity  = 20
  write_capacity = 20
  hash_key       = "key"

  attribute {
    name = "key"
    type = "S"
  }
  tags = "${local.common_tags}"
}
