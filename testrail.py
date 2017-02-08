#!/usr/bin/env python
#
# Copyright (c) 2017, Lunge Technology, LLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""
A command line Testrail implementation
"""

import sys
import argparse
import requests
from requests.auth import HTTPBasicAuth


class Testrail(object):
    """
    Testrail API integration
    """

    def __init__(self, url, username, password):
        self.base_url = url + '?/api/v2/'
        self.auth = HTTPBasicAuth(username, password)

    def _request(self, method, url, data):
        assert method in ['GET', 'POST']

        url = self.base_url + url

        headers = {'Content-Type': 'application/json'}

        if method == 'GET':
            response = requests.get(url, auth=self.auth, headers=headers)
        else:
            response = requests.post(
                url, auth=self.auth, headers=headers, json=data)
        result = response.json()
        assert 'error' not in result, 'ERROR: %s' % result['error']
        return result

    def get_projects(self):
        """
        Get a list of projects
        """
        return self._request('GET', 'get_projects', None)

    def get_project(self, name):
        """
        Get a project based on the project name
        """
        for project in self.get_projects():
            if project['name'] == name:
                return project
        raise Exception('project %s missing' % name)

    def get_runs(self, project):
        """
        Get a list of test runs
        """
        return self._request('GET', 'get_runs/%d' % project['id'], None)

    def get_suites(self, project):
        """
        Get a list of test suites
        """
        return self._request('GET', 'get_suites/%d' % project['id'], None)

    def get_suite(self, project, name):
        """
        Get a test suite based on test name
        """
        for suite in self.get_suites(project):
            if suite['name'] == name:
                return suite
        raise Exception('suite %s missing' % name)

    def get_run_status(self, project_name, run_name, run_id):
        """
        Get the status for a given test run for a project.  Accessable via run
        name or id.
        """
        project = self.get_project(project_name)
        runs = self.get_runs(project)
        for run in runs:
            if run_name is not None and run['name'] == run_name:
                return run
            if run_id is not None and run['id'] == run_id:
                return run
        raise Exception('missing test run name: %s' % run_name)

    def get_milestones(self, project):
        """
        Get a list of milestones for a project.
        """
        return self._request('GET', 'get_milestones/%d' % project['id'], None)

    def get_milestone(self, project, name):
        """
        Get a milestone based on name for a project.
        """
        for milestone in self.get_milestones(project):
            if milestone['name'] == name:
                return milestone
        raise Exception('missing milestone: %s' % name)

    def add_run(self, project_name, suite_name, run_name, milestone_name):
        """
        Get a test run.
        """
        project = self.get_project(project_name)
        suite = self.get_suite(project, suite_name)
        runs = self.get_runs(project)
        assert run_name not in [x['name'] for x in runs], 'name already used'

        params = {
            'suite_id': suite['id'],
            'name': run_name,
            'include_all': True
        }

        if milestone_name is not None:
            milestone = self.get_milestone(project, milestone_name)
            params['milestone_id'] = milestone['id']

        run = self._request('POST', 'add_run/%d' % project['id'], params)
        print "ok - added %d" % run['id']


def main():
    """
    Testrail command line integration tool
    """

    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument(
        '--project', type=str, required=True, help='project name')
    parser.add_argument('--username', type=str, required=True)
    parser.add_argument('--password', type=str, required=True)
    parser.add_argument(
        '--testrail',
        type=str,
        default='http://testrail.local/testrail/index.php',
        help='TestRail instance URL')

    sub = parser.add_subparsers(help='commands', dest="command")

    is_complete = sub.add_parser('is_completed', help='Check test run status')
    group = is_complete.add_mutually_exclusive_group(required=True)
    group.add_argument('--number', type=int, help='test run number')
    group.add_argument('--name', type=str, help='test run name')

    add = sub.add_parser('add', help='Add a test run')
    add.add_argument(
        '--suite', type=str, required=True, help='test suite name')
    add.add_argument('--name', type=str, required=True, help='test run name')
    add.add_argument('--milestone', type=str, required=False, help='milestone')
    args = parser.parse_args()

    rail = Testrail(args.testrail, args.username, args.password)

    if args.command == 'is_completed':
        status = rail.get_run_status(args.project, args.name, args.number)
        if status['is_completed']:
            has_failures = any(
                (status['failed_count'], status['blocked_count']))
            if has_failures:
                print "not",
            print "ok - %d passed %d failed %d blocked" % (
                status['passed_count'], status['failed_count'],
                status['blocked_count'])
            sys.exit(0)
        else:
            print "not ok - incomplete"
            sys.exit(1)
    elif args.command == 'add':
        rail.add_run(args.project, args.suite, args.name, args.milestone)
    else:
        raise Exception("unknown command: %s" % args.command)


if __name__ == '__main__':
    main()
