# faas-kubernetes-starter

Build status (main): [![CI](https://github.com/liebharc/faas-kubernetes-starter/workflows/CI/badge.svg?branch=main)](https://github.com/liebharc/faas-kubernetes-starter/actions)

A starter project for FAAS (Functions As A Service or Serverless) on Kubernetes. This gives you something like AWS Lambda, Dynamo DB and Cognito which you can host on your Kubernetes cluster. The examples will use functions written in Typescript, but you should be able to use any of the [environments supported by Fission.io](https://environments.fission.io/)

What you will get:

- [Fission.io](https://fission.io/) to run your functions
- [Postgres](https://www.postgresql.org/) as database
- [Keycloak](https://www.keycloak.org/) for authentication
- [Prometheus, Loki and Grafana](https://grafana.com/docs/loki/latest/) for monitoring and logging
- [Certificates](https://letsencrypt.org/) for your HTTPS endpoints

## Requirements

These requirements are needed for both dev and prod installations:

- [node & npm](https://docs.npmjs.com/cli/v7/configuring-npm/install)
- [kubectl](https://kubernetes.io/releases/download/): Download and add it to your path
- [helm](https://helm.sh/docs/intro/install/): Download https://github.com/helm/helm/releases and add it to your path
- [fission-cli](https://fission.io/docs/installation/#install-fission-cli) and add it to your path

## Steps

For the production steps we use leaf.cloud as example. Why? Because they really on an open technology stack. This way you can find other cloud providers and the steps should be similar.

|                     | Dev                                                                             | Prod                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| ------------------- | ------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Build functions     | `npm run build`                                                                 | `npm run build`                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| Get a cluster       | [Install minikube](https://kubernetes.io/de/docs/tasks/tools/install-minikube/) | [Use Terraform](/Terraform.md)                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| Install Helm charts | Run `scripts/cinstall.py full --updateDependencies`                             | - Run `scripts/cinstall.py ingress db --prod --domain YOUR_DOMAIN`<br/>- Use `pgadmin` to create users (this steps hasn't been automated yet). Take a look at the `V1_0_0__create_users.sql` file to see how users have to be created. And make sure to pick different passwords! <br/>- Run `scripts/cinstall.py cert monitoring auth fission functions --prod --domain YOUR_DOMAIN --raven.db.password=PASSWORD --keycloak.db.pw=PASSWORD --updateDependencies` |

What the install script does for you:

|                                    | Dev                                                            | Prod                                                              |
| ---------------------------------- | -------------------------------------------------------------- | ----------------------------------------------------------------- |
| ingress-controller                 | Installs the minikube ingress plugin                           | Installs the `ingress-nginx` chart                                |
| Database                           | Installs a Postgres helm chart, don't use this for production  | Installs the Kube DB operator and a Postgres database             |
| Cert Manager                       | Installs a cert manager and let's encrypt staging certificates | Installs a cert manager and let's encrypt production certificates |
| Monitoring                         | Same as for prod                                               | Installs Prometheus, Loki and Grafana                             |
| Auth                               | Same as for prod                                               | Installs Keycloak                                                 |
| Framework for Serverless Functions | Same as for prod                                               | Installs Fission                                                  |
| Functions                          | Same as for prod                                               | Creates your fission functions and routes                         |

## Fission handler names

We have encoded some information into the names of the fission handlers: `crud-v1-hello-world.ts`:

- `crud`: Specifies which operations are allowed
  - `create`: HTTP post and put
  - `read`: HTTP get
  - `update`: HTTP patch
  - `delete`: HTTP delete
- The remaining path becomes the functions URL, "-" are replaces with "/"

So `crud-v1-hello-world.ts` becomes `/v1/hello/world` and it will be called with `POST`, `PUT`, `GET`, `PATCH` and `DELETE`.

## Expected prices

This example is of course free, but you might want a picture of the hosting costs you can expect. We run this example on production at around 80€ per month on https://www.leaf.cloud. The example needs 4 CPUs, 8 GB RAM and 40 GB disk and a Kube DB Enterprise license (~10 EUR per month). You can use these numbers to compare this with your favorite cloud provider

## FAQ

### Why a script and not a parent Helm chart?

Helm charts don't allow for subcharts to be installed into different namespaces. As we use namespaces to keep utilities such as auth separated from the main application, we've opted for an install script instead.

### Why are there multiple load balancers?

The example only needs on publicly exposed load balancer for the nginx-ingress controller. Your cloud provider might automatically expose any load balancers in your cluster. Those additional load balancers can be removed.

### Database password handling or "Why are there passwords in the git examples?"

You'll find database passwords in this example which are meant only to get started with this example. You'll also note that the production examples don't mention any passwords, and production passwords should never be committed to git.

### Can I do incremental changes to my infrastructure with this?

This project is based on a couple of helm charts. If you need to update an existing deployment - especially when it's the production deployment - then please get familiar with the helm charts. This is beyond the scope of the `cinstall.py` script as well.

### How to add functions?

Add files to `k8s/services`, take also a look at the existing file as example and check the FAQ entry for function naming. Run `cinstall.py functions` to install the functions.

### Why does this look like it was originally part of a larger project?

This template has been created out of `leav.app`, which consists of multiple parts. The Kubernetes backend is only a part of it, but it's a part we wanted to share.

## Open points

### Log Storage

Loki and Prometheus have no storage configured at the moment. If you can't afford loosing any log files, then you might want to fix this immediately. PRs are welcome :).
