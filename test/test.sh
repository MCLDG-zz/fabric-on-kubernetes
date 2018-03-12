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


#now, exec into the CLI pod in the other namespace: 'kubectl exec -it <cli pod name> -n org2 bash'

#ls will show that the mychannel.block exists. You'll now join this channel from another org
ls channel-artifacts/

peer channel join -b ./channel-artifacts/mychannel.block
peer channel update -o orderer.orgorderer:7050 -c mychannel -f ./channel-artifacts/Org2MSPanchors.tx
peer chaincode list -C mychannel --instantiated

#You should see something like this. the 'Name' shows that the mycc chaincode is instantiated and visible in org2:
2018-03-11 11:51:57.739 UTC [msp] GetLocalMSP -> DEBU 001 Returning existing local MSP
2018-03-11 11:51:57.739 UTC [msp] GetDefaultSigningIdentity -> DEBU 002 Obtaining default signing identity
2018-03-11 11:51:57.739 UTC [msp/identity] Sign -> DEBU 003 Sign: plaintext: 0A8E070A6708031A0C08DDB094D50510...0F0A0D676574636861696E636F646573
2018-03-11 11:51:57.739 UTC [msp/identity] Sign -> DEBU 004 Sign: digest: 13ABB886CCE7175550EE75CAB91D6D07C945025F8726B1BAC63D3E1014DFE649
Get instantiated chaincodes on channel mychannel:
Name: mycc, Version: 1.0, Escc: escc, Vscc: vscc
2018-03-11 11:51:57.758 UTC [main] main -> INFO 005 Exiting.....

#you can also query the chaincode
git clone https://github.com/hyperledger/fabric.git
peer chaincode install -n mycc -v 1.0 -p github.com/hyperledger/fabric/peer/fabric/examples/chaincode/go/chaincode_example02
peer chaincode query -C mychannel -n mycc -c '{"Args":["query","a"]}'

#you should see the following
2018-03-11 12:02:26.423 UTC [msp] GetLocalMSP -> DEBU 001 Returning existing local MSP
2018-03-11 12:02:26.423 UTC [msp] GetDefaultSigningIdentity -> DEBU 002 Obtaining default signing identity
2018-03-11 12:02:26.423 UTC [chaincodeCmd] checkChaincodeCmdParams -> INFO 003 Using default escc
2018-03-11 12:02:26.423 UTC [chaincodeCmd] checkChaincodeCmdParams -> INFO 004 Using default vscc
2018-03-11 12:02:26.423 UTC [chaincodeCmd] getChaincodeSpec -> DEBU 005 java chaincode disabled
2018-03-11 12:02:26.423 UTC [msp/identity] Sign -> DEBU 006 Sign: plaintext: 0A8E070A6708031A0C08D2B594D50510...6D7963631A0A0A0571756572790A0161
2018-03-11 12:02:26.424 UTC [msp/identity] Sign -> DEBU 007 Sign: digest: E23FCDFEA6C69EA795B61C005F24EC9384DBF080A15C275945E05A1A07683DBC
Query Result: 100
2018-03-11 12:02:44.207 UTC [main] main -> INFO 008 Exiting.....