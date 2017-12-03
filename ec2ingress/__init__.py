# coding=utf8

"""
Manage EC2 security group ingress rules.
"""

from collections import Counter, namedtuple
import contextlib
import logging
import re
from threading import Thread
import time
import sys

import six
from six.moves.queue import Queue
from six.moves.urllib.request import urlopen

import boto3

__version_info__ = (0, 2, 0)
__version__ = '.'.join(map(str, __version_info__))

# Set up logger (WARN level for noisy boto packages, and INFO for other)
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
logging.getLogger('boto3').setLevel(logging.WARN)
logging.getLogger('botocore').setLevel(logging.WARN)

# URLs of https sites that include the IP address
# of the requester in the response.
IP_LOOKUP_URLS = (
    'https://wtfismyip.com/text',
    'https://api.ipify.org?format=text',
    'https://4.ifcfg.me/ip',
    'https://ifconfig.co/ip',
    'https://icanhazip.com',
)

# Pattern for matching an ipv4 address and extracting from lookup response.
IP_PAT = re.compile(r'\b({octet}\.{octet}\.{octet}\.{octet})\b'.format(
    octet='(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
))

# A successful response of an IP lookup, including the original
# URL that was requested, the IP address extracted from the
# result, and how long the request-response took in milliseconds.
Result = namedtuple('Result', 'url,ip,time')


class NoSecurityGroupError(Exception):
    """Unable to resolve security group based on name or id."""


class IPLookupError(Exception):
    """Failed to lookup IP."""


def decode(value):
    """
    Decode `value`(`bytes`), trying UTF8 and ISO-8859-1, in that order.

    Raises `UnicodeDecodeError` if unable to decode.
    """
    try:
        return value.decode('UTF8')
    except UnicodeDecodeError:
        pass
    return value.decode('ISO-8859-1')


def readurl(url, parse_data=decode):
    """
    Read the contents at the given `url`, using `parse_data` to parse result.
    """
    if not url.startswith('https://'):
        raise ValueError('non-https urls not supported: %s' % (url,))
    with contextlib.closing(urlopen(url)) as conn:
        data = conn.read()
    return parse_data(data)


def extract_ipv4(text):
    """
    Extract an IPv4 address from `text`, returning the first one found or None.
    """
    match = IP_PAT.search(text)
    return match.group(1) if match else None


def lookup_my_ip(urls, results):
    """
    Determine our external IP addresss, getting one url from the `urls`
    Queue, appending a `Result` to the results list on success and signalling
    completion via `urls.task_done()` (whether successful or not).

    If not able to determine the IP, `results` will remain unchanged.
    """
    start = time.time()
    url = urls.get()
    try:
        try:
            output = readurl(url)
        except Exception as exc:
            six.print_('Error doing lookup for url %s:' % url, file=sys.stderr)
            six.print_(exc, file=sys.stderr)
        else:
            ipaddr = extract_ipv4(output)
            if ipaddr:
                elapsed_ms = int(1000 * (time.time() - start))
                result = Result(url, ipaddr, elapsed_ms)
                results.append(result)
                LOG.debug('%s reports my IP: %s [%s ms]', *result)
            else:
                six.print_('Failed to extract IP from URL %s result:' % url,
                           file=sys.stderr)
                six.print_(output)
    finally:
        urls.task_done()


def get_ip_info(urls=IP_LOOKUP_URLS):
    """
    Get IP info using provided URLs of IP lookup sites.

    Returns a list of `Result` tuples with (url, ip, time).
    """
    jobs = Queue()
    results = []

    for url in urls:
        jobs.put(url)

    for url in urls:
        thread = Thread(target=lookup_my_ip, args=(jobs, results))
        thread.daemon = True
        thread.start()

    jobs.join()
    return results


def myip(min_quorum=3):
    """
    Get the current IP address by checking all the `myip_urls` concurrently
    and returning the most common response after all have completed.

    The `min_quorum` parameter is the minimum number of sources that must
    agree on the IP. Raises `IPLookupError` if the most common IP
    was reported by fewer than that number.
    """
    counts = Counter()
    for result in get_ip_info():
        counts[result.ip] += 1
    ipaddr, count = counts.most_common(1)[0]

    if count < min_quorum:
        msg = ("Failed to determine own IP: most common was %s with count "
               "of %s, but need count of at least %s to accept.")
        raise IPLookupError(msg % (ipaddr, count, min_quorum))

    return ipaddr


class Ingress(object):

    """
    Wrapper around an EC2 security group, exposing minimal API needed by lib.
    """

    def __init__(self, group_name=None, group_id=None, vpc_id=None):
        if not bool(group_name) ^ bool(group_id):
            raise ValueError("`group_name` or `group_id` required (exactly 1)")
        self.group_name = group_name
        self.group_id = group_id
        self.vpc_id = vpc_id
        self.load()

    @property
    def kw(self):
        res = {}
        if self.vpc_id:
            res['vpc_id'] = self.vpc_id
        if self.group_id:
            res['group_id'] = self.group_id
        else:
            res['group_name'] = self.group_name

    def find_security_group(self):
        """Get boto3 security group object."""
        for sg in boto3.resource('ec2').security_groups.iterator():
            # if vpc_id was provided, skip all rules that aren't for that VPC
            if self.vpc_id and sg.vpc_id != self.vpc_id:
                continue
            if self.group_id and sg.group_id == self.group_id:
                return sg
            if self.group_name and sg.group_name == self.group_name:
                return sg

    def load(self):
        self.sg = self.find_security_group()
        if self.sg is None:
            msg = "No security group found for: %s" % (self.kw,)
            raise NoSecurityGroupError(msg)
        else:
            LOG.debug("found security group: %s", self.sg)

    def get(self, port=22):
        target = ('tcp', port, port)
        for rule in self.sg.ip_permissions:
            if (rule['IpProtocol'], rule['FromPort'], rule['ToPort']) == target:
                return rule  # only one match possible

    def set(self, ip, port=22):
        if '/' not in ip:
            ip += '/32'

        # if there is only one existing rule for the target port and it is
        # for the ip we would set, then we don't need to do anything
        rule = self.get(port=port)
        if rule:
            ip_ranges = rule.get('IpRanges', [])
            if len(ip_ranges) == 1 and ip_ranges[0].get('CidrIp') == ip:
                LOG.debug('no ingress changes needed for ip=%s, port=%s',
                          ip, port)
                return
        # otherwise, either there are no rules or multiple rules or a single
        # rule that doesn't match the rule we're adding, so we need to remove
        # all the existing rules and then add just the target rule
        self.remove(port=port)
        self.add(ip, port=port)

    def add(self, ip, port=22):
        if '/' not in ip:
            ip += '/32'
        kw = {
            'IpProtocol': 'tcp',
            'CidrIp': ip,
            'FromPort': port,
            'ToPort': port
        }
        LOG.debug('authorize_ingress request: %s', kw)
        res = self.sg.authorize_ingress(**kw)
        LOG.debug('authorize_ingress result: %s', res)

    def remove(self, ip=None, port=22):
        for rule in self.sg.ip_permissions:
            sig = rule['IpProtocol'], rule['FromPort'], rule['ToPort']
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
                        LOG.debug('revoke_ingress request: %s', kw)
                        res = self.sg.revoke_ingress(
                            IpProtocol=sig[0], FromPort=sig[1],
                            ToPort=sig[2], CidrIp=d['CidrIp']
                        )
                        LOG.debug('revoke_ingress result: %s', res)
