# Overview

This project propose different endpoint to test and understand how to secure the Google Chat webhook security while 
the Cloud Run instance is deployed publicly. *Cloud Run is my preferred platform, but you can reuse this principle 
on any endpoint, on Google Cloud or not*

This [article](TODO)  
presents is the story which use this code base to enlighten the security topic

*This code is for educational purpose. It's inconsistent to have public and private endpoints for Cloud Run in the same
container.*

# General architecture

The container contains 3 endpoints
* `/private` that accepts any request on the service, without any id token (JWT) checks. Recommended to use with a 
private Cloud Run service (no-allow-unauthenticated)
* `/public` that checks the Bearer token in the Authorization header. This token is required and must be valid. In 
addition, it must be signed by Google Chat and must contain, in the audience field of the JWT, the project number
of the Google Cloud Project which has activated the Google Chat API.
* `/log` that logs the headers and the body of any HTTP request received on the endpoint.

# How to use

Build the container and deploy it

```bash
export PROJECT_ID=<your project ID>
export PROJECT_NUMBER=<your project ID>

# Build the container
gcloud builds submit --tag gcr.io/${PROJECT_ID}/google-chat-security

# Deploy it in public mode
gcloud run deploy google-chat-security --image gcr.io/${PROJECT_ID}/google-chat-security \
  --region=us-central1 --platform=managed --allow-unauthenticated --set-env-vars=PROJECT_NUMBER=${PROJECT_NUMBER}

# Deploy it in private mode
gcloud run deploy google-chat-security --image gcr.io/${PROJECT_ID}/google-chat-security \
  --region=us-central1 --platform=managed --no-allow-unauthenticated --set-env-vars=PROJECT_NUMBER=${PROJECT_NUMBER}
```

The list of command is availble in the 
[command.txt](https://github.com/guillaumeblaquiere/google-chat-security/tree/master/command.txt) file

# Licence

This library is licensed under Apache 2.0. Full license text is available in
[LICENSE](https://github.com/guillaumeblaquiere/google-chat-security/tree/master/LICENSE).