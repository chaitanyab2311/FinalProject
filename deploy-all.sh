kubectl apply -f cassandra/cassandra-deployment.yaml
kubectl apply -f cassandra/cassandra-service.yaml

kubectl apply -f rabbitmq/rabbitmq-deployment.yaml
kubectl apply -f rabbitmq/rabbitmq-service.yaml

kubectl apply -f logs/logs-deployment.yaml

kubectl apply -f rest/rest-service.yaml
kubectl apply -f rest/rest-deployment.yaml

kubectl apply -f worker/worker-deployment.yaml


