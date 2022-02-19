# faas-kubernetes-starter

A starter project for FAAS on Kubernetes. This gives you something like AWS Lambda, Dynamo DB and Cognito which you can host on your Kubernetes cluster.

What you will get:

- Fission.io to run your functions
- Postgres as database
- Keycloak for authentication
- Prometheus, Loki and Grafana for monitoring and logging
- Certificates for your HTTPS endpoints

## Requirements

These requirements are needed for both dev and prod installations:

- [kubectl](https://kubernetes.io/releases/download/): Download and add it to your path
- [helm](https://helm.sh/docs/intro/install/): Download https://github.com/helm/helm/releases and add it to your path
- [fission-cli](https://fission.io/docs/installation/#install-fission-cli) and add it to your path

## Steps

For the production steps we use leaf.cloud as example. Why? Because they really on an open technology stack. This way you can find other cloud providers and the steps should be similar.

|               | Dev                                                                             | Prod                           |
| ------------- | ------------------------------------------------------------------------------- | ------------------------------ |
| Get a cluster | [Install minikube](https://kubernetes.io/de/docs/tasks/tools/install-minikube/) | [Use Terraform](/Terraform.md) |

## Expected prices

This example is of course free, but you might want a picture of the hosting costs you can expect. We run this example on production at around 80€ per month on https://www.leaf.cloud. The example needs 4 CPUs, 8 GB RAM and 40 GB disk and a Kube DB Enterprise license (~10 EUR per month). You can use these numbers to compare this with your favorite cloud provider

## FAQ

### Why a script and not a parent Helm chart?

Helm charts don't allow for subcharts to be installed into different namespaces. As we use namespaces to keep utilities such as auth separated from the main application, we've opted for an install script instead.

### Why are there multiple load balancers?

The example only needs on publicly exposed load balancer for the nginx-ingress controller. Your cloud provider might automatically expose any load balancers in your cluster. Those additional load balancers can be removed.

### Database password handling or "Why are there passwords in the git examples?"

You'll find database passwords in this example which are meant only to get started with this example. You'll also note that the production examples don't mention any passwords, and production passwords should never be committed to git.
