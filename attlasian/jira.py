from .remote import Remote
from atlassian import Jira
from .types import (
    DevStatus,
    Issue,
    IssueHistory,
    JiraAccount,
    JiraStatus,
    IssueChangelog,
)

ENDPOINT_DEV_STATUS = "/rest/dev-status/1.0/issue/detail?issueId={issue.id}&applicationType=bitbucket&dataType=repository"


class jira_(Remote):
    _connector = Jira
    _api: Jira

    def getIssue(self, key):
        res = self._api.issue(key)
        return Issue(**res)

    def getChangelog(self, key) -> IssueChangelog:
        res = self._api.get_issue_changelog(key)
        return IssueChangelog(**res)

    def getDevStatus(self, issue: Issue) -> DevStatus:
        res = self._api.get(ENDPOINT_DEV_STATUS.format(issue=issue))
        return DevStatus(**res)

    def setIssueStatus(self, issue: Issue, status: JiraStatus, comment=None):
        update = None
        if comment:
            update = {"comment": [{"add": {"body": comment}}]}
        res = self._api.set_issue_status(issue.key, status.value, update=update)
        self._logger.info(f"\t status changed to {status.value}")
        return res

    def assignIssue(self, issue: Issue, account_id=None):
        res = self._api.assign_issue(issue.id, account_id=None)
        self._logger.info(f"\t assigning to {account_id}")
        return res

    def getReturnTo(self, key) -> JiraAccount:
        history: IssueHistory = next(
            filter(
                lambda h: JiraStatus.CODE_REVIEW.value in h.status,
                self.getChangelog(key).history,
            ),
            None,
        )
        return history.author if history else JiraAccount({"emailAddress": "<none>"})
