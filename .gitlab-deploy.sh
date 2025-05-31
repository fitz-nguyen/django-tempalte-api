#!/bin/bash
#Get servers list
set -f
string=$DEPLOY_SERVERS
array=(${string//,/ })

# if migrations then migration only
for i in "${!array[@]}"; do
    echo "Run Scripts"
    ssh ubuntu@${array[i]} "cd /usr/src/app/api && sudo chmod +x ./.ci-post-deploy.sh"
    break
done

#Iterate servers for deploy and pull last commit
echo "Deploying to servers $DEPLOY_SERVERS"
for i in "${!array[@]}"; do
    echo "Deploy project on server ${array[i]}"

    echo "Copy artifact to server"
    ssh ubuntu@${array[i]} "sudo mkdir /usr/src/dist -p"
    ssh ubuntu@${array[i]} "sudo chown ubuntu:ubuntu /usr/src/dist"
    scp $CI_JOB_STAGE-$CI_JOB_ID-dist.zip ubuntu@${array[i]}:/usr/src/dist

    if [[ $RUN_SETUP ]]; then
        scp api/.server-setup.sh ubuntu@${array[i]}:/usr/src/dist/.server-setup.sh
        ssh ubuntu@${array[i]} "sudo chmod +x /usr/src/dist/.server-setup.sh"
        ssh ubuntu@${array[i]} "sudo ENVIRONMENT=$CI_JOB_STAGE /usr/src/dist/.server-setup.sh"
        ssh ubuntu@${array[i]} "rm -Rf /usr/src/dist/.server-setup.sh"
    fi

    echo "Clean up"
    ssh ubuntu@${array[i]} "sudo rm -Rf /usr/src/api"
    ssh ubuntu@${array[i]} "sudo rm -Rf /usr/src/app"

    echo "Unzip Artifact /usr/src/dist/$CI_JOB_STAGE-$CI_JOB_ID-dist.zip"
    ssh ubuntu@${array[i]} "sudo unzip /usr/src/dist/$CI_JOB_STAGE-$CI_JOB_ID-dist.zip -d /usr/src/app"
    ssh ubuntu@${array[i]} "sudo chown -Rf ubuntu:ubuntu /usr/src/app"

    echo "Make log directory"
    ssh ubuntu@${array[i]} "mkdir /usr/src/app/api/logs"

    echo "Soft link"
    ssh ubuntu@${array[i]} "sudo ln -s /usr/src/app/api /usr/src/api"

    echo "Run Scripts"
    ssh ubuntu@${array[i]} "cd /usr/src/app/api && sudo chmod +x ./.ci-post-deploy.sh && ENVIRONMENT=$CI_JOB_STAGE ./.ci-post-deploy.sh"
    ssh ubuntu@${array[i]} "cd /usr/src/app/api && sudo chmod +x ./.start-services.sh && ENVIRONMENT=$CI_JOB_STAGE ./.start-services.sh"
done