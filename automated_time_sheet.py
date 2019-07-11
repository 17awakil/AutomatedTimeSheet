#! /usr/bin/env python

# Standard library imports
import csv
import sys

# Related third pary imports
from jira import JIRA 


#Validation check
if len(sys.argv) < 2:
    sys.exit("Must input the date as a command line argument in the following format: YYYY-MM-DD")


#Log into jira admin account on server
jira = JIRA('http://jira:8080', basic_auth=('awakil', 'Nairy444@'))

date = sys.argv[1]

#Get users from jira server that are in progress in a specific project
users = jira.search_assignable_users_for_projects("", "TEST123")

#Process issues in the following data structure: {user1 : [ {issue1 : hours1}, {issue2 : hours2}, ...], user2 : [{issue3 : hours3}, ...], ...}
user_issues = {}
for user in users:
    user_issues[user.displayName] = []
    for issue in jira.search_issues("project = TEST123 AND status WAS 'In Progress' ON {} AND assignee WAS '{}' ON {} ".format(date, user.key, date)):
        user_issues[user.displayName].append({issue.key : 0 })


#Calculate hours spent on issues (high-level estimation)
for user, assigned_issues in user_issues.items():
    for issue in assigned_issues:
        issue[list(issue.keys())[0]] = 8.0 / len(assigned_issues)


#Write data into csv file
with open("auto_time_report.csv", "w", newline = '') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Automated JIRA Time Report"] + ["for " + date])
    csv_writer.writerow(" ")
    csv_writer.writerow(["User"] + ["Assigned Issues"] + ["Hours Spent"])
    for user, assigned_issues in user_issues.items():
        for issue in assigned_issues:
            for issue_key, hours_spent in issue.items():
                csv_writer.writerow([user] + [issue_key] + [hours_spent])

