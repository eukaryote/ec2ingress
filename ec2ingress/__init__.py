# set up logger, defaulting to WARN for third party and INFO for ec2ingress
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.getLogger('boto3').setLevel(logging.WARN)
logging.getLogger('botocore').setLevel(logging.WARN)
del logging

__version_info__ = (0, 1, 0)
__version__ = '.'.join(map(str, __version_info__))


class NoSecurityGroupError(Exception):
    pass
