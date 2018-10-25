resource "aws_dynamodb_table" "whitelist" {
  name           = "dds-whitelist-${var.DDS_DEPLOYMENT_STAGE}"
  read_capacity  = 20
  write_capacity = 20
  hash_key       = "key"

  attribute {
    name = "key"
    type = "S"
  }
}
