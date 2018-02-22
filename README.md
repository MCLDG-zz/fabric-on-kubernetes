# fabric-on-kubernetes
DLT Fabric on Kubernetes

Issues with EFS

The EFS is mounted on the EC2 instances created by ec2-for-efs.yaml
However, the K8s worker nodes do NOT Have the EFS mounted
Using the EFS provisioner, it seems there is no way to share an EFS directory that already exists
E.g. I create /efsmount/opt/share from the EC2 instances with /efsmount mounted
I then try and reference this directory from the K8s worker nodes
Instead, the efs provisioner creates a new directory on EFS instead of sharing the one that is there
This could be because the efs provisioner does not allow you to create a persistentvolume (it does this automatically).
If it allowed this, you could map to an existing dir.

Solution?

I used a std PV/PVC, pointing to the EFS DNS. Seems to work
I did not use the EFS provisioner

TODO

I install kubectl on the EC2 instance, but no config - need to do this
I paste the kubectl config from my laptop manually
