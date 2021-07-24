import logging
from app.scheduler import Scheduler
from app.storage import Storage
from attlasian import Attlasian
from .types import JiraStatus
from app.jira.items import WaitingItem
from datetime import datetime, timedelta


def reschedule() -> datetime:
    now = datetime.now()
    if now.weekday() > 4:
        monday = now + timedelta(7 - now.weekday())
        return monday - timedelta(hours=monday.hour - 9)
    if now.hour > 17:
        tmr = now + timedelta(days=1)
        return tmr - timedelta(hours=tmr.hour - 9)
    if now.hour < 9:
        return now + timedelta(hours=9 - now.hour)


def add_job(dbkey, issue, run_date):
    return Scheduler.add_job(
        id=issue.key,
        func=approve_commits,
        args=[dbkey],
        replace_existing=True,
        trigger="date",
        run_date=run_date,
    )


def approve_commits(dbkey):
    with Scheduler.app_context as context:
        logger: logging.Logger = context.app.logger
        item = WaitingItem(Storage.get(dbkey))
        issue = item.issue
        logger.info(f"Processing {issue.key} {dbkey}")
        if newTime := reschedule():
            logger.info(f"Rescheduled {issue.key} -> {newTime}")
            item.job = add_job(dbkey, issue, newTime)
            return True
        aprKey = f"processed:{issue.key}"
        if not item.isValid:
            logger.info(f"Not Valid {issue.key} - {item.errors}")
            issue.update(
                {
                    "processed": {
                        "timestamp": datetime.now().timestamp(),
                        "result": False,
                        "error": item.errors,
                    }
                }
            )
            return Storage.rename(issue.persist(dbkey), aprKey)
        commits = item.devStatus.commits
        if not len(commits):
            Attlasian.Jira.setIssueStatus(
                item.issue,
                JiraStatus.IN_PROGRESS,
                "Hey, I do not see any commits.\n\nThanks.",
            )
            Attlasian.Jira.assignIssue(item.issue, item.returnTo.id)
            issue.update(
                {
                    "processed": {
                        "timestamp": datetime.now().timestamp(),
                        "result": False,
                        "error": "No commits",
                    }
                }
            )
            return Storage.rename(issue.persist(dbkey), aprKey)
        Attlasian.Bitbucket.approve(item.devStatus.commits)
        try:
            Attlasian.Jira.setIssueStatus(item.issue, JiraStatus.QA)
            Attlasian.Jira.assignIssue(item.issue)
            issue.update({"processed": {"timestamp": datetime.now().timestamp(), "result": True}})
        except:
            issue.update(
                {
                    "processed": {
                        "timestamp": datetime.now().timestamp(),
                        "result": False,
                        "error": "API error",
                    }
                }
            )
        return Storage.rename(issue.persist(dbkey), aprKey)
