# AWS targets (update, deploy) require credentials in ~/.aws/credentials and optionally AWS_PROFILE

test:
	pytest

# update zip with latest code (but don't update site packages) and deploy
update:
	scripts/update-lambda.sh

# rebuild and deploy lambda
deploy:
	scripts/deploy-lambda.sh
