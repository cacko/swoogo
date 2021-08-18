from flask import request, abort, current_app
import pyotp
from functools import wraps
from flask import (
    Blueprint, request
)
from werkzeug.exceptions import abort
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('auth', __name__, url_prefix="/auth")
Auth = HTTPBasicAuth()

HEADER_TOKEN = "X-Token"
SETTING_TOTP_SECRET = "TOTP_SECRET"
PASSWORD_CACKO = "PASSWORD_CACKO"


users = {
    "cacko": generate_password_hash(current_app.config.get(PASSWORD_CACKO)),
}

@Auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username

def auth_required(view):
    @wraps(view)
    def decorated_function(*args, **kwargs):
        if request.method == "OPTIONS":
            return
        TOTP = pyotp.TOTP(current_app.config.get(SETTING_TOTP_SECRET))
        if (token := request.headers.get(HEADER_TOKEN)) and TOTP.verify(token):
            return view(*args, **kwargs)
        abort(401)

    return decorated_function