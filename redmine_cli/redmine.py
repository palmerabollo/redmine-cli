#!/usr/bin/env python
# pylint: disable=invalid-name

# http://www.redmine.org/projects/redmine/wiki/Rest_api
# author: guido

import os
import json
from urllib import urlencode
from docopt import docopt
from sys import getfilesystemencoding
from requests import request, packages
from redmine_cli import  CLI_VERSION
# Avoid warning in old python versions for not verifying certificate
from requests.packages.urllib3.exceptions import InsecureRequestWarning

packages.urllib3.disable_warnings(InsecureRequestWarning)

# POSIX format for the CLI arguments (input for docopt library to parse the command line)
CLI_DOC = """pyRedmine CLI

Usage:
    red [-d] [-c conf] [-e url] [-k apikey] [-i sprint_number] [-p project] [-t track] list [-s <status>] [--sort <sort_order>] [--limit <n>]
    red [-d] [-c conf] [-e url] [-k apikey] detail <issue_id>
    red [-d] [-c conf] [-e url] [-k apikey] close <issue_id> [<notes>]

    red (-h | --help)
    red (-v | --version)

Options:
    -d --debug                          Enable debugging.
    -c conf --conf=conf                 Path to the configuration file (with redmine url and apikey)
    -e --url=url                        Redmine URL (Environment variable REDMINE_ENDPOINT)
    -k apikey --username=username       Api Key for Redmine (Environment variable REDMINE_API_KEY)
    -i iteration --sprint==iteration    Sprint number [default: 012]
    -p project --project=project        Project identifier [default: 4PF]
    -t track --tracker=track            Track [default: task]
    -s <status>                         Status to filter (open|closed) [default: *]
    --sort <sort_order>                 Order for the output [default: status:asc]
    --limit <n>                         Limit for output [default: 50]  
    -h --help                           Show this screen.
    -v --version                        Show version.
"""

REDMINE_API_KEY = os.environ.get("REDMINE_API_KEY")
REDMINE_ENDPOINT = os.environ.get("REDMINE_ENDPOINT")

TRACKERS = {
    "task": 7
}
me = None
headers = {
    "X-Redmine-API-Key": REDMINE_API_KEY,
    "Content-Type": "application/json"
}


class BColors:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"


def make_request(method, url,data=None, json_response=True):
    # TODO: remove deprecated interpolation
    response = request(method, url, data=data, headers=headers, verify=False)
    if json_response:
        return response.json()
    else:
        return response


def get_user_id():
    # XXX memoize
    user = make_request('GET', "%s/users/current.json" % REDMINE_ENDPOINT)
    return user['user']["id"]


def print_issue_list(issues):
    for issue in issues:
        print_issue_row(issue)


def print_issue_row(issue):
    response = make_request('GET',"%s/issues/%s.json" % (REDMINE_ENDPOINT, issue["id"]))
    issue = response["issue"]

    if "assigned_to" in issue:
        asignee = issue["assigned_to"]["id"] == me
        asignee_name = issue["assigned_to"]["name"].partition(" ")[0] # keep name
        if asignee:
            asignee_name = BColors.GREEN + asignee_name + BColors.ENDC
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


def _sanity_check(arguments):
    global me
    try:
        me = get_user_id()
    except Exception as e:
        print("Network error. Make sure you can reach %s" % REDMINE_ENDPOINT)
        exit(1)


def _command_list(arguments):
    data = {
        "project_id": arguments.get('--project'),
        "status_id": arguments.get('-s'),
        "tracker_id": TRACKERS[arguments.get('--tracker')],
        "cf_8": arguments.get('--sprint'),
        "sort": arguments.get('--sort'),
        "limit": arguments.get('--limit')
    }

    qs = urlencode(data)
    issues = make_request('GET',"%s/issues.json?%s" % (REDMINE_ENDPOINT, qs))["issues"]
    print_issue_list(issues)


def _command_close(arguments):
    STATUS_CLOSED = 5
    notes = arguments.get('<notes>', 'closed by pyRedmine client')
    data = json.dumps({"issue": { "status_id": STATUS_CLOSED, "notes":  notes}}) # 5 = Closed
    make_request('PUT', "%s/issues/%s.json" % (REDMINE_ENDPOINT, arguments.get('<issue_id>')), data=data, json_response=False)


def _command_detail(arguments):
    response = make_request('GET',"%s/issues/%s.json" % (REDMINE_ENDPOINT, arguments.get('<issue_id>')))
    issue = response["issue"]

    print("%s %s" % (issue["id"], issue["subject"]))
    print("Author %s (%s)" % (issue["author"]["name"], issue["created_on"]))
    print("Assigned to %s" % issue["assigned_to"]["name"])
    print("Status %s" % issue["status"]["name"])
    print(issue["description"] or "No description")
    print("%s/issues/%s" % (REDMINE_ENDPOINT, issue["id"]))


def convert_to_unicode_dict(input_dict):
    unicode_dict = dict()
    for key, value in input_dict.iteritems():
        key_unicode = unicode(key, getfilesystemencoding())
        if isinstance(value, list):  # not generic, just whit our expected dict
            value_unicode = map(lambda x: unicode(x, getfilesystemencoding())
                if isinstance(x, basestring) else x, value)
        elif isinstance(value, basestring):
            value_unicode = unicode(value, getfilesystemencoding())
        else:
            value_unicode = value
        unicode_dict[key_unicode] = value_unicode
    return unicode_dict


def command():
    """Parse the CLI arguments and execute the command

    Parse the CLI arguments, with docopt, according to CLI specification in CLI_DOC
    and execute the required command.
    The library docopt will validate the syntax of the CLI command
    """

    arguments = convert_to_unicode_dict(docopt(CLI_DOC, version=CLI_VERSION))

    _sanity_check(arguments)

    try:
        if arguments.get('list'):
            _command_list(arguments)
        elif arguments.get('detail'):
            _command_detail(arguments)
        elif arguments.get('close'):
            _command_close(arguments)
    except Exception as e:
        print('[Error]:')
        msg = 'It seems that something goes wrong. Contact the operator for further assistance.'
        if arguments.get('--debug'):
            print('Error details: {0}'.format(str(e)))
        print(msg)


if __name__ == "__main__":
    command()
