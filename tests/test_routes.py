from app.routes import get_headings_rows
from app.models import Assignment, Key


def test_get_headings_rows():
    assignments = [
        Assignment(user="mike", key="key1", date_out="20210101"),
        Assignment(user="mike", key="key2", date_out="20210102"),
        Assignment(user="aaron", key="key1", date_out="20210103"),
        Assignment(user="aaron", key="key3", date_out="20210104"),
    ]

    # Test heading_map with k,v pairs
    heading_map = {"user": "User", "key": "Keys Assigned"}

    want_headings = ["User", "Keys Assigned"]
    want_rows = [
        ["mike", "key1"],
        ["mike", "key2"],
        ["aaron", "key1"],
        ["aaron", "key3"],
    ]
    got = get_headings_rows(assignments, heading_map)

    assert (want_headings, want_rows) == got

    # Test heading_map with None for a value
    heading_map = {"user": "User", "key": None}
    want_headings = ["User", "key"]

    got = get_headings_rows(assignments, heading_map)
    assert (want_headings, want_rows) == got

    # Test heading_map is tuple
    heading_map = ("user", "key")
    want_headings = ["user", "key"]

    got = get_headings_rows(assignments, heading_map)
    assert (want_headings, want_rows) == got

    # Test no heading_map
    want_headings = ["user", "key", "date_out"]
    want_rows = [
        ["mike", "key1", "20210101"],
        ["mike", "key2", "20210102"],
        ["aaron", "key1", "20210103"],
        ["aaron", "key3", "20210104"],
    ]

    got = get_headings_rows(assignments)
    assert (want_headings, want_rows) == got
