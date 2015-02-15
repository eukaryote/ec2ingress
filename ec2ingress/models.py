import boto3

import ec2ingress as EI
import ec2ingress.util as util
from ec2ingress.log import logger


def fetch_security_group(group_id=None, group_name=None):
    util.validate_id_or_name(**locals())
    for sg in boto3.resource('ec2').security_groups.iterator():
        # TODO: are group names unique, as we're implicitly assuming?
        if group_id and sg.group_id == group_id:
            return sg
        elif group_name and sg.group_name == group_name:
            return sg


class Ingress(object):

    """
    Wrapper around an EC2 security group, exposing minimal API needed by lib.
    """

    def __init__(self, group_name=None, group_id=None):
        self.group_name = group_name
        self.group_id = group_id
        util.validate_id_or_name(**self.kw)
        self.load()

    @property
    def kw(self):
        if self.group_id:
            return {'group_id': self.group_id}
        else:
            return {'group_name': self.group_name}

    def load(self):
        self.sg = fetch_security_group(**self.kw)
        if self.sg is None:
            msg = "No security group found for: %s" % (self.kw,)
            raise EI.NoSecurityGroupError(msg)
        else:
            logger.debug("found security group: %s", self.sg)

    def get(self, port=22):
        target = ('tcp', port, port)
        for rule in self.sg.ip_permissions:
            if util.pluck(rule, 'IpProtocol', 'FromPort', 'ToPort') == target:
                return rule  # only one match possible

    def set(self, ip, port=22):
        ip = util.to_cidr(ip)
        # if there is only one existing rule for the target port and it is
        # for the ip we would set, then we don't need to do anything
        rule = self.get(port=port)
        if rule:
            ip_ranges = rule.get('IpRanges', [])
            if len(ip_ranges) == 1 and ip_ranges[0].get('CidrIp') == ip:
                logger.debug('no ingress changes needed for ip=%s, port=%s',
                             ip, port)
                return
        # otherwise, either there are no rules or multiple rules or a single
        # rule that doesn't match the rule we're adding, so we need to remove
        # all the existing rules and then add just the target rule
        self.remove(port=port)
        self.add(ip, port=port)

    def add(self, ip, port=22):
        ip = util.to_cidr(ip)
        kw = {
            'IpProtocol': 'tcp',
            'CidrIp': ip,
            'FromPort': port,
            'ToPort': port
        }
        logger.debug('authorize_ingress request: %s', kw)
        res = self.sg.authorize_ingress(**kw)
        logger.debug('authorize_ingress result: %s', res)

    def remove(self, ip=None, port=22):
        for rule in self.sg.ip_permissions:
            sig = util.pluck(rule, 'IpProtocol', 'FromPort', 'ToPort')
            if sig != ('tcp', port, port):
                continue
            if 'IpRanges' in rule:
                for d in rule['IpRanges']:
                    if 'CidrIp' in d and (ip is None or d['CidrIp'] == ip):
                        kw = {
                            'IpProtocol': sig[0],
                            'FromPort': sig[1],
                            'ToPort': sig[2],
                            'CidrIp': d['CidrIp']
                        }
                        logger.debug('revoke_ingress request: %s', kw)
                        res = self.sg.revoke_ingress(
                            IpProtocol=sig[0], FromPort=sig[1],
                            ToPort=sig[2], CidrIp=d['CidrIp']
                        )
                        logger.debug('revoke_ingress result: %s', res)
