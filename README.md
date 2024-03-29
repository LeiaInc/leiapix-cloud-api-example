# Leia Media Cloud REST API Demo app

This repo contains examples of backend integration with Media Cloud REST API.

The examples are provided for two use cases:
* using LeiaPix temporary storage API. Please refer to [NodeJS](src/using-leiapix-storage.ts) and [Python3](src/using-leiapix-storage.py) files to see the code integration examples for each corresponding language.
* using your own S3 storage. Please refer to [NodeJS](src/using-custom-storage.ts) and [Python3](src/using-custom-storage.py) files to see the code integration examples for each corresponding language.

# Using LeiaPix temporary storage

## Configuration
In order to run this script, a set of credentials is used:
 `Leia Backend Client ID` and `Leia Backend Client Secret` - to access Leia Media Cloud API. Can be acquired in Leia Account API Section.

### Configuring Leia Media Cloud credentials and other parameters (required for both NodeJS and Python3 examples)
Rename `.env.tmpl` into `.env`. Put next env vars in `.env` at root folder. The package.json `start:<platform>` script will read these values to be used in the script.
* `ORIGINAL_IMAGE_URL=<image_url>` - URL of the image to convert to animation or to generate disparity map from
* `BACKEND_CLIENT_ID=<value>` - Leia Backend Client ID
* `BACKEND_CLIENT_SECRET=<value>` - Leia Backend Client Secret

### Configuring node.js example
Before running the `npm run start:nodejs-provided`, you need to install npm dependencies: `npm i`.

#### Running node.js example
After the configuration is done, you can run this script with `npm run start:nodejs-provided`.

### Configuring python3 example
Before running the `npm run start:python-provided`, you would want to configure `virtualenv` for a python project:
1. Make sure you have python3 installed
2. Run `python3 -m venv demoenv` in the root directory of the demo project. This will create local virtual env for this project.
3. Run `source demoenv/bin/activate` from the root directory. This will make current virtual env an active virtual env, preventing polluting global dependencies space with this project dependencies.
4. Run `pip install -r requirements.txt` from the root directory. This will install all the project dependencies in the currently active virtual env.

#### Running python3 example
After the configuration of virtual env is completed, you may run the python example script with `npm run start:python-provided`. Running this command instead of running a file directly with `python3 src/using-leiapix-storage.py` will read env values from `.env` and make them available as ENV vars during script execution.

# Using your own custom s3 storage

## Configuration
In order to run this script, two sets of credentials are used: 
1. `AWS Access Key ID` and `AWS Secret Access Key` (so that script can generate AWS S3 pre-signed URLs)
2. `Leia Backend Client ID` and `Leia Backend Client Secret` - to access Leia Media Cloud API. Can be acquired in Leia Account API Section.

### Configure AWS CLI (required for both NodeJS and Python3 examples)
These scripts are intended for demonstration purposes only. Because of this, they rely on a [configured AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html#cli-configure-files-methods) so that they can be run from a CLI. After this is done, the `@aws-sdk/credential-provider-node` and `boto3` packages used in these scripts will handle auth with AWS.

Real production integration should be done with secrets properly managed via CI/CD, and accessed in application environment instead. 

### Configuring Leia Media Cloud credentials and other parameters (required for both NodeJS and Python3 examples)
Rename `.env.tmpl` into `.env`. Put next env vars in `.env` at root folder. The package.json `start:<platform>` script will read these values to be used in the script.
* `ORIGINAL_IMAGE_URL=<image_url>` - URL of the image to convert to animation or to generate disparity map from
* `BACKEND_CLIENT_ID=<value>` - Leia Backend Client ID
* `BACKEND_CLIENT_SECRET=<value>` - Leia Backend Client Secret
* `S3_BUCKET_NAME=<value>` - AWS S3 bucket name to generate pre-signed URLs for
* `S3_BUCKET_REGION=<value>` - AWS S3 bucket region to generate pre-signed URLs for (Recommended value is `us-east-1`)

### Configuring node.js example
Before running the `npm run start:nodejs-custom`, you need to install npm dependencies: `npm i`.

#### Running node.js example
After the configuration is done, you can run this script with `npm run start:nodejs-custom`.

### Configuring python3 example
Before running the `npm run start:python-custom`, you would want to configure `virtualenv` for a python project:
1. Make sure you have python3 installed
2. Run `python3 -m venv demoenv` in the root directory of the demo project. This will create local virtual env for this project.
3. Run `source demoenv/bin/activate` from the root directory. This will make current virtual env an active virtual env, preventing polluting global dependencies space with this project dependencies.
4. Run `pip install -r requirements.txt` from the root directory. This will install all the project dependencies in the currently active virtual env.

#### Running python3 example
After the configuration of virtual env is completed, you may run the python example script with `npm run start:python-custom`. Running this command instead of running a file directly with `python3 src/using-custom-storage.py` will read env values from `.env` and make them available as ENV vars during script execution. 

### Leia Media Cloud APIs
* `https://api.leiapix.com/api/v1/disparity`
* `https://api.leiapix.com/api/v1/animation`
