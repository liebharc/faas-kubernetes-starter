# leav-k8s backend

Leav Kubernetes backend.

## Requirements

- [kubectl](https://kubernetes.io/releases/download/): Download and add it to your path
- [helm](https://helm.sh/docs/intro/install/): Download https://github.com/helm/helm/releases and add it to your path
- [fission-cli](https://fission.io/docs/installation/#install-fission-cli) and add it to your path

## First steps

- `python install.py --updateDependencies`, this starts minikube and installs the Helm chart
- `python fission.py`, this installs all fission components
- Add the following line to the bottom of the `/etc/hosts` (or `C:\Windows\System32\drivers\etc\hosts`) file on your computer (you will need administrator access):
  - `127.0.0.1 local.leav.app`

Additional steps:

- Import dashboards from the `dashboards` directory

TODOs:

- How to deploy helm and fission functions from CI/CD (Github Actions)
- HTTPS proxies (https://kubernetes.io/docs/concepts/services-networking/ingress/)
- Database backup
- Secret management:
  - Set default secrets in the config files (doesn't matter if the leak, they are only used for development)
  - Overwrite all secrets on Github
  - Have a backup of the secrets available to C-level
  - Eventuell: https://www.keepersecurity.com/de_DE/integrations.html
- Access management:
  - Record every access, especially if it wasn't by the owning user
- Helm SQL storage backend to avoid that we run into the 1 MB storage limitation of Helm secrets: https://helm.sh/docs/topics/advanced/

## Cheat sheet

- Take a lok at `install.py` and `diagnose.py`. The scripts contain lessons learned from our early Kubernetes days in script form.

## Helm charts repos

- `helm repo add bitnami https://charts.bitnami.com/bitnami`
- `helm repo add fission-charts https://fission.github.io/fission-charts`
- `helm repo add grafana https://grafana.github.io/helm-charts`
- `helm repo add ory https://k8s.ory.sh/helm/charts`

## Resources

- [Find Helm Charts](https://artifacthub.io/)
- https://docs.bitnami.com/tutorials/create-your-first-helm-chart/
- https://phoenixnap.com/kb/postgresql-kubernetes
- https://fission.io/blog/how-to-use-postgresql-database-with-fission-functions/
- https://github.com/up-time/flyway-k8-helm-migrations/blob/master/helm/templates/deployment.yaml
- https://fission.io/blog/setting-ingress-for-your-functions/
- [Kubernetes Tutorial for Beginners by TechWorld with Nana](https://www.youtube.com/watch?v=X48VuDVv0do)
- Logs:
  - https://fission.io/docs/usage/observability/loki/
  - https://grafana.com/docs/loki/latest/installation/helm/
  - https://promcat.io/apps/postgresql
- https://itnext.io/manage-auto-generated-secrets-in-your-helm-charts-5aee48ba6918
- https://www.cloudsavvyit.com/14069/how-to-install-kubernetes-cert-manager-and-configure-lets-encrypt/
- https://getbetterdevops.io/k8s-ingress-with-letsencrypt/

## Hosters

- https://www.hetzner.com/de/cloud
- https://upcloud.com/about/
- https://cloud.ionos.com/
- https://www.leaf.cloud/
- https://www.syseleven.de/ueber-uns/#gruenefakten

## Terraform

- `terraform init`
- `terraform apply`
