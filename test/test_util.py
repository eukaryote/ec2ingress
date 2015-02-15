# coding=utf8

from __future__ import unicode_literals

import time

import ec2ingress.util as U
from ec2ingress.compat import Queue


def test_decode_utf8():
    u = 'ΔΕΖΗΘ'
    bs = u.encode('UTF8')
    assert U.decode(bs) == u


def test_decode_iso88591():
    u = '« »'
    bs = u.encode('ISO-8859-1')
    assert bs != u.encode('UTF8')
    assert U.decode(bs) == u


def test_readurl():
    url = 'http://example.com/'
    assert 'Example Domain' in U.readurl(url)


def test_runthreads_no_timeout():
    queue = Queue()

    def go(i):
        queue.put(i)

    args = list(range(0, 10))
    all_completed = U.run_threads(go, args)

    assert all_completed

    results = []
    while not queue.empty():
        results.append(queue.get())
    assert sorted(results) == args


def test_runthreads_timeout():
    queue = Queue()

    wait_on = 5

    def go(i):
        if i == wait_on:
            time.sleep(0.1)
        queue.put(i)

    args = list(range(0, 10))

    all_completed = U.run_threads(go, args, timeout=0.05)

    assert not all_completed

    results = []
    while not queue.empty():
        results.append(queue.get())

    assert sorted(results) == [a for a in args if a != wait_on]
