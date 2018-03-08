from string import Template
from pathlib import Path
import string
import config as tc
import os
import yaml

BASEDIR = os.path.dirname('/opt/share/')
ORDERERDIR = os.path.join(BASEDIR, "crypto-config/ordererOrganizations")
PEERDIR = os.path.join(BASEDIR, "crypto-config/peerOrganizations")
CRYPTOCONFIG = './crypto-gen/crypto-config.yaml'

#generateNamespacePod generate the yaml file to create the namespace for k8s, and return a set of paths which indicate the location of org files  

def generateNamespacePod(dir, name, domain):
		## generate namespace first.
		tc.configORGS(name, dir, domain)


def generateDeploymentPod(dir, name, domain):

		if dir.find("peer") != -1: #whether it create orderer pod or peer pod
			suffix = "/peers"
		else:
			suffix = "/orderers"

		memberdir = dir + '/' + domain + suffix
		members = os.listdir(memberdir)
		for member in members:
			print('in generateDeploymentPod, member is: ' + str(member))
			memberDIR = os.path.join(memberdir, member)
			print('in generateDeploymentPod, member directory is: ' + str(memberDIR))
			print('in generateDeploymentPod, member directory listing is: ' + str(os.listdir(memberDIR)))
			tc.generateYaml(member,memberDIR, suffix, domain)


#TODO kafa nodes and zookeeper nodes don't have dir to store their certificate, must use anotherway to create pod yaml.

def allInOne():
	config = yaml.load(open(CRYPTOCONFIG))
	for peer in config['PeerOrgs']:
		generateNamespacePod(PEERDIR, peer['Name'].lower(), peer['Domain'])
		generateDeploymentPod(PEERDIR, peer['Name'].lower(), peer['Domain'])

	for orderer in config['OrdererOrgs']:
		generateNamespacePod(ORDERERDIR, orderer['Name'].lower(), orderer['Domain'])
		generateDeploymentPod(ORDERERDIR, orderer['Name'].lower(), orderer['Domain'])


if __name__ == "__main__" :
	allInOne()
	
