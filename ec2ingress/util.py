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
