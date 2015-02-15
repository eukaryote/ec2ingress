import contextlib

import ec2ingress.compat as compat


def test_queue():
    q = compat.Queue()
    q.put(1)
    assert not q.empty()
    assert q.get() == 1
    assert q.empty()


def test_urlopen():
    with contextlib.closing(compat.urlopen('http://example.com/')) as conn:
        assert conn.read()
