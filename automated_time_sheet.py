#Import statements
from jira import JIRA 
import csv
import collections
from datetime import *
import math

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

    start_dict = parse_date(start_date)
    end_dict = parse_date(end_date)

    start_obj = datetime(start_dict["year"], start_dict["month"], start_dict["day"], start_dict["hour"], start_dict["minute"], start_dict["second"])
    end_obj = datetime(end_dict["year"], end_dict["month"], end_dict["day"], end_dict["hour"], end_dict["minute"], end_dict["second"])
    

    return end_obj - start_obj


def status_changes(issue):
    """ Returns an Ordered Dictionary sorted from earliest change date to latest change date to an issue in this form: { date : {} }"""
    change_dict = {}
    for change in issue.changelog.histories:
        if change.items[0].field == "status":
            change_dict[change.created] = { "changeType" : change.items[0].field, "fromString" : change.items[0].fromString, "toString" : change.items[0].toString}
        elif change.items[0].field == "resolution":
            change_dict[change.created] = {"changeType" : change.items[0].field, "fromString" : change.items[1].fromString, "toString" : change.items[1].toString}
    change_dict = collections.OrderedDict(sorted(change_dict.items()))
    return change_dict


def hours_spent(issue):
    """ Returns the number of hours spent on an issue"""
    total_hours = 0 
    prev_date = None
    changes_ordered_dict = status_changes(issue)
    for date, change in changes_ordered_dict.items():
        if change["fromString"] != "In Progress" and change["toString"] == "In Progress":
            prev_date = date  #Save the date object when a user starts progress 
        elif (change["toString"] == "Done" or change["toString"] == "To Do") and prev_date != None:
            total_hours += (time_delta(prev_date, date).days * 8) + (time_delta(prev_date, date).seconds /3600.0)
            prev_date = None 
    
    return total_hours
        
#Log into jira admin account on server
jira = JIRA('http://jira:8080', basic_auth=('awakil', 'Nairy444@'))

#Create a {user : {issue : hours}} nested dictionary
user_issues_dict = {}
list_of_issues = jira.search_issues("project = TEST123", expand = "changelog")
for issue in list_of_issues:
    if issue.fields.assignee.displayName not in user_issues_dict.keys():
        user_issues_dict[issue.fields.assignee.displayName] = {}
    user_issues_dict[issue.fields.assignee.displayName][issue.key] = hours_spent(issue)


#Write dictionary into a csv file
with open("time_report.csv", "w", newline = '') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Automated Monthly Report"])
    csv_writer.writerow(['User'] + ['Assigned Issues'] +['Hours Spent'])
    for user, assigned_issues in user_issues_dict.items():
        for issue, hours_spent in assigned_issues.items():
            csv_writer.writerow([user] + [issue] + [hours_spent])
