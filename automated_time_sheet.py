#! /usr/bin/env python

# Standard library imports
import csv
import sys

# Related third pary imports
from jira import JIRA 


#Validation check
if len(sys.argv) < 2:
    sys.exit("Must input the date as a command line argument in the following format: YYYY-MM-DD")

def hours_spent(issue):
    pass

#Constant declaration
PROJECT_KEY = "TEST123"

#Global variables
start_date = sys.argv[1]
end_date = ""
issues = []

#Log into jira admin account on server
jira = JIRA('http://jira:8080', basic_auth=('awakil', 'Nairy444@'))

#Get users from jira server that are in a specific project
users = jira.search_assignable_users_for_projects("", PROJECT_KEY)

#Process issues in the following data structure: {user1 : {issue1 : hours1 , issue2 : hours2} , user2 : {issue3 : hours3}, ...}
user_issues = {}
for user in users:
    user_issues[user.displayName] = {}
    
    if len(sys.argv) == 2:
        issues = jira.search_issues("project = {} AND status WAS 'In Progress' ON {} AND assignee WAS '{}' ON {} ".format(PROJECT_KEY, start_date, user.key, start_date))
    elif len(sys.argv) == 3:
        end_date = sys.argv[2]
        issues = jira.search_issues("project = {} AND status WAS 'In Progress' DURING ({},{}) AND assignee WAS '{}' DURING ({},{}) ".format(PROJECT_KEY, start_date, end_date, user.key, start_date, end_date))
    
    for issue in issues:
        user_issues[user.displayName][issue.key] = 0


#Calculate hours spent on issues (high-level estimation)
for user, assigned_issues in user_issues.items():
    for issue in assigned_issues:
        user_issues[user][issue] = 8.0 / len(assigned_issues.keys())


#Write data into csv file
with open("auto_time_report.csv", "w", newline = '') as csv_file:
    csv_writer = csv.writer(csv_file)

    if len(sys.argv) == 2:
        csv_writer.writerow(["Automated JIRA Time Report"] + ["for " + start_date])
    elif len(sys.argv) ==3:
        csv_writer.writerow(["Automated JIRA Time Report"] + ["from " + start_date + " to " + end_date]) 

    csv_writer.writerow(" ")
    csv_writer.writerow(["User"] + ["Assigned Issues"] + ["Hours Spent"])
    
    for user in user_issues:
        for issue, hours in user_issues[user].items():
                csv_writer.writerow([user] + [issue] + [hours])

