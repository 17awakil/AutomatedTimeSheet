#! /usr/bin/env python

# Standard library imports
import argparse
import csv
from datetime import datetime, timedelta
import pprint
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
                    default="UC",
                    )
parser.add_argument("-start",
                    "--start-date",
                    help="The start date for the time report in this format: YYYY-MM-DD",
                    type=str,
                    required=True
                    )
parser.add_argument("-end",
                    "--end-date",
                    help="The end date for the time report in this format: YYYY-MM-DD",
                    type=str,
                    )
args = parser.parse_args()

# Functions
def insert_progress(date, assignee, issue, start_date, end_date):
    cur_prog = {"assignee": assignee,
                "issue": issue,
                "start": start_date,
                "end": end_date,
                }
    # Check if the progress overlaps with the day of the report
    if cur_prog["start"].date() <= date.date() <= cur_prog["end"].date():
        # Check if progress started before 8:00 on that day
        if date + timedelta(hours=8) > cur_prog["start"]:
            cur_prog["start"] = date + timedelta(hours=8)
        # If progress start after 16:00, then the progress shouldn't be included
        if date + timedelta(hours=16) <= cur_prog["start"]:
            return
        # If progress ends before 8:00, then the progress shouldn't be included
        if date + timedelta(hours=8) > cur_prog["end"]:
            return
        # If progress ends after 16:00, end it at 16:00
        if date + timedelta(hours=16) <= cur_prog["end"]:
            cur_prog["end"] = date + timedelta(hours=16)
        progress[date.strftime("%Y-%m-%d")].append(cur_prog)

# Global variables
start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
if args.end_date:
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
else:
    end_date = start_date

# Log into jira admin account on server
jira = JIRA(args.server, basic_auth=(args.username, args.password))

progress = {}
date = start_date
while date <= end_date:
    date_string = date.strftime("%Y-%m-%d")
    # Make an entry for each day in the range [start_date, end_date] where progresses for the day will be stored
    progress[date_string] = []
    # Search issues for that day
    issues = jira.search_issues("project= " + args.project_key +
                                " AND status WAS 'In Progress' ON " + date_string +
                                " AND type != Epic",
                                expand="changelog",
                                )
    # Iterate through issues
    for issue in issues:
        assignee = None
        if issue.fields.assignee:
            assignee = issue.fields.assignee.displayName
        start = None
        end = None
        # Iterate through all the changes for each issue
        issue.changelog.histories.sort(key=lambda x: x.created)
        for change in issue.changelog.histories:
            # Change time parsed into a datetime object
            change_date = datetime.strptime(change.created[0:22], "%Y-%m-%dT%H:%M:%S.%f")
            for item in change.items:
                # Status changes (from "To-Do" to "In Progress" etc.)
                if item.field == "status":
                    # Change from NOT "In Progress" to "In Progress"
                    if item.fromString != "In Progress" and item.toString == "In Progress":
                        start = change_date
                    # Change from "In Progress" to NOT "In Progress"
                    if item.fromString == "In Progress" and item.toString != "In Progress":
                        end = change_date
                        insert_progress(date, assignee, issue, start, end)
                        start = None
                        end = None

                # Assignee changes
                if item.field == "assignee":
                    # If issue is not in progress, then just add assignee
                    if not start:
                        assignee = item.toString
                    # If there was a change of assignee while in progress, we must end the progress,
                    # append it, and create a new progress with the new assignee
                    elif start:
                        end = change_date
                        insert_progress(date, assignee, issue, start, end)
                        assignee = item.toString
                        start = change_date
                        end = None

        # If by the end of the changelog there is a progress that has started but not ended, then
        # end the progress at the time of the report (now)
        if start:
            end = datetime.now()
            insert_progress(date, assignee, issue, start, end)
    date += timedelta(days=1)

pprint.pprint(progress)

# Write data into csv file
with open("auto_time_report.csv", "w", newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Date"] +
                        ["Assignee"] +
                        ["Issue Type"] +
                        ["Issue Key"] +
                        ["Issue Title"] +
                        ["Epic Title"] +
                        ["Time Spent"]
                        )
    for date in progress:
        for prog in progress[date]:
            csv_writer.writerow([date] +
                                [prog["assignee"]] +
                                [prog["issue"].fields.issuetype.name] +
                                [prog["issue"].key] +
                                [prog["issue"].fields.summary] +
                                [prog["issue"].fields.customfield_10101] + # Epic item
                                [prog["end"] - prog["start"]]
                                )
        csv_writer.writerow("")
