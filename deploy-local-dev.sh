kubectl apply -f cassandra/cassandra-deployment.yaml
kubectl apply -f cassandra/cassandra-service.yaml

kubectl apply -f rabbitmq/rabbitmq-deployment.yaml
kubectl apply -f rabbitmq/rabbitmq-service.yaml

kubectl port-forward --address 0.0.0.0 service/cassandra 9042:9042
kubectl port-forward --address 0.0.0.0 service/rabbitmq 5672:5672 