#!/usr/bin/env python
# pylint: disable=invalid-name

# http://www.redmine.org/projects/redmine/wiki/Rest_api
# author: guido

import argparse
import json
import os
import urllib
import urllib2
import ssl

REDMINE_API_KEY = os.environ.get("REDMINE_API_KEY")
REDMINE_ENDPOINT = os.environ.get("REDMINE_ENDPOINT")

TRACKERS = {
    "task": 7
}

class bcolors:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"


def create_insecure_ssl_context():
    """
    Create a ssl context that trust all certificates (do NOT do this in production)
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

    
def http_headers():
    return {
        "X-Redmine-API-Key": REDMINE_API_KEY,
        "Content-Type": "application/json"
    }


def get_user_id():
    # XXX memoize
    headers = http_headers()
    request = urllib2.Request("%s/users/current.json" % REDMINE_ENDPOINT, headers=headers)
    response = urllib2.urlopen(request, context=create_insecure_ssl_context())
    user = json.load(response)["user"]
    return user["id"]


def list_handler(options):
    data = {
        "project_id": options.project,
        "status_id": options.status,
        "tracker_id": TRACKERS[options.tracker],
        "cf_8": options.iteration,
        "sort": options.sort,
        "limit": options.limit
    }

    qs = urllib.urlencode(data)

    headers = http_headers()
    request = urllib2.Request("%s/issues.json?%s" % (REDMINE_ENDPOINT, qs), headers=headers)
    response = urllib2.urlopen(request, context=create_insecure_ssl_context())
    issues = json.load(response)["issues"]
    print_issue_list(issues)


def print_issue_list(issues):
    for issue in issues:
        print_issue_row(issue)


def print_issue_row(issue):
    headers = http_headers()
    request = urllib2.Request("%s/issues/%s.json" % (REDMINE_ENDPOINT, issue["id"]), headers=headers)
    response = urllib2.urlopen(request, context=create_insecure_ssl_context())
    issue = json.load(response)["issue"]

    if "assigned_to" in issue:
        asignee = issue["assigned_to"]["id"] == me
        asignee_name = issue["assigned_to"]["name"].partition(" ")[0] # keep name
        if asignee:
            asignee_name = bcolors.GREEN + asignee_name + bcolors.ENDC
    else:
        asignee = False
        asignee_name = "Unassigned"

    print("%s %s %s %s [%s] - %s" % (
        "x" if issue["status"]["name"] in ["Closed", "Resolved"] else " ",
        "*" if asignee else " ",
        issue["id"],
        issue["subject"],
        asignee_name,
        issue["status"]["name"]))


def detail_handler(options):
    headers = http_headers()
    request = urllib2.Request("%s/issues/%s.json" % (REDMINE_ENDPOINT, options.issue), headers=headers)
    response = urllib2.urlopen(request, context=create_insecure_ssl_context())
    issue = json.load(response)["issue"]

    print("%s %s" % (issue["id"], issue["subject"]))
    print("Author %s (%s)" % (issue["author"]["name"], issue["created_on"]))
    print("Assigned to %s" % issue["assigned_to"]["name"])
    print("Status %s" % issue["status"]["name"])
    print(issue["description"] or "No description")
    print("%s/issues/%s" % (REDMINE_ENDPOINT, issue["id"]))


def close_handler(options):
    STATUS_CLOSED = 5
    data = {"issue": { "status_id": STATUS_CLOSED, "notes": options.notes }} # 5 = Closed

    headers = http_headers()
    request = urllib2.Request("%s/issues/%s.json" % (REDMINE_ENDPOINT, options.issue), headers=headers)
    request.get_method = lambda: "PUT"
    response = urllib2.urlopen(request, json.dumps(data), context=create_insecure_ssl_context())


def build_arg_parser():
    parser = argparse.ArgumentParser(description="Redmine CLI")
    subparsers = parser.add_subparsers(dest="operation")

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("-s", "--status", help="issue status", choices=["open", "closed", "*"], default="*")
    list_parser.add_argument("-p", "--project", help="project name or id", default="4PF")
    list_parser.add_argument("-t", "--tracker", help="tracker id", choices=["task"], default="task")
    list_parser.add_argument("-i", "--iteration", "--sprint", help="sprint id", default="012")
    list_parser.add_argument("--sort", help=argparse.SUPPRESS, default="status:asc")
    list_parser.add_argument("--limit", help=argparse.SUPPRESS, type=int, default=50)
    list_parser.set_defaults(func=list_handler)

    detail_parser = subparsers.add_parser("detail")
    detail_parser.add_argument("-i", "--issue", help="issue id")
    detail_parser.set_defaults(func=detail_handler)

    close_parser = subparsers.add_parser("close")
    close_parser.add_argument("-i", "--issue", help="issue id")
    close_parser.add_argument("-n", "--notes", help="issue notes", default="closed from redmine cli")
    close_parser.set_defaults(func=close_handler)

    return parser

parser = build_arg_parser()
arguments = parser.parse_args()

try:
    me = get_user_id()
except urllib2.URLError, e:
    print("Network error. Make sure you can reach %s" % REDMINE_ENDPOINT)
    exit(1)

arguments.func(arguments)
