import common


def test_CommonJsd():
    assert common.jsd({"a": "b"}) == common.jsd(a="b")
