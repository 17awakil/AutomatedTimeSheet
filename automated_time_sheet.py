#! /usr/bin/env python

# Standard library imports
import csv
import sys
from datetime import datetime, timedelta
import argparse

# Related third pary imports
from jira import JIRA

# Set up argument parser for time report options
parser = argparse.ArgumentParser()
parser.add_argument(
    "--server", help="The JIRA server URL you wish to connect to", type=str)
parser.add_argument(
    "--username", help="The JIRA username you wish to login with", type=str)
parser.add_argument(
    "--password", help="The password to your JIRA account", type=str)
parser.add_argument(
    "--project-key", help="The key to the project for which you wish to produce a time report", type=str)
parser.add_argument(
    "--start-date", help="The start date for the time report in this format: YYYY-MM-DD", type=str)
parser.add_argument(
    "--end-date", help="The end date for the time report in this format: YYYY-MM-DD", type=str)
args = parser.parse_args()

# Constant declaration for default values
SERVER = "http://jira:8080"
USERNAME = "awakil"
PASSWORD = "Nairy444@"
PROJECT_KEY = "TEST123"

# Change constants if different values are inputted by command line
if args.server:
    SERVER = args.server
if args.username:
    USERNAME = args.username
if args.password:
    PASSWORD = asgs.password
if args.project_key:
    PROJECT_KEY = args.project_key

# Global variables
start_date = datetime.strptime("2019-07-01", "%Y-%m-%d")
if args.start_date:
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
end_date = start_date
if args.end_date:
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d")

# Log into jira admin account on server
jira = JIRA(SERVER, basic_auth=(USERNAME, PASSWORD))

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
