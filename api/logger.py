import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# * INFO: https://github.com/googleapis/google-api-python-client/issues/299#issuecomment-255793971
# There is a typo in the GitHub comment that we fix in the code below.
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
