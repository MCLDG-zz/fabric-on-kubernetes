#!/usr/bin/env bash

export FABRICUTILS=$PWD/bin
export CRYPTOCONFIG=$PWD/../crypto-config
generateCerts
copyCerts

function generateCerts (){
  echo "Generate certificates using cryptogen tool"

  if [ -d "$CRYPTOCONFIG" ]; then
    rm -Rf $CRYPTOCONFIG
  fi
  set -x
  $FABRICUTILS/cryptogen generate --config=./crypto-config.yaml
  set +x
  if [ "$?" -ne 0 ]; then
    echo "Failed to generate certs..."
    exit 1
  fi
}

function copyCerts (){
    echo "Copy certificates to EFS"
    chmod -R 777 $CRYPTOCONFIG
	cp -r $CRYPTOCONFIG /opt/share/
}	