import logging
import ec2ingress

formatter = logging.Formatter('%(asctime)s %(name)-12s: '
                              '%(levelname)-8s %(message)s')
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger = logging.getLogger(ec2ingress.__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logging.getLogger('boto3').setLevel(logging.WARN)
logging.getLogger('boto3').addHandler(handler)
logging.getLogger('botocore').setLevel(logging.WARN)
logging.getLogger('botocore').addHandler(handler)
del logging, formatter, handler
