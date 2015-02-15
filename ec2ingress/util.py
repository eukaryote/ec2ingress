import contextlib
from threading import Thread

from ec2ingress.compat import urlopen


def pluck(d, *keys):
    return tuple(d[k] for k in keys)


def to_cidr(ipaddr):
    if '/' not in ipaddr:
        ipaddr += '/32'
    return ipaddr


def validate_id_or_name(group_id=None, group_name=None):
    if not (bool(group_name) ^ bool(group_id)):
        msg = "exactly one of `group_name` or `group_id` is required"
        raise ValueError(msg)


def run_threads(target, args, timeout=None):
    """
    Run callable `target` in a thread with each arg in `args`.

    If `timeout` is given, it should be a float representing the maximum
    number of seconds to wait for each thread to complete. If not given,
    wait indefinitely.

    Returns False if a timeout is given and not all threads completed before
    their timeout expired, and True otherwise.
    """
    ts = [Thread(target=target, args=(arg,)) for arg in args]
    for t in ts:
        t.start()
    for t in ts:
        t.join(timeout)
    return not(any(t.isAlive() for t in ts))


def decode(bs):
    """
    Convert the given byte string to a unicode value by trying to decode from
    UTF8 and if that fails from ISO-8859-1, raising a `UnicodeDecodeError`
    if unable to decode from either of those codecs.
    """
    try:
        return bs.decode('UTF8')
    except UnicodeDecodeError:
        return bs.decode('ISO-8859-1')


def readurl(url):
    """
    Read the contents at the given `url`, returning a unicode string.
    """
    with contextlib.closing(urlopen(url)) as conn:
        return decode(conn.read())
