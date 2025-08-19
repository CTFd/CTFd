from CTFd.constants.options import (
    AccountVisibilityTypes,
    ChallengeVisibilityTypes,
    RegistrationVisibilityTypes,
    ScoreVisibilityTypes,
    UserModeTypes,
)
from CTFd.constants.themes import DEFAULT_THEME

DEFAULTS = {
    # General Settings
    "ctf_name": "CTFd",
    "user_mode": UserModeTypes.USERS,
    # Visual/Style Settings
    "ctf_theme": DEFAULT_THEME,
    # Visibility Settings
    "challenge_visibility": ChallengeVisibilityTypes.PRIVATE,
    "registration_visibility": RegistrationVisibilityTypes.PUBLIC,
    "score_visibility": ScoreVisibilityTypes.PUBLIC,
    "account_visibility": AccountVisibilityTypes.PUBLIC,
    # Default Email Templates (set to imported constants)
    "verification_email_subject": "Please confirm your account",  # DEFAULT_VERIFICATION_EMAIL_SUBJECT
    "verification_email_body": "Please visit the following link to confirm and activate your account: {url}",  # DEFAULT_VERIFICATION_EMAIL_BODY
    "successful_registration_email_subject": "Successfully registered for {ctf_name}",  # DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_SUBJECT
    "successful_registration_email_body": "You've successfully registered for {ctf_name}!",  # DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_BODY
    "user_creation_email_subject": "Message from {ctf_name}",  # DEFAULT_USER_CREATION_EMAIL_SUBJECT
    "user_creation_email_body": "A user account has been created for you for {ctf_name}. Your username is {name} and your password is {password}",  # DEFAULT_USER_CREATION_EMAIL_BODY
    "password_reset_subject": "Password Reset Request from {ctf_name}",  # DEFAULT_PASSWORD_RESET_SUBJECT
    "password_reset_body": "Did you initiate a password reset? Click the following link to reset your password: {url}",  # DEFAULT_PASSWORD_RESET_BODY
    "password_change_alert_subject": "Password Change Confirmation for {ctf_name}",
    "password_change_alert_body": "Your password for {ctf_name} has been changed.\n\nIf you didn't request a password change you can reset your password here: {url}",
}
