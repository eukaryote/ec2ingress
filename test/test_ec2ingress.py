import re

import ec2ssh as E


def test_version():
    assert re.match('\d+(\.\d+){2}', E.__version__)
