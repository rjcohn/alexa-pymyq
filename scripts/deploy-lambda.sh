#!/usr/bin/env bash

# Create zip file with lambda code and deploy
# (requires AWS credentials in environment or ~/.aws/credentials)

set -e

SCRIPT_DIR=$(realpath $(dirname "${BASH_SOURCE[0]}"))
PROJECT_DIR=$(realpath $SCRIPT_DIR/..)
FUNCTION=OperateGarage
ZIP=$FUNCTION.zip

cd $PROJECT_DIR
echo "Create site-packages.zip ..."
$SCRIPT_DIR/shrink-site-packages.sh

# keep site packages if we want to reuse it
cp site-packages.zip $ZIP

$SCRIPT_DIR/update-lambda.sh
