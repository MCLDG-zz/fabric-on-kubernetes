#!/usr/bin/env bash

export FABRICUTILS=$PWD/bin
export EFSMOUNT=/opt/share
export CHANNELARTIFACTS=$EFSMOUNT/channel-artifacts
export CHANNELNAME="mychannel"
export FABRIC_CFG_PATH=${PWD}/configtx-gen

# Generate orderer genesis block, channel configuration transaction and
# anchor peer update transactions
function generateChannelArtifacts() {
  if [ -d "$CHANNELARTIFACTS" ]; then
    rm -Rf $CHANNELARTIFACTS
  fi
  if [ ! -d $CHANNELARTIFACTS ]; then
    mkdir $CHANNELARTIFACTS
  fi
  echo "##########################################################"
  echo "#########  Generating Orderer Genesis block ##############"
  echo "##########################################################"
  # Note: For some unknown reason (at least for now) the block file can't be
  # named orderer.genesis.block or the orderer will fail to launch!
  $FABRICUTILS/configtxgen -profile TwoOrgsOrdererGenesis -outputBlock $CHANNELARTIFACTS/genesis.block
  if [ "$?" -ne 0 ]; then
    echo "Failed to generate orderer genesis block..."
    exit 1
  fi
  echo
  echo "#################################################################"
  echo "### Generating channel configuration transaction 'channel.tx' ###"
  echo "#################################################################"
  $FABRICUTILS/configtxgen -profile TwoOrgsChannel -outputCreateChannelTx $CHANNELARTIFACTS/channel.tx -channelID $CHANNELNAME
  if [ "$?" -ne 0 ]; then
    echo "Failed to generate channel configuration transaction..."
    exit 1
  fi

  echo
  echo "#################################################################"
  echo "#######    Generating anchor peer update for Org1MSP   ##########"
  echo "#################################################################"
  $FABRICUTILS/configtxgen -profile TwoOrgsChannel -outputAnchorPeersUpdate $CHANNELARTIFACTS/Org1MSPanchors.tx -channelID $CHANNELNAME -asOrg Org1MSP
  if [ "$?" -ne 0 ]; then
    echo "Failed to generate anchor peer update for Org1MSP..."
    exit 1
  fi

  echo
  echo "#################################################################"
  echo "#######    Generating anchor peer update for Org2MSP   ##########"
  echo "#################################################################"
  $FABRICUTILS/configtxgen -profile TwoOrgsChannel -outputAnchorPeersUpdate $CHANNELARTIFACTS/Org2MSPanchors.tx -channelID $CHANNELNAME -asOrg Org2MSP
  if [ "$?" -ne 0 ]; then
    echo "Failed to generate anchor peer update for Org2MSP..."
    exit 1
  fi
  echo
}

generateChannelArtifacts