#/bin/bash

FILE_PATH=$(dirname $0)
cd $FILE_PATH/src

#check if orb.yml is valid
circleci orb validate @orb.yml

#if not valid, exit
if [ $? -ne 0 ]; then
  exit 1
fi

#pack orb
rm -f orb.yml
circleci orb pack ./ > orb.yml

circleci orb publish orb.yml ethereum-optimism/circleci-utils@dev:first

# circleci orb source ethereum-optimism/circleci-utils@dev:first
