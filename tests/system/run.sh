#!/bin/bash

. start_ldap
. start_mongo

pushd ../../

export PYTHONPATH=$(pwd):$PYTHONPATH
pipenv run python -m pytest tests/system/

popd

stop_mongo
stop_ldap
