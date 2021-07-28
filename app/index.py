from flask import (
    Blueprint, abort, redirect
)
from flask.helpers import url_for

bp = Blueprint('index', __name__)

@bp.route('/')
def index():
    redirect(url_for("/custom_50x.html"), 502)