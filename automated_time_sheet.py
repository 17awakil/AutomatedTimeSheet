#! /usr/bin/env python

# Standard library imports
import argparse
import csv
from datetime import datetime, timedelta

# Related third pary imports
from jira import JIRA

# Set up argument parser for time report options
parser = argparse.ArgumentParser()
parser.add_argument("-s",
                    "--server",
                    help="The JIRA server URL you wish to connect to",
                    type=str,
                    default="http://jira:8080",
                    )
parser.add_argument("-u",
                    "--username",
                    help="The JIRA username you wish to login with",
                    type=str,
                    default="awakil",
                    )
parser.add_argument("-pass",
                    "--password",
                    help="The password to your JIRA account",
                    type=str,
                    default="Nairy444@",
                    )
parser.add_argument("-proj",
                    "--project-key",
                    help="The key to the project for which you wish to produce a time report",
                    type=str,
                    default="TEST123",
                    )
parser.add_argument("start",
                    help="The start date for the time report in this format: YYYY-MM-DD",
                    type=str,
                    )
parser.add_argument("-end",
                    "--end-date",
                    help="The end date for the time report in this format: YYYY-MM-DD",
                    type=str,
                    default="2019-07-01",
                    )
args = parser.parse_args()

# Constants
PROJECT_KEY = args.project_key

# Global variables
start_date = datetime.strptime(args.start, "%Y-%m-%d")
end_date = datetime.strptime(args.end_date, "%Y-%m-%d")

# Log into jira admin account on server
jira = JIRA(args.server, basic_auth=(args.username, args.password))

# Get users from jira server that are in a specific project
users = jira.search_assignable_users_for_projects("", PROJECT_KEY)

# Process issues in the below data strucure:
# {date1: {user1: {issue1: hours1,
#                  issue2: hours2,
#                 },
#          user2: {issue3: hours3,
#                  issue4: hours4,
#                 },
#         },
#  date2: {user3: {issue5: hours5,
#                  issue6: hours6,
#                  issue7: hours7,
#                 },
#         },
# }
user_issues = {}
date = start_date
while date <= end_date:
    date_string = date.strftime("%Y-%m-%d")
    user_issues[date_string] = {}
    for user in users:
        user_issues[date_string][user.displayName] = {}
        issues = jira.search_issues("project= " + PROJECT_KEY +
                                    " AND status WAS 'In Progress' ON " + date_string +
                                    " AND assignee WAS " + user.key + " ON " + date_string
                                    )
        for issue in issues:
            user_issues[date_string][user.displayName][issue.key] = 0
    date += timedelta(days=1)

# Calculate hours spent on issues (high-level estimation)
for date in user_issues:
    for user in user_issues[date]:
        for issue in user_issues[date][user]:
            user_issues[date][user][issue] = 8.0 / len(user_issues[date][user])

# Write data into csv file
with open("auto_time_report.csv", "w", newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Automated JIRA Time Report"])
    csv_writer.writerow(" ")
    csv_writer.writerow(["Date"] + ["User"] + ["Assigned Issue"] + ["Hours Spent"])
    for date in user_issues:
        for user in user_issues[date]:
            for issue, hours in user_issues[date][user].items():
                csv_writer.writerow([date] + [user] + [issue] + [hours])
        csv_writer.writerow("")
