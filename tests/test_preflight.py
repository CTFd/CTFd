"""deploy/scripts/preflight.py -- the pure evaluators, no network.

The script is not a package; it is loaded from its path so the checks that
gate `make preflight` are pinned by CI like any plugin.
"""
import importlib.util
import pathlib

_PATH = (
    pathlib.Path(__file__).resolve().parents[1] / "deploy" / "scripts" / "preflight.py"
)
_spec = importlib.util.spec_from_file_location("preflight", _PATH)
pf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pf)

GOOD_HEX = "a" * 64
NOW = 1_792_000_000  # 2026-10-14
PRESEL = {
    "start": "1792782000",
    "freeze": "1792969200",
    "end": "1792972800",
}  # ven 19h -> lun 00h (53 h)


def by_name(results):
    return {r.name: r for r in results}


def statuses(results):
    return {r.name: r.status for r in results}


def test_parse_env_keeps_only_key_value_lines():
    env = pf.parse_env("A=1\nweird line\nB=x=y\n_C=\n1BAD=2\n")
    assert env == {"A": "1", "B": "x=y", "_C": ""}


def test_secrets_dev_values_fail_and_never_leak():
    env = {
        "CTF_TEAM_FLAG_SECRET": "test-secret",
        "SECRET_KEY": "",
        "KOTH_HILLS": "[{}]",
        "KOTH_SCORER_SECRET": "local-dev-koth-scorer",
        "MARIADB_PASSWORD": "ctfd",
        "DATABASE_URL": "mysql+pymysql://ctfd:ctfd@db/ctfd",
        "REDIS_URL": "redis://cache:6379",
    }
    res = pf.check_secrets(env)
    st = statuses(res)
    assert st["CTF_TEAM_FLAG_SECRET"] == pf.FAIL
    assert st["SECRET_KEY"] == pf.FAIL
    assert st["KOTH_SCORER_SECRET"] == pf.FAIL
    assert st["MARIADB_PASSWORD"] == pf.FAIL
    assert st["DATABASE_URL"] == pf.FAIL
    assert st["REDIS_URL"] == pf.WARN
    assert pf.exit_code(res) == 1
    for r in res:  # no secret value ever appears in the output
        assert "test-secret" not in r.detail and "local-dev" not in r.detail


def test_secrets_prod_values_pass():
    env = {
        "CTF_TEAM_FLAG_SECRET": GOOD_HEX,
        "SECRET_KEY": "b" * 48,
        "KOTH_HILLS": "[{}]",
        "KOTH_SCORER_SECRET": "c" * 64,
        "MARIADB_PASSWORD": "d" * 40,
        "DATABASE_URL": "mysql+pymysql://ctfd:" + "d" * 40 + "@db/ctfd",
        "REDIS_URL": "redis://:pw@cache:6379",
    }
    res = pf.check_secrets(env)
    assert all(r.status == pf.OK for r in res), statuses(res)
    assert GOOD_HEX not in " ".join(r.detail for r in res)
    # short / non-hex
    res = pf.check_secrets({**env, "CTF_TEAM_FLAG_SECRET": "abc"})
    assert statuses(res)["CTF_TEAM_FLAG_SECRET"] == pf.FAIL
    res = pf.check_secrets({**env, "CTF_TEAM_FLAG_SECRET": "z" * 40})
    assert statuses(res)["CTF_TEAM_FLAG_SECRET"] == pf.WARN
    # no env at all -> WARN, not FAIL (network checks still run)
    assert [r.status for r in pf.check_secrets(None)] == [pf.WARN]


def test_windows_preselection_example_is_valid():
    res = pf.check_windows(PRESEL, "preselection", now=NOW)
    st = statuses(res)
    assert st == {"ordre": pf.OK, "start": pf.OK, "duree": pf.OK, "freeze": pf.OK}


def test_windows_missing_order_past_and_duration():
    assert statuses(pf.check_windows({}, "preselection", now=NOW)) == {
        "start/freeze/end": pf.FAIL
    }
    bad = {"start": "20", "freeze": "10", "end": "30"}
    assert statuses(pf.check_windows(bad, "none", now=0))["ordre"] == pf.FAIL
    # started 2 h ago
    running = {
        "start": str(NOW - 2 * 3600),
        "freeze": str(NOW + 71 * 3600),
        "end": str(NOW + 72 * 3600),
    }
    assert statuses(pf.check_windows(running, "none", now=NOW))["start"] == pf.FAIL
    assert (
        statuses(pf.check_windows(running, "none", now=NOW, allow_running=True))[
            "start"
        ]
        == pf.WARN
    )
    # ended
    over = {"start": "1", "freeze": "2", "end": "3"}
    assert statuses(pf.check_windows(over, "none", now=NOW))["end"] == pf.FAIL
    # preselection windows checked as a finale -> wrong duration
    assert statuses(pf.check_windows(PRESEL, "finale", now=NOW))["duree"] == pf.FAIL
    # freeze not in the last hour -> WARN
    early = {
        "start": str(NOW + 10),
        "freeze": str(NOW + 10 + 3600),
        "end": str(NOW + 10 + 72 * 3600),
    }
    assert (
        statuses(pf.check_windows(early, "preselection", now=NOW))["freeze"] == pf.WARN
    )
    # paused
    assert (
        statuses(
            pf.check_windows({**PRESEL, "paused": "true"}, "preselection", now=NOW)
        )["paused"]
        == pf.FAIL
    )


def test_identity_per_phase():
    cfg = {
        "ctf_name": "NCTF26",
        "ctf_theme": "hibris",
        "user_mode": "teams",
        "team_size": "4",
        "registration_visibility": "public",
        "score_visibility": "public",
        "account_visibility": "public",
        "challenge_visibility": "private",
        "verify_emails": "true",
    }
    res = pf.check_identity(cfg, "preselection", team_size=4)
    assert all(r.status == pf.OK for r in res), statuses(res)
    # finale wants registrations closed
    assert (
        statuses(pf.check_identity(cfg, "finale", 4))["registration_visibility"]
        == pf.FAIL
    )
    st = statuses(
        pf.check_identity(
            {**cfg, "ctf_name": "NCTF25", "user_mode": "users"}, "preselection", 4
        )
    )
    assert st["ctf_name"] == pf.FAIL and st["user_mode"] == pf.FAIL
    assert (
        statuses(pf.check_identity({**cfg, "team_size": ""}, "preselection", 4))[
            "team_size"
        ]
        == pf.FAIL
    )
    assert (
        statuses(pf.check_identity({**cfg, "team_size": ""}, "preselection"))[
            "team_size"
        ]
        == pf.WARN
    )
    assert (
        statuses(pf.check_identity({**cfg, "verify_emails": "false"}, "preselection"))[
            "verify_emails"
        ]
        == pf.WARN
    )
    assert (
        statuses(
            pf.check_identity({**cfg, "score_visibility": "hidden"}, "preselection")
        )["score_visibility"]
        == pf.WARN
    )


def test_email_gate_when_verification_on():
    # verify OFF -> le check email reste silencieux (check_identity le signale)
    assert pf.check_email({"verify_emails": "false"}, {}, "preselection") == []
    # verify ON sans SMTP (ni config ni env) -> FAIL bloquant (lockout)
    st = statuses(pf.check_email({"verify_emails": "true"}, {}, "preselection"))
    assert st["smtp"] == pf.FAIL
    # SMTP via la config CTFd -> OK + rappel MANUAL de prouver l'envoi
    st = statuses(
        pf.check_email(
            {"verify_emails": "true", "mail_server": "smtp-relay.brevo.com"},
            {},
            "preselection",
        )
    )
    assert st["smtp"] == pf.OK and st["envoi"] == pf.MANUAL
    # SMTP via l'env (MAIL_SERVER injecté par le compose, absent de /configs) -> OK
    st = statuses(
        pf.check_email(
            {"verify_emails": "true"},
            {"MAIL_SERVER": "email-smtp.eu-west-3.amazonaws.com"},
            "preselection",
        )
    )
    assert st["smtp"] == pf.OK


def test_registration_needs_reglement_and_university_field():
    cfg = {"tos_text": "# Reglement"}
    uni = [{"name": "Université", "required": True}]
    assert all(
        r.status == pf.OK for r in pf.check_registration(cfg, uni, "preselection")
    )
    st = statuses(pf.check_registration({"tos_text": " "}, uni, "preselection"))
    assert st["reglement"] == pf.FAIL
    assert (
        statuses(pf.check_registration({"tos_url": "https://x"}, uni, "preselection"))[
            "reglement"
        ]
        == pf.OK
    )
    assert (
        statuses(pf.check_registration(cfg, [], "preselection"))["universite"]
        == pf.FAIL
    )
    assert (
        statuses(
            pf.check_registration(
                cfg, [{"name": "Université", "required": False}], "preselection"
            )
        )["universite"]
        == pf.FAIL
    )
    # finale : inscriptions fermees, simple avertissement
    assert statuses(pf.check_registration({}, [], "finale"))["reglement"] == pf.WARN


def test_content_counts_flags_and_test_values():
    chals = [
        {"id": 1, "name": "A", "category": "web", "state": "visible"},
        {"id": 2, "name": "B", "category": "pwn", "state": "visible"},
        {"id": 3, "name": "C", "category": "pwn", "state": "hidden"},
    ]
    flags = [
        {"challenge_id": 1, "type": "static", "content": "NCTF{real}"},
        {"challenge_id": 2, "type": "team_hmac", "content": "pwn-b"},
        {"challenge_id": 3, "type": "static", "content": "NCTF{test-flag}"},
    ]
    # check_content compte désormais le set VISIBLE : 2 challenges visibles
    # (ids 1,2) sur 2 catégories ; le 3e est masqué (compté à part -> hidden).
    st = statuses(pf.check_content(chals, flags, 2, 2))
    assert st["challenges"] == pf.OK and st["categories"] == pf.OK
    assert st["hidden"] == pf.WARN
    assert st["flags"] == pf.OK
    assert st["flags de test"] == pf.FAIL
    st = statuses(pf.check_content(chals[:2], flags[:2], 203, 19))
    assert st["challenges"] == pf.FAIL and st["categories"] == pf.FAIL
    assert st["hidden"] == pf.OK and st["flags de test"] == pf.OK
    st = statuses(pf.check_content(chals, flags[:1]))
    assert st["flags"] == pf.FAIL
    st = statuses(
        pf.check_content(
            chals, flags[:2] + [{"challenge_id": 3, "type": "static", "content": " "}]
        )
    )
    assert st["flags vides"] == pf.FAIL
    assert statuses(pf.check_content([], []))["challenges"] == pf.FAIL


def test_koth_states():
    on = {
        "active": True,
        "hills": [{"id": "throne", "name": "T", "points": 1, "king": {"online": True}}],
    }
    off = {
        "active": True,
        "hills": [
            {
                "id": "throne",
                "name": "T",
                "points": 1,
                "king": {"online": False},
                "error": "timeout",
            }
        ],
    }
    env_k = {"KOTH_HILLS": "[{}]"}
    assert statuses(pf.check_koth(on, env_k))["throne"] == pf.OK
    st = by_name(pf.check_koth(off, env_k))["throne"]
    assert st.status == pf.FAIL and "timeout" in st.detail
    assert statuses(pf.check_koth({"active": False}, env_k))["plugin"] == pf.FAIL
    assert statuses(pf.check_koth({"active": False}, {}))["plugin"] == pf.OK
    assert statuses(pf.check_koth(None, {}))["plugin"] == pf.OK
    assert statuses(pf.check_koth(None, env_k))["plugin"] == pf.FAIL
    assert (
        statuses(pf.check_koth({"active": True, "hills": []}, env_k))["collines"]
        == pf.FAIL
    )


def test_theme_and_exit_code_and_report(capsys):
    st = statuses(
        pf.check_theme("<div class='nctf-intro'>", {"HTML_SANITIZATION": "0"})
    )
    assert st == {"accueil": pf.OK, "HTML_SANITIZATION": pf.OK}
    st = statuses(pf.check_theme("<p>plain</p>", {"HTML_SANITIZATION": "true"}))
    assert st == {"accueil": pf.WARN, "HTML_SANITIZATION": pf.WARN}
    assert statuses(pf.check_theme(None, None))["accueil"] == pf.FAIL
    res = pf.check_theme("<p>plain</p>", None) + pf.manual_checks()
    assert pf.exit_code(res) == 0  # WARN + MANUAL never block
    pf.report(res)
    out = capsys.readouterr().out
    assert "PRET" in out and "[MANUAL]" in out and "[WARN  ]" in out
    pf.report(pf.check_theme(None, None))
    assert "REFUSE" in capsys.readouterr().out
