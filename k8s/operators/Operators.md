## Create Postgres Operator and Cluster

-   https://kubedb.com/docs/v2021.12.21/setup/install/enterprise/
    -   `helm install kubedb appscode/kubedb --version v2021.12.21 --namespace kubedb --create-namespace --set kubedb-enterprise.enabled=true --set kubedb-autoscaler.enabled=true --set-file global.license=kubedb-enterprise-license-0a9c119d-59d7-4db1-8e71-902f56c873b8.txt`
-   https://kubedb.com/docs/v2021.12.21/guides/postgres/:
    -   `kubectl create ns db`
    -   `kubectl create -f kubedb/pgadmin.yaml`
    -   `kubectl create -f kubedb/postgres.yaml`
