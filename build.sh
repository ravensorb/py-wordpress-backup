#!/bin/bash

echo "-------------------------------------------------------------------------------------------"
echo "Removing Old Versions..."
rm -f dist/*

if [ "$1" == "bump" ]; then
    echo "-------------------------------------------------------------------------------------------"
    echo "Staging changes with git"    
    git stage .
    git commit
    
    echo "Incrementing Version..."
    python3 -m bumpversion --list patch
fi

echo "-------------------------------------------------------------------------------------------"
echo "Building..."
python3 setup.py build
python3 setup.py sdist bdist_wheel

echo "-------------------------------------------------------------------------------------------"
echo "Validating"
python3 -m twine check dist/*
retVal=$?
if [ $retVal -ne 0 ]; then
    echo "Error in package. Please fix and try again..."
    exit $retVal
fi

echo "-------------------------------------------------------------------------------------------"
echo "Installing Locally"
sudo python3 setup.py install
echo "-------------------------------------------------------------------------------------------"

rm -r wpbackup2.egg-info
