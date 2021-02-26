# Requirements
- openssl
- docker
- minikube
- kubectl
- some local storage for redis and registry

# Create dirs
``` sh
mkdir auth storage redis-storage certs
```

# Generate example user pass
``` sh
docker run \
--entrypoint htpasswd \
registry:2.7.0 \
-Bbn admin adminpassword >> auth/htpasswd

docker run \
--entrypoint htpasswd \
registry:2.7.0 \
-Bbn anotheruser anotherpassword >> auth/htpasswd
```

# Generate self-signed certs
``` sh
openssl req -newkey rsa:4096 \
    -x509 \
    -sha256 \
    -days 3650 \
    -nodes \
    -out certs/tls.crt \
    -keyout certs/tls.key \
    -subj '/CN=registry-service.pelago.svc.cluster.local:5000'
```

# Deploy redis, registry and cronjob garbage-collector in k8s
``` sh
kubectl create ns pelago
kubectl -n pelago apply -f redis
kubectl -n pelago apply -f registry
```

## Registry is accessible in node port 30007, in my case localhost:30007
## Test the registry
``` sh
docker pull nginx
docker tag nginx localhost:30007/nginx:latest
docker tag nginx localhost:30007/nginx:1.0
docker login localhost:30007 -u admin -p adminpassword
docker push localhost:30007/nginx:latest
docker push localhost:30007/nginx:1.0
docker rmi localhost:30007/nginx:latest localhost:30007/nginx:1.0
docker run -d --name test-nginx -p 80:80 localhost:30007/nginx:latest
curl localhost

# test data persistence, delete the registry objects
kubectl -n pelago delete -f registry
docker rm -f test-nginx
docker rmi localhost:30007/nginx:latest
# re-deploy and test
kubectl -n pelago apply -f registry
docker run -d --name test-nginx -p 80:80 localhost:30007/nginx:latest
curl localhost
```

# Deploy cronjob for python-garbage-collector
``` sh
cd garbage-collector
docker build -t localhost:30007/python-garbage-collector:1.0 .
docker push localhost:30007/python-garbage-collector:1.0
kubectl -n pelago apply -f k8s
```

# TODO
- python script line 47, to sort tags by latest created, not yet available in registry API at time of writing
