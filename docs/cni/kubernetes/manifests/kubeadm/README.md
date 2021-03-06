# Install for Kubeadm

This directory contains a single packaged manifest for installing Calico on kubeadm managed Kubernetes clusters.  It is a specific case of the 
more general manifests provided [here](../README.md)

To install this manifest, make sure you've created a cluster using the kubeadm tool.

Then use kubectl to create the manifest in this directory:

```
kubectl create -f calico.yaml
```

## About

This manifest deploys the standard Calico components described [here](../README.md#how-it-works) as well as a dedicated Calico etcd
node on the Kubernetes master.  Note that in a production cluster, it is recommended you use a secure, replicated etcd cluster.

### Requirements / Limitations

* This install does not configure etcd TLS
* This install expects that your Kubernetes master node has been labeled with `kubeadm.alpha.kubernetes.io/role: master`

