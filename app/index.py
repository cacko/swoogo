from flask import (
    Blueprint, abort
)

bp = Blueprint('index', __name__)

@bp.route('/')
def index():
    abort(502)