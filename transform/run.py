import os
import yaml

BASEDIR = os.path.dirname('/opt/share/')
ORDERERDIR = os.path.join(BASEDIR, "crypto-config/ordererOrganizations")
PEERDIR = os.path.join(BASEDIR, "crypto-config/peerOrganizations")
CRYPTOCONFIG = './crypto-gen/crypto-config.yaml'

def runOrderers(dir, name, domain):
	orgPath = os.path.join(dir, domain)
	namespaceYaml = os.path.join(orgPath, name + "-namespace.yaml" )
	print('Org Namespace YAML: ' + namespaceYaml)
	checkAndRun(namespaceYaml)

	ordererPath = os.path.join(orgPath + "/orderers", name + '.' + domain)
	ordererYaml = os.path.join(ordererPath, name + "." + domain + ".yaml")
	print('Org Orderer Deployment YAML: ' + ordererYaml)
	checkAndRun(ordererYaml)

def runPeers(dir, name, domain, peerCount):
	orgPath = os.path.join(dir, domain)
	print('Peer orgPath: ' + str(orgPath))

	namespaceYaml = os.path.join(orgPath, name + "-namespace.yaml" )
	checkAndRun(namespaceYaml)

	caYaml = os.path.join(orgPath, name + "-ca.yaml" )
	checkAndRun(caYaml)

	cliYaml = os.path.join(orgPath, name + "-cli.yaml" )
	checkAndRun(cliYaml)

	for peerNumber in range(peerCount):
		peerPath = os.path.join(orgPath + "/peers", 'peer' + str(peerNumber) + '.' + domain)
		peerYaml = os.path.join(peerPath, 'peer' + str(peerNumber) + '.' + domain + ".yaml")
		print('Peer Deployment YAML: ' + peerYaml)
		checkAndRun(peerYaml)


def checkAndRun(f):
	if os.path.isfile(f):
		os.system("kubectl create -f " + f)

	else:
		print("file %s does not exist"%(f))

if __name__ == "__main__":
	config = yaml.load(open(CRYPTOCONFIG))
	for orderer in config['OrdererOrgs']:
		runOrderers(ORDERERDIR, orderer['Name'].lower(), orderer['Domain'])

	for peer in config['PeerOrgs']:
		peerCount = peer['Template']['Count']
		runPeers(PEERDIR, peer['Name'].lower(), peer['Domain'], peerCount)
