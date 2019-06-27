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
    
    year = date.year
    month = date.month
    day = date.day
    hour = date.hour
    minute = date.minute
    second = date.second

    return {"year" : year , "month" : month , "day" : day , "hour" : hour , "minute" : minute , "second" : second }


def time_delta(start_date, end_date):
    """ Returns a timedelta object that is equal to the time elapsed from the start_date to the end_date """

    start = parse_date(start_date)
    end = parse_date(end_date)

    initial_time = datetime(start["year"], start["month"], start["day"], start["hour"], start["minute"], start["second"])
    final_time = datetime(end["year"], end["month"], end["day"], end["hour"], end["minute"], end["second"])
    
    return final_time - initial_time


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
    
    return total_hours

    
#Log into jira admin account on server
jira = JIRA('http://jira:8080', basic_auth=('awakil', 'Nairy444@'))

#Create a {user : {issue : hours}} nested dictionary
user_issues = {}
list_of_issues = jira.search_issues("project = TEST123 AND ( (resolved >= startOfMonth() AND resolved <= endOfMonth()) OR (status = 'In Progress') )"  , expand = "changelog")
for issue in list_of_issues:
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
    
