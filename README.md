# Leia Media Cloud REST API Demo app

This repo contains examples of backend integration with Media Cloud REST API.

Please refer to `src/index.ts` and `src/index.py` files to see code integration examples for each corresponding language.

## Configuration
In order to run this script, two sets of credentials are used: 
1. `AWS Access Key ID` and `AWS Secret Access Key` (so that script can generate AWS S3 pre-signed URLs)
2. `Leia Backend Client ID` and `Leia Backend Client Secret` - to access Leia Media Cloud API. Can be acquired in Leia Account API Section.

### Configure AWS CLI (required for both examples)
These scripts are intended for demonstration purposes only. Because of this, they rely on a [configured AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html#cli-configure-files-methods) so that they can be run from a CLI. After this is done, the `@aws-sdk/credential-provider-node` and `boto3` packages used in these scripts will handle auth with AWS.

Real production integration should be done with secrets properly managed via CI/CD, and accessed in application environment instead. 

### Configuring Leia Media Cloud credentials and other parameters (required for both examples)
Rename `.env.tmpl` into `.env`. Put next env vars in `.env` at root folder. The package.json `start:<platform>` script will read these values to be used in the script.
* `ORIGINAL_IMAGE_URL=<image_url>` - URL of the image to convert to animation or to generate disparity map from
* `BACKEND_CLIENT_ID=<value>` - Leia Backend Client ID
* `BACKEND_CLIENT_SECRET=<value>` - Leia Backend Client Secret
* `S3_BUCKET_NAME=<value>` - AWS S3 bucket name to generate pre-signed URLs for
* `S3_BUCKET_REGION=<value>` - AWS S3 bucket region to generate pre-signed URLs for (Recommended value is `us-east-1`)

### Configuring node.js example
Before running the `npm run start:nodejs`, you need to install npm dependencies: `npm i`.

#### Running node.js example
After the configuration is done, you can run this script with `npm run start:nodejs`.

### Configuring python3 example
Before running the `npm run start:python`, you would want to configure `virtualenv` for a python project:
1. Make sure you have python3 installed
2. Run `python3 -m venv demoenv` in the root directory of the demo project. This will create local virtual env for this project.
3. Run `source demoenv/bin/activate` from the root directory. This will make current virtual env an active virtual env, preventing polluting global dependencies space with this project dependencies.
4. Run `pip install -r requirements.txt` from the root directory. This will install all the project dependencies in the currently active virtual env.

#### Running python3 example
After the configuration of virtual env is completed, you may run the python example script with `npm run start:python`. Running this command instead of running a file directly with `python3 src/index.py` will read env values from `.env` and make them available as ENV vars during script execution.  

### Leia Media Cloud APIs
* `https://api.leiapix.com/api/v1/disparity`
* `https://api.leiapix.com/api/v1/animation`
