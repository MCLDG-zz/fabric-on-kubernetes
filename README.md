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
In a terminal window run ./ec2-for-efs/deploy-ec2.sh. Check CFN console for completion
When complete, SSH to one of the EC2 instances. The EFS should be mounted in /opt/share
cd fabric-on-kubernetes in the home directory of the EC2 instance - it should have been auto-cloned by the cloud:init script
run ./generateALL.sh. You may need to run using sudo
This will generate the Hyperledger genesis block and other Fabric files. Plus it will generate the K8s YAML files

Now, the next step needs kubectl, which has been installed but is not pointing to any kubernetes cluster.
We need to point it to your K8s cluster.
Easiest method (thought this should be improved) is to copy the contents of your own ~/.kube/config file
On the EC2 instance created above, do 'mkdir /home/ec2-user/.kube'
then 'vi config' and paste/save the contents of your config file
Then do 'kubectl get nodes' to check kubectl is working and pointing to your cluster.

run python3.5 transform/run.py - this will deploy the K8s YAML files. 
Do a kubectl get all --all-namespaces. You should see the Hyperledger pods running in the org1, org2 and orgorderer namespaces

To test hyperledger is working, execute the commands in the test folder. 

run python3.5 transform/delete.py to cleanup

## Troubleshoorting

2018-03-11 01:35:59.221 UTC [nodeCmd] createChaincodeServer -> WARN 043 peer.chaincodeListenAddress is not set, using peer0.org1:7052
2018-03-11 01:35:59.223 UTC [nodeCmd] createChaincodeServer -> ERRO 044 Error creating GRPC server: listen tcp 100.66.112.84:7052: bind: cannot assign requested address
2018-03-11 01:35:59.223 UTC [nodeCmd] serve -> CRIT 045 Failed to create chaincode server: listen tcp 100.66.112.84:7052: bind: cannot assign requested address
panic: Failed to create chaincode server: listen tcp 100.66.112.84:7052: bind: cannot assign requested address

Peer pods must contain this under spec->containers->env:

        - name: CORE_PEER_CHAINCODELISTENADDRESS
          value: 0.0.0.0:7052


Peer pods cannot access chaincode pods. This is a known K8s problem, and occurs due to peer pods starting
chaincode pods using Docker, so K8s is not aware of them. They are therefore not registered in the K8s DNS.

See: http://www.think-foundry.com/deploy-hyperledger-fabric-on-kubernetes-part-1/

To work around this problem, we need to add the Kube_dns IP address in each worker node’s Docker engine. Add in the 
below option in Docker engine’s configuration file. In the below example, 10.0.0.10 is the IP address of kube_dns pod. 
Replace it with the right value in your environment.

To update the docker engine on the AWS EC2 instance provisoned by kops (they are Debian Jessy), do the following:

ssh -i ~/.ssh/mcdg2k8s admin@ec2-18-219-254-91.us-east-2.compute.amazonaws.com

sudo systemctl show docker | grep Env
more /etc/sysconfig/docker
more /etc/environment
sudo vi /etc/sysconfig/docker

update the file to include the options and save it:
DOCKER_OPTS=--ip-masq=false --iptables=false --log-driver=json-file --log-level=warn --log-opt=max-file=5 --log-opt=max-size=10m --storage-driver=overlay --dns=10.0.0.10 --dns=192.168.0.1 --dns-search=default.svc.cluster.local --dns-search=svc.cluster.local --dns-opt=ndots:2 --dns-opt=timeout:2 --dns-opt=attempts:2

sudo systemctl restart docker
sudo docker info


"--dns=10.0.0.10 --dns=192.168.0.1 --dns-search \
default.svc.cluster.local --dns-search \
svc.cluster.local --dns-opt ndots:2 --dns-opt \
timeout:2 --dns-opt attempts:2 "

DOCKER_OPTS="--dns=100.64.0.10 --dns=192.168.0.1 --dns-search \
default.svc.cluster.local --dns-search \
svc.cluster.local --dns-opt ndots:2 --dns-opt \
timeout:2 --dns-opt attempts:2 "

do 'kops edit cluster'

apiVersion: kops/v1alpha2
kind: Cluster
metadata:
  creationTimestamp: 2018-02-06T22:43:03Z
  name: mcdgk8s.cluster.k8s.local
spec:
  docker:
    dns: 100.64.0.10
    dns: 192.168.0.1
    dns-search: default.svc.cluster.local
    dns-search: svc.cluster.local
    dns-opt: ndots:2
    dns-opt: timeout:2
    dns-opt: attempts:2
  additionalPolicies:
  
  
apiVersion: kops/v1alpha2
kind: Cluster
metadata:
  creationTimestamp: 2018-02-06T22:43:03Z
  name: mcdgk8s.cluster.k8s.local
spec:
  docker:
    dns:
    - 100.64.0.10
    - 192.168.0.1
    dns-search:
    - default.svc.cluster.local
    - svc.cluster.local
    dns-opt:
    - ndots:2
    - timeout:2
    - attempts:2
  additionalPolicies: