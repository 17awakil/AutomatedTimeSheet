#! /usr/bin/env python

# Standard library imports
import csv
import sys
from datetime import datetime, timedelta

# Related third pary imports
from jira import JIRA

# Validation check
if len(sys.argv) < 2:
    sys.exit("Must input the date as a command line argument"
             "in the following format: YYYY-MM-DD")

# Constant declaration
PROJECT_KEY = "TEST123"

# Global variables
start_date_string = sys.argv[1]
end_date_string = ""
issues = []
start_date = datetime.strptime(start_date_string, "%Y-%m-%d")
end_date = start_date
if len(sys.argv) == 3:
    end_date_string = sys.argv[2]
    end_date = datetime.strptime(end_date_string, "%Y-%m-%d")

# Log into jira admin account on server
jira = JIRA('http://jira:8080', basic_auth=('awakil', 'Nairy444@'))

# Get users from jira server that are in a specific project
users = jira.search_assignable_users_for_projects("", PROJECT_KEY)

# Process issues in the below data structure
# { date1 :
#           { user1 :
#                       {issue1 :hours1}
#           , user2 :
#                       {issue2: hours2}
#           }
# }

user_issues = {}
date = start_date
while date <= end_date:
    date_string = date.strftime("%Y-%m-%d")
    user_issues[date_string] = {}
    for user in users:
        user_issues[date_string][user.displayName] = {}
        issues = jira.search_issues("project={} AND status WAS 'In Progress'"
                                    "ON {} AND assignee WAS '{}' ON {} "
                                    .format(PROJECT_KEY, date_string, user.key,
                                            date_string))
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
    csv_writer.writerow(["Date"] + ["User"]
                                 + ["Assigned Issue"] + ["Hours Spent"])
    for date in user_issues:
        for user in user_issues[date]:
            for issue, hours in user_issues[date][user].items():
                csv_writer.writerow([date] + [user] + [issue] + [hours])
        csv_writer.writerow("")
