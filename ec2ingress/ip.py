import re
from collections import Counter

try:
    from Queue import Queue
except ImportError:
    from queue import Queue  # py3

from ec2ingress import logger
import ec2ingress.util as util

myip_urls = (
    'https://wtfismyip.com/text',
    'https://api.ipify.org?format=text',
    'https://www.telize.com/ip',
    'https://icanhazip.com'
)

octet_regex = '(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
ip_regex = r'\b((?:%s\.){3}%s)\b' % (octet_regex, octet_regex)


def extract_ipv4(text):
    """
    Extract an IPv4 address from `text`, returning the first one found or None.
    """
    m = re.search(ip_regex, text)
    if m:
        return m.group(1)


def myip():
    """
    Get the current IP address by checking all the `myip_urls` concurrently
    and returning the most common response after all have completed.
    """
    q = Queue()

    def lookup(url):
        ip = extract_ipv4(util.readurl(url))
        logger.debug('%s reports my ip: %s', url, ip)
        q.put(ip)

    util.run_threads(lookup, myip_urls)

    c = Counter()
    while not q.empty():
        c[q.get()] += 1
    ip, count = c.most_common(1)[0]
    assert count >= 3  # winner should be reported by at least 3 hosts
    return ip
