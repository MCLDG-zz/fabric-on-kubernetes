# fabric-on-kubernetes
DLT Fabric on Kubernetes

TODO

I install kubectl on the EC2 instance, but no config - need to do this
I paste the kubectl config from my laptop manually
I have to manually update the docker_opts on the worker nodes - can I automate this?

## Steps

To get this working, the steps are:

You need a K8s cluster to start. 
You can create one using the kubernetes-on-aws-quickstart repo in MCLDG github account
git clone the fabric-on-kubernetes repo to your mac
check the parameters in ec2-for-efs/deploy-ec2-sh
The VPC, RouteTable, CIDR, and Subnet params should be those of your existing K8s cluster
Keypair is a keypair you own, that you have previously saved to your Mac. You'll need this to access the EC2 
instance created by deploy-ec2.sh
VolumeName is the name assigned to your EFS volume
Once all the parameters are set, in a terminal window run ./ec2-for-efs/deploy-ec2.sh. Check CFN console for completion
When complete, SSH to one of the EC2 instances. The EFS should be mounted in /opt/share
cd /home/ec2-user/fabric-on-kubernetes - this directory should have been auto-cloned by the cloud:init script
run ./runALL.sh. 
This will generate the Hyperledger genesis block and other Fabric files. 

Now, the next step needs kubectl, which has been installed but is not pointing to any kubernetes cluster.
We need to point it to your K8s cluster.
Easiest method (though this should be improved) is to copy the contents of your own ~/.kube/config file from your Mac (or whichever device you used to create the Kubernetes cluster)
On the EC2 instance created above, do 'mkdir /home/ec2-user/.kube'
then 'vi config' in the .kube directory and paste/save the contents of your config file
Then do 'kubectl get nodes' to check kubectl is working and pointing to your cluster.

cd /home/ec2-user/fabric-on-kubernetes
run python3.5 transform/generate.py - this will generate the K8s YAML files. 
run python3.5 transform/run.py - this will deploy the K8s YAML files. 
Do a kubectl get all --all-namespaces. You should see the Hyperledger pods running in the org1, org2 and orgorderer namespaces
The pods should have a status of 'Running'. For troubleshooting do 'kubectl logs' on the Hyperledger pods.
To test hyperledger is working, execute the commands in the test/test.sh folder. 

## Cleanup
* cd /home/ec2-user/fabric-on-kubernetes
* run python3.5 transform/delete.py to cleanup

## Troubleshooting

### Using EFS for shared storage: certs, blocks, etc

There is no need to use the EFS Provisioner. Instead, just mount EFS directly using the standard K8s PV/PVC mechanism.

EFS Provisioner: https://github.com/kubernetes-incubator/external-storage/tree/master/aws/efs

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

### Peers cannot start chaincode server
If you see your peer pods have a status of 'Error' when doing 'kubectl get pods -n --all-namespaces',
and you check the logs and see an entry similar to the following in your peer logs, 
i.e. when executing 'kubectl logs peer0-org1-7f69b8f86c-zsh66 -n org1 -c peer0-org1'

2018-03-11 01:35:59.221 UTC [nodeCmd] createChaincodeServer -> WARN 043 peer.chaincodeListenAddress is not set, using peer0.org1:7052
2018-03-11 01:35:59.223 UTC [nodeCmd] createChaincodeServer -> ERRO 044 Error creating GRPC server: listen tcp 100.66.112.84:7052: bind: cannot assign requested address
2018-03-11 01:35:59.223 UTC [nodeCmd] serve -> CRIT 045 Failed to create chaincode server: listen tcp 100.66.112.84:7052: bind: cannot assign requested address
panic: Failed to create chaincode server: listen tcp 100.66.112.84:7052: bind: cannot assign requested address

Peer pods must contain this in the peer YAML under spec->containers->env:

        - name: CORE_PEER_CHAINCODELISTENADDRESS
          value: 0.0.0.0:7052


### Chaincode cannot be instantiated
When instantiating chaincode from the CLI server using the command below:

peer chaincode instantiate -o orderer.orgorderer:7050 -C mychannel -n mycc -v 1.0 -c '{"Args":["init","a", "100", "b","200"]}' -P "OR ('Org1MSP.peer','Org2MSP.peer')"

If you see the following:
2018-03-11 01:47:02.735 UTC [dockercontroller] stopInternal -> DEBU 55e Removed container dev-peer0.org1-mycc-1.0
2018-03-11 01:47:02.735 UTC [container] unlockContainer -> DEBU 55f container lock deleted(dev-peer0.org1-mycc-1.0)
2018-03-11 01:47:02.735 UTC [chaincode] func1 -> DEBU 560 chaincode mycc:1.0 launch seq completed
2018-03-11 01:47:02.735 UTC [chaincode] Launch -> ERRO 561 launchAndWaitForRegister failed: timeout expired while starting chaincode mycc:1.0(networkid:dev,peerid:peer0.org1,tx:733c788fb7219889d872d8cbe9de25a119022fc7c87c169b983481a6c694377c)

Peer pods cannot access chaincode pods. This is a known K8s problem, and occurs due to peer pods starting
chaincode pods using Docker, so K8s is not aware of them. They are therefore not registered in the K8s DNS.

See: http://www.think-foundry.com/deploy-hyperledger-fabric-on-kubernetes-part-1/

To work around this problem, we need to add the Kube_dns IP address in each worker node’s Docker engine. Add in the 
below option in Docker engine’s configuration file. In the below example, 10.0.0.10 is the IP address of kube_dns pod. 
Replace it with the right value in your environment.

To update the docker engine on the AWS EC2 instance provisoned by kops (they are Debian Jessie), do the following
for EVERY EC2 worker node:

ssh -i ~/.ssh/mcdg2k8s admin@ec2-18-219-254-91.us-east-2.compute.amazonaws.com

Note: the key in the .ssh folder was created by the Kubernetes Quickstart, and will use the name of your cluster. If you 
created the cluster using Kops, the key should be ~/.ssh/id_rsa. If you created the K8s cluster in some other way, 
use your own key. 

sudo systemctl show docker | grep Env
more /etc/sysconfig/docker
sudo vi /etc/sysconfig/docker

update the file to include the options and save it:
DOCKER_OPTS=--ip-masq=false --iptables=false --log-driver=json-file --log-level=warn --log-opt=max-file=5 --log-opt=max-size=10m --storage-driver=overlay --dns=10.0.0.10 --dns=192.168.0.1 --dns-search=default.svc.cluster.local --dns-search=svc.cluster.local --dns-opt=ndots:2 --dns-opt=timeout:2 --dns-opt=attempts:2

sudo systemctl restart docker
sudo docker info

I tried using Kops to edit the cluster and update the docker_opts; unfortunately Kops only support a limited
set of docker options so this does not work. Here are the docker opts supported by Kops: 
https://github.com/kubernetes/kops/blob/master/pkg/apis/kops/dockerconfig.go#L20

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
  .
  .
  .
  
## References
* Deploying Hyperledger on K8s: https://medium.com/@zhanghenry/how-to-deploy-hyperledger-fabric-on-kubernetes-2-751abf44c807 (parts 1 & 2) & https://github.com/hainingzhang/articles/tree/master/fabric_on_kubernetes
* Hyperledger docker images: https://nexus.hyperledger.org/content/repositories/releases/org/hyperledger/fabric/hyperledger-fabric/
* Overview of running Hyperledger: https://medium.com/@vitaly.bezgachev/hyperledger-fabric-in-practice-part-1-main-components-and-running-them-locally-aa4b805465fa
* Fabric docs: http://hyperledger-fabric.readthedocs.io/en/latest/prereqs.html
* Fabric Github repo: https://github.com/hyperledger/fabric
* Issue with time out during 'chaincode instantiate': https://github.com/chawlanikhil24/hyperledger-fabric-k8s/issues/4
