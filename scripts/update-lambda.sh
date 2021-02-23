#!/usr/bin/env bash

# Update existing zip file with lambda code and deploy
# (requires AWS credentials in environment or ~/.aws/credentials)

set -e

PROJECT_DIR=$(realpath $(dirname "${BASH_SOURCE[0]}")/..)
FUNCTION=OperateGarage
ZIP=$PROJECT_DIR/$FUNCTION.zip
FILES=".env lambda_function.py"

cd $PROJECT_DIR
echo "Adding files to $ZIP ..."
zip -g $ZIP $FILES
echo "Update lambda function code ..."
aws lambda update-function-code --region us-east-1 --function-name $FUNCTION --zip-file fileb://$FUNCTION.zip
