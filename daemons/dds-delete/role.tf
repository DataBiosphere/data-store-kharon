data "aws_iam_policy_document" "dds_delete_policy" {
  statement {
    actions = [
      "s3:AbortMultipartUpload",
      "s3:Delete*",
      "s3:Get*",
      "s3:List*"
    ]
    resources = [
      "arn:aws:s3:::${var.DSS_S3_BUCKET}/*",
    ]
  }
  statement {
    actions = [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes"
    ]
    resources = [
      "*"
    ]
  }
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = [
      "arn:aws:logs:*:${var.account_id}:log-group:/aws/lambda/dds-delete-${var.DDS_DEPLOYMENT_STAGE}"
    ]
  }
  statement {
    actions = [
      "es:ESHttpDelete",
      "es:ESHttpGet",
      "es:ESHttpHead",
      "es:ESHttpPost",
      "es:ESHttpPut"
    ]
    resources = [
      "arn:aws:es:*:${var.account_id}:domain/dss-index-${var.DDS_DEPLOYMENT_STAGE}/*",
    ]
  }
  statement {
    actions = [
      "dynamodb:*"
    ]
    resources = [
      "arn:aws:dynamodb:*:${var.account_id}:table/dds-whitelist-${var.DDS_DEPLOYMENT_STAGE}"
    ]
  }
}

data "aws_iam_policy_document" "dds_delete_role_assumption" {
  statement {
    actions = [
      "sts:AssumeRole"
    ]
    principals = {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "dds_delete" {
  name   = "dds-delete-${var.DDS_DEPLOYMENT_STAGE}"
  assume_role_policy = "${data.aws_iam_policy_document.dds_delete_role_assumption.json}"
}

resource "aws_iam_role_policy" "dds_delete" {
  name   = "dds-delete-${var.DDS_DEPLOYMENT_STAGE}"
  role   = "${aws_iam_role.dds_delete.id}"
  policy = "${data.aws_iam_policy_document.dds_delete_policy.json}"
}

output "role-arn" {
  value = "${aws_iam_role.dds_delete.arn}"
}
