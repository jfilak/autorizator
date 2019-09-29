#!/bin/bash

. start_ldap
. start_mongo

pushd ../../

export PYTHONPATH=$(pwd):$PYTHONPATH
pipenv run python -m pytest tests/system/test_ldap.py
pipenv run python -m pytest tests/system/test_mongo.py

popd

stop_mongo
stop_ldap
