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


#Constant declaration
date1 = sys.argv[1]
date2 = ""
project_key = "TEST123"
issues = []



#Get users from jira server that are in a specific project
users = jira.search_assignable_users_for_projects("", project_key)

#Process issues in the following data structure: {user1 : {issue1 : hours1 , issue2 : hours2} , user2 : {issue3 : hours3}, ...}
user_issues = {}
for user in users:
    user_issues[user.displayName] = {}
    issues = jira.search_issues("project = {} AND status WAS 'In Progress' ON {} AND assignee WAS '{}' ON {} ".format(project_key, date1, user.key, date1))
    
    if len(sys.argv) == 3:
        date2 = sys.argv[2]
        issues = jira.search_issues("project = {} AND status WAS 'In Progress' DURING ({},{}) AND assignee WAS '{}' DURING ({},{}) ".format(project_key, date1, date2, user.key, date1, date2))
    
    for issue in issues:
        user_issues[user.displayName][issue.key] = 0


#Calculate hours spent on issues (high-level estimation)
for user, assigned_issues in user_issues.items():
    for issue, hours in assigned_issues.items():
        user_issues[user][issue] = 8.0 / len(assigned_issues.keys())


#Write data into csv file
with open("auto_time_report.csv", "w", newline = '') as csv_file:
    csv_writer = csv.writer(csv_file)

    if len(sys.argv) == 2:
        csv_writer.writerow(["Automated JIRA Time Report"] + ["for " + date1])
    elif len(sys.argv) ==3:
        csv_writer.writerow(["Automated JIRA Time Report"] + ["for " + date1 + " to " + date2]) 

    csv_writer.writerow(" ")
    csv_writer.writerow(["User"] + ["Assigned Issues"] + ["Hours Spent"])
    
    for user in user_issues:
        for issue, hours in user_issues[user].items():
                csv_writer.writerow([user] + [issue] + [hours])

