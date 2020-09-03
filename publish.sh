#!/bin/bash

if [ "$1" == "test" ]; then
    twine upload --verbose --repository-url https://test.pypi.org/legacy/ dist/*
else
    twine upload --verbose dist/*
fi