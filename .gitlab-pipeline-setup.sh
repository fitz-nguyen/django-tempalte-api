#!/bin/bash

echo ""
echo "#########################"
echo "# Creating Gitlab CI config for ${ENVIRONMENT}"
echo "# Frontend URL: ${FRONTEND_BASE_URL}" #http://localhost
echo "# Backend URL: ${BASE_URL}"
echo "#########################"
echo ""

# get the json objects from terraform
djangoFile=`cat secrets/${ENVIRONMENT}/django/settings/.env.${ENVIRONMENT}`
deployServers=`jq -r ".value" secrets/${ENVIRONMENT}/terraform/output/api_public_ip.json`
sshPrivateKey=`jq -r ".value" secrets/${ENVIRONMENT}/terraform/output/private_key_pem.json`

echo ${djangoFile}
echo ${deployServers}
echo ${sshPrivateKey}
ENVIRONMENT_UPPER=`echo ${ENVIRONMENT} | tr [a-z] [A-Z]`


curl --request DELETE --header "PRIVATE-TOKEN: ${GITLABS_ACCESS_TOKEN}" "https://gitlab.com/api/v4/projects/${GITLAB_PROJECT_ID}/variables/${ENVIRONMENT_UPPER}_DEPLOY_SERVERS"
curl --request POST --header "PRIVATE-TOKEN: ${GITLABS_ACCESS_TOKEN}" "https://gitlab.com/api/v4/projects/${GITLAB_PROJECT_ID}/variables" --form "key=${ENVIRONMENT_UPPER}_DEPLOY_SERVERS" --form "value=${deployServers}"
curl --request DELETE --header "PRIVATE-TOKEN: ${GITLABS_ACCESS_TOKEN}" "https://gitlab.com/api/v4/projects/${GITLAB_PROJECT_ID}/variables/${ENVIRONMENT_UPPER}_ENV_FILE"
curl --request POST --header "PRIVATE-TOKEN: ${GITLABS_ACCESS_TOKEN}" "https://gitlab.com/api/v4/projects/${GITLAB_PROJECT_ID}/variables" --form "key=${ENVIRONMENT_UPPER}_ENV_FILE" --form "value=${djangoFile}" --form "variable_type=file"
curl --request DELETE --header "PRIVATE-TOKEN: ${GITLABS_ACCESS_TOKEN}" "https://gitlab.com/api/v4/projects/${GITLAB_PROJECT_ID}/variables/${ENVIRONMENT_UPPER}_SSH_PRIVATE_KEY"
curl --request POST --header "PRIVATE-TOKEN: ${GITLABS_ACCESS_TOKEN}" "https://gitlab.com/api/v4/projects/${GITLAB_PROJECT_ID}/variables" --form "key=${ENVIRONMENT_UPPER}_SSH_PRIVATE_KEY" --form "value=${sshPrivateKey}"