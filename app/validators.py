import re


def validate_register_login_input(username, password):
    if len(username) < 8 or len(password) < 8:
        return False, "Username and password must be at least 8 characters long."

    if not re.match("^[A-Za-z0-9]*$", username):
        return False, "Username must not contain special characters."

    if not re.match("^[A-Za-z0-9]*$", password):
        return False, "Password must not contain special characters."

    if not re.match("^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]*$", username):
        return False, "Username must contain at least one letter and one number."

    if not re.match("^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]*$", password):
        return False, "Password must contain at least one letter and one number."

    return True, ""


def check_username_password_provided(username, password):
    if not username and not password:
        return False, "Username and password are required"
    elif not username:
        return False, "Username is required"
    elif not password:
        return False, "Password is required"
    return True, ""

