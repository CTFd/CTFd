import base64
import hashlib
import io
import json
import secrets

import pyotp
import qrcode
from cryptography.fernet import Fernet
from flask import current_app

from CTFd.utils.crypto import hash_password, verify_password

MFA_TOTP_DIGITS = 6
MFA_TOTP_INTERVAL = 30
MFA_TOTP_VALID_WINDOW = 1
MFA_BACKUP_CODE_COUNT = 10
MFA_BACKUP_CODE_LENGTH = 10
MFA_BACKUP_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def _fernet():
    secret_key = current_app.config["SECRET_KEY"]
    if isinstance(secret_key, str):
        secret_key = secret_key.encode("utf-8")

    key_material = hashlib.sha256(secret_key + b"|ctfd:mfa|v1").digest()
    key = base64.urlsafe_b64encode(key_material)
    return Fernet(key)


def generate_totp_secret():
    return pyotp.random_base32()


def encrypt_totp_secret(secret):
    return _fernet().encrypt(secret.encode("utf-8")).decode("utf-8")


def decrypt_totp_secret(secret):
    return _fernet().decrypt(secret.encode("utf-8")).decode("utf-8")


def build_totp(secret):
    return pyotp.TOTP(secret, digits=MFA_TOTP_DIGITS, interval=MFA_TOTP_INTERVAL)


def build_totp_uri(secret, account_name, issuer_name):
    return build_totp(secret).provisioning_uri(
        name=account_name, issuer_name=issuer_name
    )


def generate_totp_qrcode(uri):
    qr = qrcode.QRCode(box_size=6, border=1)
    qr.add_data(uri)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white")

    output = io.BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    return base64.b64encode(output.read()).decode("ascii")


def normalize_otp(otp):
    if otp is None:
        return ""

    return "".join(str(otp).strip().split())


def verify_totp_code(secret, otp):
    otp = normalize_otp(otp)
    if otp == "":
        return False

    return bool(build_totp(secret).verify(otp, valid_window=MFA_TOTP_VALID_WINDOW))


def generate_backup_codes(count=MFA_BACKUP_CODE_COUNT):
    codes = []
    for _ in range(count):
        code = "".join(
            secrets.choice(MFA_BACKUP_CODE_ALPHABET)
            for _ in range(MFA_BACKUP_CODE_LENGTH)
        )
        codes.append(code)
    return codes


def hash_backup_codes(codes):
    return json.dumps([hash_password(code) for code in codes])


def parse_backup_codes(backup_codes):
    if not backup_codes:
        return []

    try:
        parsed = json.loads(backup_codes)
    except (TypeError, ValueError):
        return []

    if isinstance(parsed, list):
        return [str(x) for x in parsed]

    return []


def count_backup_codes(backup_codes):
    return len(parse_backup_codes(backup_codes))


def consume_backup_code(backup_codes, candidate):
    candidate = normalize_otp(candidate).upper()
    if candidate == "":
        return False, backup_codes

    hashed_codes = parse_backup_codes(backup_codes)
    for idx, hashed in enumerate(hashed_codes):
        if verify_password(candidate, hashed):
            del hashed_codes[idx]
            return True, json.dumps(hashed_codes)

    return False, backup_codes


def is_mfa_enabled(user):
    return bool(user and user.mfa and user.mfa.enabled)


def get_mfa_labels(user):
    issuer = current_app.config.get("APP_NAME") or "CTFd"
    account_name = user.email or user.name
    return issuer, account_name
