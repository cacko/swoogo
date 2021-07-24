from enum import Enum
import secrets
import json

from app.storage import Storage
from functools import reduce


class JiraStatus(Enum):
    QA = "QA"
    CODE_REVIEW = "Code Review"
    IN_PROGRESS = "In Progress"

class JiraAccount(dict):
    @property
    def name(self):
        return self.get("displayName", "<unassigned>")

    @property
    def id(self):
        return self.get("accountId")

    @property
    def email(self):
        return self.get("emailAddress", "<unknown>")


class IssueHistory(dict):
    @property
    def author(self) -> JiraAccount:
        return JiraAccount(self.get("author", {"emailAddress": "<none>"}))

    @property
    def items(self) -> list:
        return self.get("items", [])

    @property
    def status(self) -> list:
        res = reduce(
            lambda r, x: [x.get("toString"), *r] if x.get("field") == "status" else r,
            self.items,
            [],
        )
        return res


class IssueChangelog(dict):
    @property
    def history(self) -> list[IssueHistory]:
        return [IssueHistory(h) for h in self.get("histories", [])]

class IssueStatus(dict):
    @property
    def name(self):
        return self.get("name", "")


class Issue(dict):
    @property
    def id(self):
        return self.get("id")

    @property
    def key(self):
        return self.get("key")

    @property
    def summary(self):
        return self.fields.get("summary")

    @property
    def fields(self) -> dict:
        return self.get("fields")

    @property
    def assignee(self):
        if data := self.fields.get("assignee"):
            return JiraAccount(**data)
        return JiraAccount({"emailAddress": "<unassigned>"})

    @property
    def status(self) -> IssueStatus:
        return IssueStatus(self.fields.get("status", {"name": "<none>"}))

    def persist(self, dbkey=None):
        if not dbkey:
            dbkey = f"waiting:{self.key}"
        Storage.set(
            dbkey,
            json.dumps(dict(self.items())),
        )
        Storage.persist(dbkey)
        return dbkey


class Commit(dict):
    @property
    def id(self):
        return self.get("id", None)


class DevStatus(dict):
    @property
    def detail(self):
        return self.get("detail", [])[-1]

    @property
    def repository(self):
        return self.detail.get("repositories", [])[-1] if self.detail else None

    @property
    def commits(self) -> list[Commit]:
        return (
            list(map(lambda x: Commit(x), self.repository.get("commits", [])))
            if self.repository
            else []
        )
