data "google_project" "project" {}

resource "google_service_account" "dds" {
  display_name = "${var.DDS_GCP_SERVICE_ACCOUNT_NAME}-${var.DDS_DEPLOYMENT_STAGE}"
  account_id = "${var.DDS_GCP_SERVICE_ACCOUNT_NAME}-${var.DDS_DEPLOYMENT_STAGE}"
}

# Useful command to discover role names (Guessing based on console titles is difficult):
# `gcloud iam list-grantable-roles //cloudresourcemanager.googleapis.com/projects/{project-id}`

resource "google_project_iam_member" "storageobjectadmin" {
  project = "${data.google_project.project.project_id}"
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.dds.email}"
}

resource "google_project_iam_member" "viewer" {
  project = "${data.google_project.project.project_id}"
  role    = "roles/viewer"
  member  = "serviceAccount:${google_service_account.dds.email}"
}
