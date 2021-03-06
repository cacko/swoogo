from flask import Blueprint, request, render_template, current_app, redirect
from flask.helpers import url_for
from app.auth import auth_required, Auth
from app.storage import Storage
from .items import ProcessedItem, WaitingItem
from attlasian.types import Issue
from attlasian.commands import add_job
from datetime import datetime, timedelta
import random

bp = Blueprint("jira", __name__, url_prefix="/jira", template_folder="templates")


@bp.route("/")
@Auth.login_required
def index():
    res = Storage.keys("waiting:*")
    waiting = [WaitingItem(d) for d in Storage.mget(res)]
    res = Storage.keys("processed:*")
    processed = [ProcessedItem(x) for x in Storage.mget(res)]
    return render_template(
        "index.html",
        waiting=sorted(waiting, key=lambda w: w.job.next_run_time if w.job else 0),
        processed=sorted(processed, key=lambda a: a.timestamp),
    )


@bp.route("/approve", methods=["POST"])
@auth_required
def approve():
    data = request.get_json()
    if issueData := data.get("issue"):
        issue = Issue(issueData)
        dbkey = issue.persist()
        job = add_job(
            dbkey,
            issue,
            datetime.now() + timedelta(minutes=random.randint(5, 55)),
        )
        current_app.logger.info(f"JOB ADDED -> {job.next_run_time} {job.id}")

    return ("OK", 200)

@bp.route("/archive", methods=["GET"])
@Auth.login_required
def archive():
    key = request.args.get('key', '')
    type = request.args.get("type", '')
    Storage.rename(f"{type}:{key}", f"archived:{key}")
    return redirect(url_for("jira.index"))


