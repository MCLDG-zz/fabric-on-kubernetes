#!/usr/bin/env bash

export FABRICUTILS=$PWD/bin
export CRYPTOCONFIG=$PWD/crypto-gen
export CONFIGTX=$PWD/configtx-gen

$CRYPTOCONFIG/gen-certs.sh
$CONFIGTX/gen-configtx.sh
