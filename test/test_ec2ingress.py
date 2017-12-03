# coding=utf8

from __future__ import unicode_literals

import pytest

import ec2ingress as EI


# Example IDs from AWS Docs.
VPC_ID = 'vpc-18ac277d'
GROUP_ID = 'sg-51530134'
GROUP_NAME = 'MySecurityGroup'


def test_extract_ipv4_plain():
    for ip in ('202.231.191.124', '101.142.245.239'):
        assert EI.extract_ipv4(ip) == ip


def test_extract_ipv4_small():
    for ip in ('9.1.4.0', '3.201.4.189', '99.0.4.7'):
        assert EI.extract_ipv4(ip) == ip


def test_extract_ipv4_leading_zeros():
    for ip in ('02.009.04.0', '145.01.244.8'):
        assert EI.extract_ipv4(ip) == ip


def test_extract_ipv4_invalid():
    for ip in ('', '256.101.128.144', '1110.234.215.123', '232.189.121'):
        assert EI.extract_ipv4(ip) is None


def test_decode_utf8():
    u = 'ΔΕΖΗΘ'
    bs = u.encode('UTF8')
    assert EI.decode(bs) == u


def test_decode_iso88591():
    u = '« »'
    bs = u.encode('ISO-8859-1')
    assert bs != u.encode('UTF8')
    assert EI.decode(bs) == u


def test_readurl_https():
    url = 'https://example.com/'
    assert 'Example Domain' in EI.readurl(url)


def test_readurl_http():
    with pytest.raises(ValueError) as err:
        EI.readurl('http://example.com')
    assert str(err.value).startswith('non-https urls not supported')
