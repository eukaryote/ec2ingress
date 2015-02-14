
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
