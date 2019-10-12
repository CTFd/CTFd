from CTFd.utils.formatters import format


def test_safe_format():
    assert format("Message from {ctf_name}", ctf_name="CTF") == "Message from CTF"
    assert format("Message from {{ ctf_name }}", ctf_name="CTF") == "Message from CTF"
    assert format("{{ ctf_name }} {{ctf_name}}", ctf_name="CTF") == "CTF CTF"
    assert (
        format("{{ ctf_name }} {{ctf_name}} {asdf}", ctf_name="CTF") == "CTF CTF {asdf}"
    )
