import sys
import logging
import argparse
import pprint

import ec2ingress


def get_group(args, exit_on_err=True):
    try:
        return ec2ingress.Ingress(
            group_name=args.group_name,
            group_id=args.group_id,
            vpc_id=args.vpc,
        )
    except ec2ingress.NoSecurityGroupError as err:
        print(err)
        if exit_on_err:
            sys.exit(1)


def show(args):
    group = get_group(args)
    pprint.pprint(group.get())


def _set(args):
    group = get_group(args)
    group.set(args.ip or ec2ingress.myip(), port=args.port)


def add(args):
    group = get_group(args)
    group.add(args.ip or ec2ingress.myip(), port=args.port)


def remove(args):
    group = get_group(args)
    group.remove(ip=args.ip, port=args.port)


def myip(args):
    print('myip args:', args)


def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(description='Control EC2 SSH Access.')

    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument('-v', '--verbose', action='store_true',
                                 help="show verbose output")
    verbosity_group.add_argument('-vv', '--very-verbose', action='store_true',
                                 help="really verbose output, including "
                                      "boto debug info")

    sg_group = parser.add_mutually_exclusive_group(required=True)
    sg_group.add_argument('--group-name', type=str,
                          help="EC2 security group name")
    sg_group.add_argument('--group-id', type=str, help="EC2 security group id")
    parser.add_argument('-V', '--version', action='store_true',
                        help="Show version")

    parser.add_argument('--vpc', type=str,
                        help='VPC ID (only needed if using --group-name '
                             'and there are multiple security groups '
                             'in different VPCs with that name')

    subparsers = parser.add_subparsers(help='available commands')

    ip_arg_help = ('IP (or CIDR address) for ingress rule -- if not given, '
                   'your public IP address will be looked up '
                   'and used as the only IP for ingress')
    port_arg_help = 'ingress PORT (default 22)'
    min_quorum_arg_help = ('Minimum number of IP lookup services that must '
                           'report the same IP when setting or adding '
                           'current external IP to security group '
                           'ingress rules')

    # 'set' command and params
    _help = 'set ingress rule for PORT after removing existing rules for PORT'
    parser_set = subparsers.add_parser('set', help=_help)
    parser_set.set_defaults(func=_set)
    parser_set.add_argument('--port', type=int, metavar='PORT',
                            default=22, help=port_arg_help)
    set_ip_group = parser_set.add_mutually_exclusive_group(required=False)
    set_ip_group.add_argument('--ip', metavar='IP', help=ip_arg_help)
    set_ip_group.add_argument('--min-quorum', type=int, default=3,
                              help=min_quorum_arg_help)

    # 'add' command and params
    _help = 'add additional ingress rule for PORT'
    parser_add = subparsers.add_parser('add', help=_help)
    parser_add.set_defaults(func=add)
    parser_add.add_argument('--port', type=int, metavar='PORT',
                            default=22, help=port_arg_help)
    add_ip_group = parser_add.add_mutually_exclusive_group(required=False)
    add_ip_group.add_argument('--ip', metavar='IP', help=ip_arg_help)
    add_ip_group.add_argument('--min-quorum', type=int, default=3,
                              help=min_quorum_arg_help)

    # 'show' command and params
    parser_show = subparsers.add_parser('show', help='show help')
    parser_show.set_defaults(func=show)
    parser_show.add_argument('--port', type=int, metavar='PORT',
                             default=22, help=port_arg_help)

    # 'remove' command and params
    parser_remove = subparsers.add_parser('remove', help='remove help')
    parser_remove.set_defaults(func=remove)
    parser_remove.add_argument('--port', type=int, metavar='PORT',
                               default=22, help=port_arg_help)
    _help = ('IP (or CIDR address) to remove ingress rule for -- if not '
             'given, all existing ingress rules for the PORT will be removed')
    parser_remove.add_argument('--ip', metavar='IP', help=_help)

    # 'myip' command and params
    parser_myip = subparsers.add_parser('myip', help='show my IP lookup info')
    parser_myip.set_defaults(func=myip)

    args = parser.parse_args()

    if args.version:
        print("%s %s" % (ec2ingress.__name__, ec2ingress.__version__))
        sys.exit(0)

    if args.verbose or args.very_verbose:
        ec2ingress.logger.setLevel(logging.DEBUG)

    if args.very_verbose:
        logging.getLogger('boto3').setLevel(logging.DEBUG)
        logging.getLogger('botocore').setLevel(logging.DEBUG)

    args.func(args)


if __name__ == '__main__':
    main()
