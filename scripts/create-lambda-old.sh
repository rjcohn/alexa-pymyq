#!/usr/bin/env bash

# Create zip file with lambda code for old-style skill (no .env file)

set -e

SCRIPT_DIR=$(realpath $(dirname "${BASH_SOURCE[0]}"))
PROJECT_DIR=$(realpath $SCRIPT_DIR/..)
ZIP=lambda-upload.zip

cd $PROJECT_DIR
echo "Create site-packages.zip ..."
$SCRIPT_DIR/shrink-site-packages.sh

# keep site packages if we want to reuse it
cp site-packages.zip $ZIP

FILES="lambda_function.py"

cd $PROJECT_DIR
echo "Adding files to $ZIP ..."
zip -g $ZIP $FILES
