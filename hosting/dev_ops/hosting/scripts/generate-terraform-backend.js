#! /usr/bin/env node
'use strict';

const fs = require('fs');
const glob = require('glob');
const path = require('path');
const program = require('commander');
const { readJson, writeJson, getTerraformConfig } = require('./common');
const execSync = require('child_process').execSync;

const environment = process.env.ENVIRONMENT || 'development'

let azure_storage_account_key;

program
  .option('--environment [config_name]', 'Environment (production or development', environment)
  .option('--provider [provider]', 'Run terraform based on provider', 'aws')
  .option('--region [region]', 'Run terraform on region', 'us-east-1')
  .option('--refresh [provicer]', 'Refresh state')
  .option('--destroy [config_name]', 'Flag to destroy environment')
  .option('--services [config_name]', 'Generates config for services list', 'vpc')
  .parse(process.argv);

const createTerraformEnvironment = async () => {

  const { config } = await readJson(`hosting/terraform/src/${program.provider}/${program.environment}.json`);

  switch(program.provider) {
    case 'aws':
      execSync(`aws configure list --profile ${config.profile}`, {stdio: 'inherit'})
      execSync(`aws s3api create-bucket --bucket ${config.account_id}.${config.region}.tfstates --profile ${config.profile} --region ${program.region}`)
      break;
    case 'azure':
      execSync(`az login --allow-no-subscriptions --tenant ${config.tenant_id}`)
      execSync(`az group create --name terraform --location ${config.region} --subscription ${config.subscription_id}`)
      execSync(`az storage account create --name ${config.domain}tfstates --resource-group terraform --location ${config.region} --sku Standard_LRS --encryption blob --subscription ${config.subscription_id}`)
      const key_out = execSync(`az storage account keys list -g terraform -n ${config.domain}tfstates --subscription ${config.subscription_id}`).toString()
      azure_storage_account_key = JSON.parse(key_out)[0].value
      execSync(`az storage container create --name tfstates --account-key ${azure_storage_account_key} --account-name ${config.domain}tfstates --subscription ${config.subscription_id}`)
      break;
  }

  // create secrets folder
  // SHOULD REALLY BE SOMEWHERE TOWARDS PROJECT SET UP
  execSync(`mkdir -p secrets`)

  // create environment folder
  execSync(`mkdir -p hosting/terraform/environments/${program.environment}`)
  execSync(`mkdir -p hosting/terraform/environments/${program.environment}/${program.provider}`)

  // copy src to environments folder
  execSync(`cp -Rf hosting/terraform/src/${program.provider} hosting/terraform/environments/${program.environment}`)
  execSync(`cp -Rf hosting/terraform/src/${program.provider} hosting/terraform/environments/${program.environment}`)

  // copy terraform environment files to secrets folder
  execSync(`mkdir -p secrets/${program.environment}/terraform/environments && cp -Rf hosting/terraform/src/${program.provider}/*.json secrets/${program.environment}/terraform/environments`)

};

(async () => {

  // purge
  execSync(`rm -Rf hosting/terraform/environments/${program.environment}`, {stdio: 'inherit'});

  // create environment folder
  await createTerraformEnvironment()

  // services list
  const services_list = program.services.split(',')

  // loop over desired services
  for (let service in services_list) {

    console.log(`**********************************************`)
    console.log(`RUNNING TF BUILD FOR ${services_list[service]}`)
    console.log(`**********************************************`)

    const { config } = await readJson(`hosting/terraform/environments/${program.environment}/${program.provider}/${program.environment}.json`);
    const config_backend = await readJson(`hosting/terraform/environments/${program.environment}/${program.provider}/${program.environment}.backend.json`);

    let bucket
    let backend
    switch(program.provider) {
      case 'aws':
        backend = {
          ...config_backend,
          region: `${program.region}`,
          bucket: `${config.account_id}.${config.region}.tfstates`,
          key: `${program.environment}.${services_list[service]}.tfstate`,
        };
        break;
      case 'azure':
        backend = {
          ...config_backend,
          key: `${program.environment}.${services_list[service]}.tfstate`,
          access_key: azure_storage_account_key
        };
        break;
    }
    console.log(`Created bucket:`, backend)
    await runTerraform(services_list[service], program, config, backend)
  }

})()
.then(() => {
  process.exit(0);
})
.catch(err => {
  console.error(err);
  process.exit(1);
})

const runTerraform = async (component, program, config, backend) => {

  // component
  execSync(`mkdir -p hosting/terraform/environments/${program.environment}/${program.provider}/${component}/envs`, {stdio: 'inherit'});
  await writeJson(`hosting/terraform/environments/${program.environment}/${program.provider}/${component}/envs/${program.environment}.backend.json`, backend);
  await writeJson(`hosting/terraform/environments/${program.environment}/${program.provider}/${component}/envs/${program.environment}.json`, config);
  // console.log(config)
  // execSync(`cp -Rf hosting/terraform/environments/${program.environment}/${program.provider}/${program.environment}.json hosting/terraform/environments/${program.environment}/${program.provider}/${component}/envs/${program.environment}.json`, {stdio: 'inherit'});
  execSync(`cd hosting/terraform/environments/${program.environment}/${program.provider}/${component} && terraform init -backend-config=envs/${environment}.backend.json`, {stdio: 'inherit'});
  if (program.destroy) {
    execSync(`cd hosting/terraform/environments/${program.environment}/${program.provider}/${component} && terraform destroy -var-file=envs/${program.environment}.json`, {stdio: 'inherit'});
    return
  } else if (program.refresh) {
    execSync(`cd hosting/terraform/environments/${program.environment}/${program.provider}/${component} && terraform refresh -var-file=envs/${program.environment}.json`, {stdio: 'inherit'});
  } else {
    execSync(`cd hosting/terraform/environments/${program.environment}/${program.provider}/${component} && terraform apply -auto-approve -var-file=envs/${program.environment}.json`, {stdio: 'inherit'});
  }

  // get output variables and save to secrets folder
  execSync(`mkdir -p secrets/${program.environment}/terraform/output`, {stdio: 'inherit'});
  if (['vpc'].indexOf(component)>=0) {
    execSync(`cd hosting/terraform/environments/${program.environment}/${program.provider}/${component} && terraform output -json domain > domain.json`, {stdio: 'inherit'});
    execSync(`cp hosting/terraform/environments/${program.environment}/${program.provider}/${component}/domain.json secrets/${program.environment}/terraform/output`, {stdio: 'inherit'});
  }
  if (['ec2','virtual_machines'].indexOf(component)>=0) {
    execSync(`cd hosting/terraform/environments/${program.environment}/${program.provider}/${component} && terraform output -json api_public_ip > api_public_ip.json`, {stdio: 'inherit'});
    execSync(`cp hosting/terraform/environments/${program.environment}/${program.provider}/${component}/api_public_ip.json secrets/${program.environment}/terraform/output`, {stdio: 'inherit'});

    execSync(`cd hosting/terraform/environments/${program.environment}/${program.provider}/${component} && terraform output -json private_key_pem > private_key_pem.json`, {stdio: 'inherit'});
    execSync(`cp hosting/terraform/environments/${program.environment}/${program.provider}/${component}/private_key_pem.json secrets/${program.environment}/terraform/output`, {stdio: 'inherit'});

    execSync(`cd hosting/terraform/environments/${program.environment}/${program.provider}/${component} && terraform output -json public_key_pem > public_key_pem.json`, {stdio: 'inherit'});
    execSync(`cp hosting/terraform/environments/${program.environment}/${program.provider}/${component}/public_key_pem.json secrets/${program.environment}/terraform/output`, {stdio: 'inherit'});

    execSync(`cd hosting/terraform/environments/${program.environment}/${program.provider}/${component} && terraform output -json elb_dns_name > elb_dns_name.json`, {stdio: 'inherit'});
    execSync(`cp hosting/terraform/environments/${program.environment}/${program.provider}/${component}/elb_dns_name.json secrets/${program.environment}/terraform/output`, {stdio: 'inherit'});
  }
  if (['db'].indexOf(component)>=0) {
    execSync(`cd hosting/terraform/environments/${program.environment}/${program.provider}/${component} && terraform output -json address > address.json`, {stdio: 'inherit'});
    execSync(`cp hosting/terraform/environments/${program.environment}/${program.provider}/${component}/address.json secrets/${program.environment}/terraform/output`, {stdio: 'inherit'});

    execSync(`cd hosting/terraform/environments/${program.environment}/${program.provider}/${component} && terraform output -json database > database.json`, {stdio: 'inherit'});
    execSync(`cp hosting/terraform/environments/${program.environment}/${program.provider}/${component}/database.json secrets/${program.environment}/terraform/output`, {stdio: 'inherit'});

    execSync(`cd hosting/terraform/environments/${program.environment}/${program.provider}/${component} && terraform output -json password > password.json`, {stdio: 'inherit'});
    execSync(`cp hosting/terraform/environments/${program.environment}/${program.provider}/${component}/password.json secrets/${program.environment}/terraform/output`, {stdio: 'inherit'});

    execSync(`cd hosting/terraform/environments/${program.environment}/${program.provider}/${component} && terraform output -json username > username.json`, {stdio: 'inherit'});
    execSync(`cp hosting/terraform/environments/${program.environment}/${program.provider}/${component}/username.json secrets/${program.environment}/terraform/output`, {stdio: 'inherit'});
  }
  if (['elasticache'].indexOf(component)>=0) {
    execSync(`cd hosting/terraform/environments/${program.environment}/${program.provider}/${component} && terraform output -json cache_nodes > cache_nodes.json`, {stdio: 'inherit'});
    execSync(`cp hosting/terraform/environments/${program.environment}/${program.provider}/${component}/cache_nodes.json secrets/${program.environment}/terraform/output`, {stdio: 'inherit'});
  }
  /*
  if (['cloudwatch'].indexOf(component)>=0) {
    execSync(`cd hosting/terraform/environments/${program.environment}/${program.provider}/${component} && terraform output -json domain_name > cdn_domain_name.json`, {stdio: 'inherit'});
    execSync(`cp hosting/terraform/environments/${program.environment}/${program.provider}/${component}/domain_name.json secrets/${program.environment}/terraform/output`, {stdio: 'inherit'});
  }
  */

};