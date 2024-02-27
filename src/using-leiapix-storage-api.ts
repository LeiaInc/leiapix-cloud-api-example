import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

/**
 * Reading configuration from environment
 */

const CLIENT_ID = process.env.BACKEND_CLIENT_ID;
const CLIENT_SECRET = process.env.BACKEND_CLIENT_SECRET;

if (!CLIENT_ID || !CLIENT_SECRET) {
  console.error('Error. In order to authenticate against Leia Media Cloud' +
    ' API, you need to provide BACKEND_CLIENT_ID and BACKEND_CLIENT_SECRET ' +
    'env vars');
  process.exit(1);
}

/**
 * Needs to be configured before running a script;
 */
const MEDIA_CLOUD_REST_API_BASE_URL = 'https://api.leiapix.com';
const LEIA_LOGIN_OPENID_TOKEN_URL = 'https://auth.leialoft.com/auth/realms/leialoft/protocol/openid-connect/token';

const ORIGINAL_IMAGE_URL = (process.env.ORIGINAL_IMAGE_URL && process.env.ORIGINAL_IMAGE_URL !== '')
  ? process.env.ORIGINAL_IMAGE_URL
  : 'https://images.pexels.com/photos/38771/pexels-photo-38771.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1';

const TWENTY_FOUR_HRS_IN_S = 24 * 60 * 60;
const THREE_MIN_IN_MS = 3 * 60 * 1000;

(async () => {
  try {

    /**
     * First, we need to authenticate against Leia Login with Client
     * credentials and acquire a temporary access token.
     *
     * You can generate ClientID and Client Secret in Leia Login API Section.
     */

    console.log('Acquiring access token from LeiaLogin...');

    const tokenResponse = await axios.post(LEIA_LOGIN_OPENID_TOKEN_URL, {
      client_id: CLIENT_ID,
      client_secret: CLIENT_SECRET,
      grant_type: 'client_credentials',
    }, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      timeout: THREE_MIN_IN_MS,
    });

    const accessToken = tokenResponse.data.access_token;

    console.log(`\nLeiaLogin AccessToken acquired: ${accessToken}`);

    /**
     * Now that we have an oidc access token we can call the API. First, let's
     * generate a disparity map for our image.
     */

    // We start with preparing a correlationId. This might be an internal
    // ID which you use in your system for this image/entity represented
    // by the image/etc, or, as we do now, we can just generate new UUIDv4.
    let correlationId = uuidv4();

    // Before you'll to be able to create an animation, you want to generate a
    // disparity map for your image and store it somewhere. For the next step,
    // you'll need to provide an uploadable URL where Leia Media Cloud API
    // will PUT the result of the call. Here we use the Leia Storage API to
    // generate the upload URL for the temporary storage of the result.
    let fileName = "disparity.jpg";
    let mediaType = "image/jpeg";
    let disparityUploadUrlResult = await axios.get(`${MEDIA_CLOUD_REST_API_BASE_URL}/api/v1/get-upload-url?correlationId=${correlationId}&fileName=${fileName}&mediaType=${mediaType}`, {
      headers: {
        Authorization: `Bearer ${accessToken}`
      },
      timeout: THREE_MIN_IN_MS,
    });

    const putDisparityPresignedUrl = disparityUploadUrlResult.data.url;

    console.log(`\nGenerating Disparity: ${correlationId}...`);

    // Now we're ready to call the API. We provide only required parameters: a
    // correlationId, URL of the image for which we want to generate
    // disparity map, and the result url where disparity map will be
    // uploaded. You can find all available parameters in the documentation
    // on https://cloud.leiapix.com
    let disparityGenerationResult = await axios.post(`${MEDIA_CLOUD_REST_API_BASE_URL}/api/v1/disparity`, {
      correlationId,
      inputImageUrl: ORIGINAL_IMAGE_URL,
      resultPresignedUrl: putDisparityPresignedUrl
    }, {
      headers: {
        Authorization: `Bearer ${accessToken}`
      },
      timeout: THREE_MIN_IN_MS,
    });

    // At this point, the disparity map should be uploaded to the upload
    // url. We omit the error handling in this example for simplicity, but
    // you should always check for a returned status & errors from the API
    // in real code.

    // The result of the call contains a GET pre-signed URL to download the
    // resulting disparity image:

    const getDisparityPresignedUrl = disparityGenerationResult.data.resultPresignedUrl;

    console.log('\nDisparity has been uploaded to the temporary storage.' +
      `To view it, use this GET URL: ${getDisparityPresignedUrl}`);

    // If you're interested not only in a disparity map, but you also want
    // to generate an animation, you would need to make another request to
    // the service. The steps are very similar to how we called a disparity
    // map endpoint: first we acquire correlationId...
    correlationId = uuidv4();

    // ...then we prepare an uploadable url...
    fileName = "animation.mp4";
    mediaType = "video/mp4";
    let animationUploadUrlResult = await axios.get(`${MEDIA_CLOUD_REST_API_BASE_URL}/api/v1/get-upload-url?correlationId=${correlationId}&fileName=${fileName}&mediaType=${mediaType}`, {
      headers: {
        Authorization: `Bearer ${accessToken}`
      },
      timeout: THREE_MIN_IN_MS,
    });
    const putMP4PresignedUrl = animationUploadUrlResult.data.url;

    console.log(`\nGenerating mp4 animation: ${correlationId}...`);

    // ...and we make a request. This time we need four required inputs: a
    // correlationId; original image we want to animate (which was used for
    // disparity map generation); the pre-signed PUT URL for a disparity map
    // from previous step (this URL needs to support HTTP PUT verb, so use the
    // one that was used to upload the disparity result); and an uploadable url
    // for the result animation. You can find all available parameters in the
    // documentation on https://cloud.leiapix.com
    let animationGenerationResult = await axios.post(`${MEDIA_CLOUD_REST_API_BASE_URL}/api/v1/animation`, {
      correlationId,
      inputImageUrl: ORIGINAL_IMAGE_URL,
      inputDisparityUrl: putDisparityPresignedUrl,
      resultPresignedUrl: putMP4PresignedUrl,
      animationLength: 5
    }, {
      headers: {
        Authorization: `Bearer ${accessToken}`
      },
      timeout: THREE_MIN_IN_MS,
    });

    // At this point, the video should be uploaded to a specified upload URL.
    // The resulting file is accessible via the pre-signed GET URL, that you
    // can find included in the response to the animation request:
    const getMP4PresignedUrl = animationGenerationResult.data.resultPresignedUrl;
    // Please note that the pre-signed GET URL has a relatively short
    // expiration period, so make sure to download the file as soon as possible.

    console.log('\nMP4 Animation has been uploaded to the temporary storage.' +
      `To download, please use this GET URL:: ${getMP4PresignedUrl}`);

  } catch (e: any) {
    if (e.hasOwnProperty('message') || e.hasOwnProperty('response')) {
      console.error(`Error. Unhandled exception: ${JSON.stringify(e.message)}`);
      console.error(`Error body: ${JSON.stringify(e.response?.data)}`);
    } else {
      console.error(`Error. Unhandled exception: ${JSON.stringify(e)}`);
    }
  }
})();
