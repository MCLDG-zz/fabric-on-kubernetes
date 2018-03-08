#!/usr/bin/env bash

export CRYPTOCONFIGSUFFIX=crypto-config
export FABRICUTILS=$PWD/bin
export EFSMOUNT=/opt/share
export CRYPTOCONFIG=$EFSMOUNT/$CRYPTOCONFIGSUFFIX

function generateCerts (){
  echo "Generate certificates using cryptogen tool"

  if [ -d "$CRYPTOCONFIG" ]; then
    rm -Rf $CRYPTOCONFIG
  fi
  $FABRICUTILS/cryptogen generate --config=./crypto-gen/crypto-config.yaml --output=$CRYPTOCONFIG
  if [ "$?" -ne 0 ]; then
    echo "Failed to generate certs..."
    exit 1
  fi
}

generateCerts
