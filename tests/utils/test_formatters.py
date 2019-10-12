from CTFd.utils.formatters import safe_format


def test_safe_format():
    assert safe_format("Message from {ctf_name}", ctf_name="CTF") == "Message from CTF"
    assert (
        safe_format("Message from {{ ctf_name }}", ctf_name="CTF") == "Message from CTF"
    )
    assert safe_format("{{ ctf_name }} {{ctf_name}}", ctf_name="CTF") == "CTF CTF"
    assert (
        safe_format("{ ctf_name } {ctf_name} {asdf}", ctf_name="CTF")
        == "CTF CTF {asdf}"
    )
