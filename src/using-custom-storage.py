import sys
import os
import uuid
import boto3
from botocore.exceptions import NoCredentialsError
import requests

# print("\n".join(sys.path))
# Reading configuration from environment
if sys.prefix == sys.base_prefix:
    print('Error. You should run application in virtualenv to not pollute global dependencies. Please refer to '
          'README.md for instructions on how to set it up', file=sys.stderr)
    print(f'sys.prefix: {sys.prefix}')
    print(f'sys.base_prefix: {sys.base_prefix}')
    exit(1)

# Get the environment variables
CLIENT_ID = os.getenv('BACKEND_CLIENT_ID')
CLIENT_SECRET = os.getenv('BACKEND_CLIENT_SECRET')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
S3_BUCKET_REGION = os.getenv('S3_BUCKET_REGION')

# Check that they are all set
if not CLIENT_ID or not CLIENT_SECRET:
    print('Error. In order to authenticate against Leia Media Cloud API, you need to provide BACKEND_CLIENT_ID and '
          'BACKEND_CLIENT_SECRET env vars', file=sys.stderr)
    exit(1)

if not S3_BUCKET_NAME or not S3_BUCKET_REGION:
    print('Error. In order to use Leia Media Cloud API, you need to provide S3_BUCKET_NAME and '
          'S3_BUCKET_REGION env vars', file=sys.stderr)
    exit(1)

MEDIA_CLOUD_REST_API_BASE_URL = 'https://api.leiapix.com'
LEIA_LOGIN_OPENID_TOKEN_URL = 'https://auth.leialoft.com/auth/realms/leialoft/protocol/openid-connect/token'


DEFAULT_ORIGINAL_IMAGE_URL = 'https://images.pexels.com/photos/38771/pexels-photo-38771.jpeg?auto=compress&cs' \
                             '=tinysrgb&w=1260&h=750&dpr=1'
ORIGINAL_IMAGE_URL = os.getenv('ORIGINAL_IMAGE_URL', DEFAULT_ORIGINAL_IMAGE_URL)
ORIGINAL_IMAGE_URL = DEFAULT_ORIGINAL_IMAGE_URL if ORIGINAL_IMAGE_URL == '' else ORIGINAL_IMAGE_URL


TWENTY_FOUR_HRS_IN_S = 24 * 60 * 60
THREE_MIN_IN_S = 3 * 60

S3_DISPARITY_PATH = 'public/leiapixcloud/disparity.jpg'
S3_MP4_PATH = 'public/leiapixcloud/animation.mp4'

# Initiate the s3 client
s3 = boto3.client('s3', region_name=S3_BUCKET_REGION)


def get_presigned_url(bucket, key, method):
    try:
        return s3.generate_presigned_url(ClientMethod=method,
                                         Params={'Bucket': bucket, 'Key': key},
                                         ExpiresIn=TWENTY_FOUR_HRS_IN_S)
    except NoCredentialsError:
        print('Error. No AWS credentials found', file=sys.stderr)
        return None


try:
    """
    * First, we need to authenticate against Leia Login with Client
    * credentials and acquire a temporary access token.
    * 
    * You can generate ClientID and Client Secret in Leia Login API Section.
    """
    print('Acquiring access token from LeiaLogin...')
    token_response = requests.post(LEIA_LOGIN_OPENID_TOKEN_URL, data={
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }).json()
    access_token = token_response['access_token']
    print(f'\nLeiaLogin AccessToken acquired: {access_token}')

    """
    * Now that we have an oidc access token we can call the API. First, let's
    * generate a disparity map for our image.
    """

    # We start with preparing a correlationId. This might be an internal
    # ID which you use in your system for this image/entity represented
    # by the image/etc, or, as we do now, we can just generate new UUIDv4.
    correlation_id = str(uuid.uuid4())

    # You probably want to store the image somewhere. You need to provide
    # an uploadable URL where Leia Media Cloud API will PUT the result of a
    # call. Here we use AWS S3 pre-signed URLs as uploadable url. The url
    # needs to support HTTP PUT command.
    put_disparity_presigned_url = get_presigned_url(
        S3_BUCKET_NAME,
        S3_DISPARITY_PATH,
        'put_object'
    )

    print(f'\nGenerating Disparity: {correlation_id}...')

    # Now we're ready to call the API. We provide only required parameters: a
    # correlationId, URL of the image for which we want to generate
    # disparity map, and the result url where disparity map will be uploaded.
    # You can find all available parameters in the documentation on
    # https://cloud.leiapix.com
    response = requests.post(
        f'{MEDIA_CLOUD_REST_API_BASE_URL}/api/v1/disparity',
        headers={
            'Authorization': f'Bearer {access_token}'
        },
        json={
            'correlationId': correlation_id,
            'inputImageUrl': ORIGINAL_IMAGE_URL,
            'resultPresignedUrl': put_disparity_presigned_url
        },
        timeout=THREE_MIN_IN_S
    )
    if not response.status_code == 201:
        raise Exception(f"Request returned with an error {response.status_code}. "
                        f"The full response is: {response.content}")

    # At this point, the disparity map should be uploaded to the upload
    # url. We omit the error handling in this example for simplicity, but
    # you should always check for a returned status & errors from the API
    # in real code.

    # To demonstrate that the upload was successful, we generate a GET
    # presigned URL to output it to be used. This URL will also be used
    # later in the script as an input for an animation call - but it is
    # optional if the disparity map is the only result you need.
    get_disparity_presigned_url = get_presigned_url(
        S3_BUCKET_NAME,
        S3_DISPARITY_PATH,
        'get_object'
    )

    print(f'\nDisparity has been uploaded to specified AWS S3 bucket. '
          f'To view it, use this GET URL: {get_disparity_presigned_url}')

    # If you're interested not only in a disparity map, but you also want
    # to generate an animation, you would need to make another request to
    # the service. The steps are very similar to how we called a disparity
    # map endpoint: first we acquire correlationId...
    correlation_id = str(uuid.uuid4())

    # ...then we prepare an uploadable url...
    put_mp4_presigned_url = get_presigned_url(
        S3_BUCKET_NAME,
        S3_MP4_PATH,
        'put_object'
    )

    print(f'\nGenerating mp4 animation: {correlation_id}...')

    # ...and we make a request. This time we need four required inputs: a
    # correlationId; original image we want to animate (which was used for
    # disparity map generation); the downloadable URL for a disparity map
    # from previous step (this URL needs to support HTTP GET verb); and an
    # uploadable url for the result animation. You can find all available
    # parameters in the documentation on https://cloud.leiapix.com
    response = requests.post(
        f'{MEDIA_CLOUD_REST_API_BASE_URL}/api/v1/animation',
        headers={
            'Authorization': f'Bearer {access_token}'
        },
        json={
            'correlationId': correlation_id,
            'inputImageUrl': ORIGINAL_IMAGE_URL,
            'inputDisparityUrl': get_disparity_presigned_url,
            'resultPresignedUrl': put_mp4_presigned_url,
            'animationLength': 5
        },
        timeout=THREE_MIN_IN_S
    )
    if not response.status_code == 201:
        raise Exception(f"Request returned with an error {response.status_code}. "
                        f"The full response is: {response.content}")

    # At this point, the video should be uploaded to a specified upload URL.

    # This step is optional. We generate a presigned url to download the
    # results of the animation call for convenience.
    get_mp4_presigned_url = get_presigned_url(
        S3_BUCKET_NAME,
        S3_MP4_PATH,
        'get_object'
    )

    print(f'\nMP4 Animation has been uploaded to specified AWS S3 bucket. '
          f'To download, please use this GET URL: {get_mp4_presigned_url}')

except Exception as e:
    print('Error. Unhandled exception: ' + str(e), file=sys.stderr)
