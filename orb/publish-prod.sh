#/bin/bash

FILE_PATH=$(dirname $0)
cd $FILE_PATH/src

#check if orb.yml is valid
circleci orb validate @orb.yml

#if not valid, exit
if [ $? -ne 0 ]; then
  exit 1
fi

#before continuing make sure we ask for confirmation
read -p "Are you sure you want to publish the orb? (y/n) " -n 1 -r
echo   # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

circleci orb publish promote ethereum-optimism/circleci-utils@dev:first patch

#if the publish was successful, we should add a tag to the repository with the same version as the orb
if [ $? -eq 0 ]; then
    #get the version of the orb
    ORB_VERSION=$(circleci orb info ethereum-optimism/circleci-utils | grep -i latest | cut -d"@" -f2)
    #tag the repository with the version of the orb
    git tag -a orb/$ORB_VERSION -m "Version orb/$ORB_VERSION"
    git push origin $ORB_VERSION
    else
    exit 1
fi