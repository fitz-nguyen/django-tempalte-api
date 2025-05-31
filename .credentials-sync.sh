#!/bin/sh

# terraform sync
PROVIDER=${PROVIDER:=aws} mkdir -p ~/Documents/consultant_work/Client_Credentials/${PWD##*/}; cp -af secrets/* ~/Documents/consultant_work/Client_Credentials/${PWD##*/}/
