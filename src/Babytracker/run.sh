#!/bin/bash

# For Heroku; Pocfile is:
#
# web: ./src/Babytracker/run.sh
#

cd src/Babytracker
../../bin/python setup.py develop
../../bin/python runapp.py
