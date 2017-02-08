# Test Rail integration tool

A command line tool to allow programatic creation of test runs within Test Run.

# USAGE
    usage: testrail.py [-h] --project PROJECT --username USERNAME --password
        PASSWORD [--testrail TESTRAIL]
        {is_completed,add} ...


    usage: testrail.py add [-h] --suite SUITE --name NAME --milestone MILESTONE

    optional arguments:
      -h, --help             show this help message and exit
      --suite SUITE          test suite name
      --name NAME            test run name
      --milestone MILESTONE  milestone

    usage: testrail.py is_completed [-h] (--number NUMBER | --name NAME)

    optional arguments:
      -h, --help       show this help message and exit
      --number NUMBER  test run number
      --name NAME      test run name

# Available commands

## add
Given a project, test suite, and milestone, adds a test run

### Example output

    ok - added <TEST_RUN_ID>

### Results

* Exit code of 0 indicates successful creation of the test run.  Any other exit code indicates failure to create the test run.
* Upon success, the test run identifier can be determined via the output.


## is_completed
Given a project and either a test run name or test run number, gives the status.

### Example output

    <status> - <number_passed> passed <number_failed> failed <number_blocked> blocked

### Results
* Exit code of 0 indicates the test run completed.  Exit code of 1 indicate communication failure or test run is incomplete.
* Success or failure is determined via TAP like output.  Lines beginning with "ok" indicate success.  Lines beginning with "not ok" indicate failure.


# Example uses:

    $ python testrail.py --username USERNAME --password PASSWORD --project "My Project" is_completed --name "Release Test Suite 2017-02-07"
    not ok - 16 passed 1 failed 3 blocked
    $ echo $?
    0
    $

    $ python testrail.py --username USERNAME --password PASSWORD --project "My Project" is_completed --number 16
    ok - 14 passed 0 failed 0 blocked
    $ echo $?
    0
    $

    $ python testrail.py --username USERNAME --password PASSWORD --project "My Project" is_completed --number 19
    not ok - incomplete
    $ echo $?
    1
    $

    $ python testrail.py --username USERNAME --password PASSWORD --project "My Project" add --name "Release Test Suite 2017-02-08" --suite "Master Release Test" --milestone "Spiral 9 Sprint 2"
    ok - added 19
    $ echo $?
    0
    $
