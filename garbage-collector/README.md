# how to run locally
``` sh
export PYTHONWARNINGS="ignore:Unverified HTTPS request"
docker build -t garbage-collector:1.0 .
docker run -e PYTHONWARNINGS="ignore:Unverified HTTPS request" -e REGISTRY_URL=https://192.168.170.251:30007 REGISTRY_CREDS=YWRtaW46YWRtaW5wYXNzd29yZA== garbage-collector:1.0
```