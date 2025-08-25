DEFAULT_VERIFICATION_EMAIL_SUBJECT = "Confirm your account for {ctf_name}"
DEFAULT_VERIFICATION_EMAIL_BODY = (
    "Welcome to {ctf_name}!\n\n"
    "Click the following link to confirm and activate your account:\n"
    "{url}"
    "\n\n"
    "If the link is not clickable, try copying and pasting it into your browser."
)
DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_SUBJECT = "Successfully registered for {ctf_name}"
DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_BODY = (
    "You've successfully registered for {ctf_name}!"
)
DEFAULT_USER_CREATION_EMAIL_SUBJECT = "Message from {ctf_name}"
DEFAULT_USER_CREATION_EMAIL_BODY = (
    "A new account has been created for you for {ctf_name} at {url}. \n\n"
    "Username: {name}\n"
    "Password: {password}"
)
DEFAULT_PASSWORD_RESET_SUBJECT = "Password Reset Request from {ctf_name}"
DEFAULT_PASSWORD_RESET_BODY = (
    "Did you initiate a password reset on {ctf_name}? "
    "If you didn't initiate this request you can ignore this email. \n\n"
    "Click the following link to reset your password:\n{url}\n\n"
    "If the link is not clickable, try copying and pasting it into your browser."
)
DEFAULT_PASSWORD_CHANGE_ALERT_SUBJECT = "Password Change Confirmation for {ctf_name}"
DEFAULT_PASSWORD_CHANGE_ALERT_BODY = (
    "Your password for {ctf_name} has been changed.\n\n"
    "If you didn't request a password change you can reset your password here:\n{url}\n\n"
    "If the link is not clickable, try copying and pasting it into your browser."
)
