#!/bin/bash

if [ "$1" == "test" ]; then
    python3 -m twine upload --verbose --repository testpypi dist/*
else
    python3 -m twine upload --verbose dist/*
fi