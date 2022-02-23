

data "openstack_networking_subnet_v2" "public_subnet" {
  name = "external"
}

module "controlplane" {
  source           = "remche/rke2/openstack"
  cluster_name     = "cockatoo-cluster"
  write_kubeconfig = true
  image_name       = "Ubuntu-20.04"
  flavor_name      = "ec1.medium"
  public_net_name  = "external"
  ssh_keypair_name = "cockatoo-adm"
  system_user      = "ubuntu"
  boot_from_volume = true
  boot_volume_size = 10 # change this to your desired size
  nodes_count      = 1
  nodes_net_cidr   = "192.168.40.0/22"
  rke2_config      = file("controlplane_rke2.yaml")
  manifests_gzb64 = {
    "cinder-csi-plugin" : local.os_cinder_b64
    "openstack-controller-manager" : local.os_ccm_b64
  }
}

module "blue_node" {
  source           = "remche/rke2/openstack//modules/agent"
  image_name       = "Ubuntu-20.04"
  nodes_count      = 1
  name_prefix      = "blue"
  flavor_name      = "ec1.medium"
  node_config      = module.controlplane.node_config
}