==========
ec2ingress
==========

ec2ingress is a commandline script to simplify management of EC2 ingress rules
for a particular EC2 security group. The defaults make it especially easy to
restrict SSH access on a security group to just the IP address of the
host that you run the script on, regardless of whether you're behind a NAT
device or not.

For example, to update a security group named `SSH` so that it only allows
SSH access from my current public IP, I run::

    ec2ingress --group-name SSH set

That uses the `ipgetter` library to determine what my current public IP
address is, removes existing ingress rules to port 22 (`--port` defaults to 22),
and then adds a single ingress rule for port 22 from my current IP.

Setup
-----

The boto3 library that `ec2ssh` relies on uses the following configuration
files for your AWS account credentials and default region.

In `~/.aws/credentials`:

    [default]
    aws_access_key_id = YOUR_KEY
    aws_secret_access_key = YOUR_SECRET

In `~/.aws/config` (change to your default region):

    [default]
    region = us-west-1


Python Compatibility
--------------------

ec2ingress works on Python 2.7 or later, including Python 3.
