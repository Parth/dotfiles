curl http://sdk.cloud.google.com/ | bash
# The next two line updates path for the Google Cloud SDK temporarily so we can run the final two commands
~/google-cloud-sdk/bin/./gcloud auth login
~/google-cloud-sdk/bin/./gcloud components update gae-python
