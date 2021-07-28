from flask import (
    Blueprint, abort, redirect
)

bp = Blueprint('index', __name__)

@bp.route('/')
def index():
    redirect("/custom_50x.html", 502)