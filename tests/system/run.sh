#!/bin/bash

. start_ldap
#. start_mongo

pushd ../../

export PYTHONPATH=$(pwd):$PYTHONPATH
pipenv run python tests/system/test_ldap.py

popd

stop_ldap
#stop_mongo
