#! /usr/bin/env python

# Standard library imports
import csv
import sys

# Related third pary imports
from jira import JIRA 

#Log into jira admin account on server
jira = JIRA('http://jira:8080', basic_auth=('awakil', 'Nairy444@'))

#Validation check
if len(sys.argv) < 2:
    sys.exit("Must input the date as a command line argument in the following format: YYYY-MM-DD")

#Get issues worked on by date
def issues_by_date(date):
    issues = jira.search_issues("project = TEST123 AND status WAS 'In Progress' ON {}".format(date))
    users_issues = {}
    for issue in issues:
        if issue.fields.assignee.displayName not in users_issues.keys():
            users_issues[issue.fields.assignee.displayName] = []
        users_issues[issue.fields.assignee.displayName].append(issue.key)
    return users_issues

def hours_spent(issues):
    """ Returns the number of hours per issue, assuming that they worked 8 hours / number of issues they worked on that day """
    return 8.0 / len(issues)

#Write data into csv file
with open("auto_time_report.csv", "w", newline = '') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Automated JIRA Time Report"])
    csv_writer.writerow(" ")
    csv_writer.writerow(["User"] + ["Assigned Issues"] + ["Hours Spent"])
    for user, assigned_issues in issues_by_date(sys.argv[1]).items():
        hours = hours_spent(assigned_issues)
        for issue in assigned_issues:
            csv_writer.writerow([user] + [issue] + [hours])