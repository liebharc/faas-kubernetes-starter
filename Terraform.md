# Creating a cluster using terraform

At the example of leaf.cloud

- [Install terraform](https://www.terraform.io/downloads)
- Create an account on your cloud provider
- Create [key pairs](https://docs.leaf.cloud/en/latest/Getting-Started/Key-pairs/) and add them to your keyring
- In this repo: `cd backend/terraform` && `terraform init` && `terraform apply`
- When successful, it should put a (rke2).yaml file with the credentials into the current working directory. Move this file to `~/config` and `export KUBECONFIG=~/config` to have kubectl use this config file.
- Run `kubectl get nodes` to see the nodes in your cluster
- Create a S3 object storage bucket called `cockatoobackup`

🎆 You now should have a cloud in the cloud which you can use for the next steps 🎇.

More resources:

- [Leav HQ Terraform examples](https://github.com/leafcloudhq/terraform-examples/tree/main/kubernetes-rke2)
- [S3 Object Storage Setup](https://docs.leaf.cloud/en/latest/object-storage/using-object-storage/)
