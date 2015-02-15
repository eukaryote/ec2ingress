from ec2ingress.ip import extract_ipv4


def test_extract_ipv4_plain():
    for ip in ('202.231.191.124', '101.142.245.239'):
        assert extract_ipv4(ip) == ip


def test_extract_ipv4_small():
    for ip in ('9.1.4.0', '3.201.4.189', '99.0.4.7'):
        assert extract_ipv4(ip) == ip


def test_extract_ipv4_leading_zeros():
    for ip in ('02.009.04.0', '145.01.244.8'):
        assert extract_ipv4(ip) == ip


def test_extract_ipv4_invalid():
    for ip in ('', '256.101.128.144', '1110.234.215.123', '232.189.121'):
        assert extract_ipv4(ip) is None
