const fs = require('fs');
const bluebird = require('bluebird');

bluebird.promisifyAll(fs);

const AWS_ENV = process.env['AWS_ENV'];

const readJson = async (file) => {
  const content = await fs.readFileAsync(file, 'utf-8');
  return JSON.parse(content);
}
const writeJson = async (file, data) => {
  await fs.writeFileAsync(file, JSON.stringify(data, null, 2), 'utf-8');
}

const getTerraformConfig = async () => {
  const { config } = await readJson(`hosting/terraform/app/envs/${AWS_ENV}.json`);
  return config;
}

const getTerraformData = async () => {
  const config = await getTerraformConfig();
  const output = await readJson(`hosting/terraform/app/outputs/${AWS_ENV}.json`);

  Object.keys(output).forEach(outputKey => output[outputKey] = output[outputKey].value);

  return { config, output };
}

module.exports = { readJson, writeJson, getTerraformData, getTerraformConfig };
