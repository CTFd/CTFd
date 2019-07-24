from CTFd.utils.humanize.numbers import ordinalize


def test_ordinalize():
    tests = {
        1: "1st",
        2: "2nd",
        3: "3rd",
        4: "4th",
        11: "11th",
        12: "12th",
        13: "13th",
        101: "101st",
        102: "102nd",
        103: "103rd",
        111: "111th",
    }
    for t, v in tests.items():
        assert ordinalize(t) == v
