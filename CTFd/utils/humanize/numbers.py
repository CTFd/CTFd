def ordinalize(n):
    """
    http://codegolf.stackexchange.com/a/4712
    """
    k = n % 10
    return "%d%s" % (n, "tsnrhtdd"[(n // 10 % 10 != 1) * (k < 4) * k :: 4])
