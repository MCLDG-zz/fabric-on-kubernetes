#!/usr/bin/env bash

#after running ./run-all.sh, followed by transform/generate.py, and transform/run.py,
#enter into the CLI pod using 'kubectl exec -it <cli pod name> -n org1 bash'
#then execute the following
#info here: https://medium.com/@zhanghenry/how-to-deploy-hyperledger-fabric-on-kubernetes-2-751abf44c807
peer channel create -o orderer.orgorderer:7050 -c mychannel -f ./channel-artifacts/channel.tx
cp mychannel.block channel-artifacts/
peer channel join -b ./channel-artifacts/mychannel.block
peer channel update -o orderer.orgorderer:7050 -c mychannel -f ./channel-artifacts/Org1MSPanchors.tx
git clone https://github.com/hyperledger/fabric.git
peer chaincode install -n mycc -v 1.0 -p github.com/hyperledger/fabric/peer/fabric/examples/chaincode/go/chaincode_example02
peer chaincode instantiate -o orderer.orgorderer:7050 -C mychannel -n mycc -v 1.0 -c '{"Args":["init","a", "100", "b","200"]}' -P "OR ('Org1MSP.peer','Org2MSP.peer')"
peer chaincode list -C mychannel --instantiated