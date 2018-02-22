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

Steps

To get this working, the steps are:

You need a K8s cluster to start. 
You can create one using the kubernetes-on-aws-quickstart repo in MCLDG github account
git clone the fabric-on-kubernetes repo to your mac
check the parameters in ec2-for-efs/deploy-ec2-sh
The VPC and Subnet params should be those of your existing K8s cluster
Make sure you have a keypair on your laptop, update the params with the key name 
Run deploy-ec2.sh. Check CFN console for completion
When complete, SSH to one of the EC2 instances. The EFS should be mounted in /opt/share
cd fabric-on-kubernetes in the home directory of the EC2 instance - it should have been auto-cloned by the cloud:init script
run ./generateALL.sh. You may need to run using sudo
This will generate the Hyperledger genesis block and other Fabric files. Plus it will generate the K8s YAML files
run python3.5 transform/run.py - this will deploy the K8s YAML files. 
Do a kubectl get all --all-namespaces. You should see the Hyperledger pods running in the org1 and org2 namespaces
run python3.5 transform/delete.py to cleanup
