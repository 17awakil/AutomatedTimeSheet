#! /usr/bin/env python

# Standard library imports
import csv
import collections
from datetime import *
import math

# Related third pary imports
from jira import JIRA 


def parse_date(date_string):
    """ Returns a parsed date dictionary from a JIRA formatted date. Example date: 2019-06-18T18:39:02.524+0000 """

    date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%f%z")

    return date


def time_delta(start_date, end_date):
    """ Returns a timedelta object that is equal to the time elapsed from the start_date to the end_date """


    end = parse_date(end_date)
    start = parse_date(start_date)
    
    return end - start


def status_changes(issue):
    """ Returns an Ordered Dictionary sorted from earliest change date to latest change date to an issue in this form: { date : {} }"""
    
    changes = {}
    for change in issue.changelog.histories:
        if change.items[0].field == "status":
            changes[change.created] = {"changeType": change.items[0].field, "initialStatus": change.items[0].fromString, "finalStatus": change.items[0].toString}
        elif change.items[0].field == "resolution":
            changes[change.created] = {"changeType": change.items[0].field, "initialStatus": change.items[1].fromString, "finalStatus": change.items[1].toString}
    changes = collections.OrderedDict(sorted(changes.items()))
    
    return changes


def hours_spent(issue):
    """ Returns the number of hours spent on an issue"""
    
    total_hours = 0 
    prev_date = None
    issue_status_changes = status_changes(issue)
    for date, change in issue_status_changes.items():
        if change["initialStatus"] != "In Progress" and change["finalStatus"] == "In Progress":
            prev_date = date  #Save the date object when a user starts progress 
        elif (change["finalStatus"] != "In Progress") and prev_date != None:
            total_hours += (time_delta(prev_date, date).days * 8) + (time_delta(prev_date, date).seconds /3600.0)
            prev_date = None 
        # elif prev_date != None:
        #     total_hours += time_delta(prev_date, "now").days * 8 + (time_delta(prev_date,"now").seconds /3600.0)

    return total_hours

    
#Log into jira admin account on server
jira = JIRA('http://jira:8080', basic_auth=('awakil', 'Nairy444@'))

#Create a {user : {issue : hours}} nested dictionary
user_issues = {}
issues = jira.search_issues("project = TEST123 AND ( (resolved >= startOfMonth() AND resolved <= endOfMonth()) OR (status = 'In Progress') )"  , expand = "changelog")
for issue in issues:
    if issue.fields.assignee.displayName not in user_issues.keys():
        user_issues[issue.fields.assignee.displayName] = {}
    user_issues[issue.fields.assignee.displayName][issue.key] = hours_spent(issue)


#Write dictionary into a csv file
with open("time_report.csv", "w", newline = '') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Automated Monthly Report"])
    csv_writer.writerow(["User"] + ["Assigned Issues"] + ["Date Started"] + ["Date Completed"] + ["Hours Spent"])
    for user, assigned_issues in user_issues.items():
        for issue, hours_spent in assigned_issues.items():
            csv_writer.writerow([user] + [issue] + [""] + [""] + [hours_spent])
    csv_writer.writerow([""])
    csv_writer.writerow(["User"] +["Total Hours"])
    
def progress_overlapping(progress1 , progress2):
    
    start1 = parse_date(list(progress1)[0])
    end1 = parse_date(list(progress1.values())[0])
    start2 = parse_date(list(progress2)[0])
    end2 = parse_date(list(progress2.values())[0])

    start_time = str
    end_time = str

    if (start1 <= start2 <= end1) or (start2 <= start1 <= end2):
        
        if start1 <= start2:
            start_time = start2
        else:
            start_time = start1

        if end1 <= end2:
            end_time = end1
        else:
            end_time = end2
        
        return {start_time : end_time}

def overlap_exists(progress1, progress2):
    if progress_overlapping(progress1,progress2) != None:
        return True
    else:
        return False

def progress(issue):
    changes = status_changes(issue)

    progresses = []

    start_progress = None

    for date, change in changes.items():
        if change["initialStatus"] != "In Progress" and change["finalStatus"] == "In Progress":
            start_progress = date
            
        elif change["finalStatus"] != "In Progress" and change["initialStatus"] == "In Progress" and start_progress != None:
            progresses.append({start_progress : date})
            start_progress = None
    
    return progresses


def issues_today_by_user():
    issues = jira.search_issues("project = TEST123 AND ( (resolved >= startOfDay() AND resolved <= endOfDay()) OR (status = 'In Progress') )", expand = "changelog")
    users_issues = []
    for issue in issues:
        users_issues.append(issue)
    return users_issues


issue1_progresses = progress(jira.issue("TEST123-13", expand = "changelog"))
issue2_progresses = progress(jira.issue("TEST123-12", expand = "changelog"))


