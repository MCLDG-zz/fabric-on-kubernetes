import os
import yaml

BASEDIR = os.path.dirname('/opt/share/')
ORDERERDIR = os.path.join(BASEDIR, "crypto-config/ordererOrganizations")
PEERDIR = os.path.join(BASEDIR, "crypto-config/peerOrganizations")
CRYPTOCONFIG = './crypto-gen/crypto-config.yaml'

def deleteOrderers(dir, name, domain):
	orgPath = os.path.join(dir, domain)
	namespaceYaml = os.path.join(orgPath, name + "-namespace.yaml" )
	ordererPath = os.path.join(orgPath + "/orderers", name, domain)
	ordererYaml = os.path.join(ordererPath, name + "." + domain + ".yaml")
	print('Org Orderer Deployment YAML: ' + ordererYaml)
	checkAndDelete(ordererYaml)
	print('Org Namespace YAML: ' + namespaceYaml)
	checkAndDelete(namespaceYaml)


def deletePeers(dir, name, domain, peerCount):
	orgPath = os.path.join(dir, domain)
	print('Peer orgPath' + str(orgPath))

	for peerNumber in range(peerCount):
		peerPath = os.path.join(orgPath + "/peers", 'peer' + str(peerNumber) + '.' + domain)
		peerYaml = os.path.join(peerPath, 'peer' + str(peerNumber) + '.' + domain + ".yaml")
		print('Peer Deployment YAML: ' + peerYaml)
		checkAndDelete(peerYaml)

	namespaceYaml = os.path.join(orgPath, name + "-namespace.yaml" )
	checkAndDelete(namespaceYaml)

	caYaml = os.path.join(orgPath, name + "-ca.yaml" )
	checkAndDelete(caYaml)

	cliYaml = os.path.join(orgPath, name + "-cli.yaml" )
	checkAndDelete(cliYaml)


def checkAndDelete(f):
	if os.path.isfile(f):
		os.system("kubectl delete -f " + f)

if __name__ == "__main__":

	config = yaml.load(open(CRYPTOCONFIG))
	for orderer in config['OrdererOrgs']:
		deleteOrderers(ORDERERDIR, orderer['Name'].lower(), orderer['Domain'])

	for peer in config['PeerOrgs']:
		peerCount = peer['Template']['Count']
		deletePeers(PEERDIR, peer['Name'].lower(), peer['Domain'], peerCount)

