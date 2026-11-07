from dataclasses import dataclass


@dataclass
class DashboardSummary:
    category: str
    count: int
    summary: str


@dataclass
class RecentMail:
    sender: str
    subject: str
    category: str
    priority: str
    summary: str


def get_dashboard_payload():
    return {
        "user": {"name": "Ashin", "email": "ashin@example.com"},
        "totals": {"unread": 12, "important": 4, "newsletter": 5, "promotional": 3},
        "summary": [
            DashboardSummary("Important", 4, "Critical account alerts and urgent work follow-ups are waiting for review."),
            DashboardSummary("Newsletter", 5, "Tech and productivity newsletters are mostly informational and low priority."),
            DashboardSummary("Promotional", 3, "Deals and marketing emails are present but less urgent than account updates."),
        ],
        "recent": [
            RecentMail("bank@example.com", "Security alert: New sign-in detected", "Important", "High", "A new login was detected and the account should be reviewed for suspicious activity."),
            RecentMail("jobs@example.com", "Interview scheduled for tomorrow", "Important", "High", "A job interview is scheduled for tomorrow and requires a prompt response."),
        ],
    }
