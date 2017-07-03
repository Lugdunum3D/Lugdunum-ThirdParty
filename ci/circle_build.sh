#!/bin/bash

# Clone Lugdunum to get the config file
git clone https://github.com/Lugdunum3D/Lugdunum.git ~/Lugdunum
cd ~/Lugdunum
git checkout feature-gltf-integration-loader # TODO: Change the branch to dev

# Build the third party for Lugdunum
cd ~/Lugdunum-ThirdParty
mkdir build && cd build && python ../build.py -vvv -z $CIRCLE_ARTIFACTS/Lugdunum-ThirdParty-Linux.zip ~/Lugdunum/thirdparty.yml
