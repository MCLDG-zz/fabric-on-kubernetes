from string import Template
#from pathlib import Path
import string
import os
import yaml

TestDir = './dest/'
PORTSTARTFROM = 30000
GAP = 100  #interval for worker's port
EFSCONFIG = './efsconfig.yaml'
def render(src, dest, **kw):
	t = Template(open(src, 'r').read())
	with open(dest, 'w') as f:
		f.write(t.substitute(**kw))


def getTemplate(templateName):
	baseDir = os.path.dirname(__file__)
	configTemplate = os.path.join(baseDir, "../templates/" + templateName)
	return configTemplate


# create org/namespace 
def configORGS(name, path, domain): # name means if of org, path describe where is the namespace yaml to be created.
	efsconfig = yaml.load(open(EFSCONFIG))
	efsserver = efsconfig['efsserver']
	print('efs server url: ' + efsserver)
	print('configORGS. name: ' + name)
	print('configORGS. path: ' + path)
	print('configORGS. domain: ' + domain)
	path = path + '/' + domain
	print('configORGS. full path: ' + path)
	namespaceTemplate = getTemplate("fabric_1_0_template_pod_namespace.yaml")
#	arr = path.split('/')
#	idx = arr.index('crypto-config')
#	pathname = '/'
#	for i in range(idx, len(arr)):
#		pathname = pathname + arr[i] + '/'
	render(namespaceTemplate, path + "/" + name + "-namespace.yaml",
		org = domain,
		pvName = name + "-pv",
		efsserver = efsserver,
		path = path.replace('/opt/share','')
	)

	
	if path.find("peer") != -1 :
		####### pod config yaml for org cli
		cliTemplate = getTemplate("fabric_1_0_template_pod_cli.yaml")
		
		mspPathTemplate = 'users/Admin@{}/msp'

		render(cliTemplate, path + "/" + name + "-cli.yaml",
			name = "cli",
			namespace = name,
			mspPath = mspPathTemplate.format(domain),
			pvName = name + "-pv",
			artifactsName = name + "-artifacts-pv",
			peerAddress = "peer0." + name + ":7051",
 		    efsserver=efsserver,
 		    mspid = name.split('-')[0].capitalize()+"MSP",
		)
		###Need to expose pod's port to worker ! ####
		##org format like this org1-f-1##
		addressSegment = (int(name.split(".")[0].split("org")[-1]) - 1) * GAP
		exposedPort = PORTSTARTFROM + addressSegment

		caTemplate = getTemplate("fabric_1_0_template_pod_ca.yaml")
		
		tlsCertTemplate = '/etc/hyperledger/fabric-ca-server-config/{}-cert.pem'
		tlsKeyTemplate = '/etc/hyperledger/fabric-ca-server-config/{}'
		caPathTemplate = 'ca/'
		cmdTemplate =  ' fabric-ca-server start --ca.certfile /etc/hyperledger/fabric-ca-server-config/{}-cert.pem --ca.keyfile /etc/hyperledger/fabric-ca-server-config/{} -b admin:adminpw -d '

		skFile = ""
		for f in os.listdir(path + "/ca"):  # find out sk!
			if f.endswith("_sk"):
				skFile = f
			
		render(caTemplate, path + "/" + name + "-ca.yaml",
			namespace = name,
			command = '"' + cmdTemplate.format("ca."+name, skFile) + '"',
			caPath = caPathTemplate,
			tlsKey = tlsKeyTemplate.format(skFile),
			tlsCert = tlsCertTemplate.format("ca."+name),
			nodePort = exposedPort,
			pvName = name + "-pv"
		)
		#######

def generateYaml(member, memberPath, flag, domain):
	print('generateYaml. member: ' + member)
	print('generateYaml. memberPath: ' + memberPath)
	print('generateYaml. flag: ' + flag)
	if flag == "/peers":
		configPEERS(member, memberPath, domain)
	else:
		configORDERERS(member, memberPath, domain)
	

# create peer/pod
def configPEERS(name, path, domain): # name means peerid.
	print('configPEERS name: ' + name)
	print('configPEERS. path: ' + path)
	print('configPEERS. domain: ' + domain)
	print('configPEERS. full path: ' + path)
	configTemplate = getTemplate("fabric_1_0_template_pod_peer.yaml")
	
	mspPathTemplate = 'peers/{}/msp'
	tlsPathTemplate =  'peers/{}/tls'
	#mspPathTemplate = './msp'
	#tlsPathTemplate = './tls'
	nameSplit = name.split(".")
	peerName = nameSplit[0]
	orgName = nameSplit[1]

	addressSegment = (int(orgName.split("-")[0].split("org")[-1]) - 1) * GAP
	##peer from like this peer 0##
	peerOffset = int((peerName.split("peer")[-1])) * 2
	exposedPort1 = PORTSTARTFROM + addressSegment + peerOffset + 1
	exposedPort2 = PORTSTARTFROM + addressSegment + peerOffset + 2
	
	render(configTemplate, path + "/" + name + ".yaml", 
		namespace = domain,
		podName = peerName + "-" + domain,
		peerID  = peerName,
		org = domain,
		corePeerID = name,
		peerAddress = name + ":7051",
		peerGossip = name  + ":7051",
		localMSPID = orgName.split('-')[0].capitalize()+"MSP",
		mspPath = mspPathTemplate.format(peerName + '.' + domain),
		tlsPath = tlsPathTemplate.format(peerName + '.' + domain),
		nodePort1 = exposedPort1,
		nodePort2 = exposedPort2,
		pvName = domain + "-pv"
	)


# create orderer/pod
def configORDERERS(name, path, domain): # name means ordererid
	efsconfig = yaml.load(open(EFSCONFIG))
	efsserver = efsconfig['efsserver']
	print('configORDERERS name: ' + name)
	print('configORDERERS. path: ' + path)
	print('configORDERERS. domain: ' + domain)
	configTemplate = getTemplate("fabric_1_0_template_pod_orderer.yaml")
	
	mspPathTemplate = 'orderers/{}/msp'
	tlsPathTemplate = 'orderers/{}/tls'

	nameSplit = name.split(".")
	ordererName = nameSplit[0]
	orgName = nameSplit[1]

	#TODO - uncomment this and test whether it supports multiple orderers
	#ordererOffset = int(ordererName.split("orderer")[-1])
	ordererOffset = 1
	exposedPort = 32000 + ordererOffset

	render(configTemplate, path + "/" + name + ".yaml", 
		namespace = domain,
		ordererID = ordererName,
		podName =  ordererName + "-" + domain,
		localMSPID =  orgName.capitalize() + "MSP",
		mspPath= mspPathTemplate.format(ordererName + '.' + domain),
		tlsPath= tlsPathTemplate.format(ordererName + '.' + domain),
		nodePort = exposedPort,
	    artifactsName=ordererName + "-artifacts-pv",
	    efsserver=efsserver,
	    pvName = ordererName + "-pv"
	)



#if __name__ == "__main__":
#	#ORG_NUMBER = 3
#	podFile = Path('./fabric_cluster.yaml')
#	if podFile.is_file():
#		os.remove('./fabric_cluster.yaml')

#delete the previous exited file	
#	configPeerORGS(1, 2)
#	configPeerORGS(2, 2)
#	configOrdererORGS()
