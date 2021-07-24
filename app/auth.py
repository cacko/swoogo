from flask import request, abort, current_app
import pyotp
from functools import wraps
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

bp = Blueprint('auth', __name__, url_prefix="/auth")


HEADER_TOKEN = "X-Token"
SETTING_TOTP_SECRET = "TOTP_SECRET"


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