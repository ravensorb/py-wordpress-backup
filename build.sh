#!/bin/bash

sudo rm -r build dist wpbackup2.egg-info

#echo "-------------------------------------------------------------------------------------------"
#echo "Incrementing Version..."
#bumpversion --current-version 0.3.0 minor setup.py wpbackup2/__init__.py

echo "-------------------------------------------------------------------------------------------"
echo "Building..."
python3 setup.py build
python3 setup.py sdist bdist_wheel

echo "-------------------------------------------------------------------------------------------"
echo "Validating"
twine check dist/*
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