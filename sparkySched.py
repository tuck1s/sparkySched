#!/usr/bin/env python3
#SparkPost example - manage scheduled transmissions via command-line
#Copyright  2017 SparkPost

#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

#
# Author: Steve Tuck (March 2017)
#

from __future__ import print_function
import configparser, time, json, sys, os
from sparkpost import SparkPost
from datetime import datetime,timedelta
from sparkpost.exceptions import SparkPostAPIException

# Strip initial and final quotes from strings, if present
def stripQuotes(s):
    if s.startswith('"') and s.endswith('"'):
        s = s[1:-1]
    return s

def printHelp():
    progName = sys.argv[0]
    shortProgName = os.path.basename(progName)
    print('\nNAME')
    print('   ' + progName)
    print('   Simple command-line tool to trigger bulk sends through SparkPost using a stored template.\n')
    print('SYNOPSIS')
    print('  ./' + shortProgName + ' recipient_list template_id sending_time\n')
    print('MANDATORY PARAMETERS')
    print('    recipient_list       filename, containing plain text list of email addresses')
    print('    template_id          SparkPost named template')
    print('    sending_time         In ISO format, interpreted as UTC (Greenwich Mean Time) as in YYYY-MM-DDTHH:MM:SS')
    print('                             with optional timezone offset as in YYYY-MM-DDTHH:MM:SS±HH:MM')

# Check/enforce SparkPost's native start_time format, which is slightly different to Python's
def isExpectedDateTimeFormat(timestamp):
    format_string = '%Y-%m-%dT%H:%M:%S%z'
    try:
        colon = timestamp[-3]
        if not colon == ':':
            raise ValueError()
        colonless_timestamp = timestamp[:-3] + timestamp[-2:]
        datetime.strptime(colonless_timestamp, format_string)
        return True
    except ValueError:
        return False

# Inject the messages into SparkPost for a batch of recipients, using a named template, binding, and campaign ID
# Global substitution data is applied, along with a start_time for scheduled sending.
def sendToRecips(sp, recipBatch, template, binding, campaign, globalSubData, returnPath, startTime):
    print('To', str(len(recipBatch)).rjust(5, ' '),
          'recips: template "' + template + '" binding "' + binding + '" campaign "' + campaign + '" start_time ' + startTime + ' : ',
          end='', flush=True)

    sendObj = dict(
        recipients=recipBatch,
        template=template,  # this sets the friendly-from and subject line
        track_opens=True,
        track_clicks=True,
        use_draft_template=False,
        start_time=startTime,
        campaign=campaign,  # Note attribute is called campaign, not campaign_id
        return_path=returnPath,
        metadata={"binding": binding},
        substitution_data=globalSubData
    )
    startT = time.time()
    try:
        response = sp.transmissions.send(**sendObj)
        endT = time.time()
        print('OK TxID', response['id'], 'in', round(endT - startT, 3), 'seconds')
    except SparkPostAPIException as err:
        print('error code', err.status, ':', err.errors)
        exit(1)

# -----------------------------------------------------------------------------------------
# Main code
# -----------------------------------------------------------------------------------------
# Get parameters from .ini file
# Get connection parameters from .ini file
config = configparser.ConfigParser()
config.read('sparkpost.ini')
p = dict(
    apiKey = stripQuotes(config['SparkPost']['Authorization']),
    uri = 'https://' + stripQuotes(config['SparkPost']['Host']),
    binding = stripQuotes(config['SparkPost']['Binding']),
    returnPath = stripQuotes(config['SparkPost']['Return-Path']),
    batchSize = int(stripQuotes(config['SparkPost']['BatchSize'])),
    campaign  = stripQuotes(config['SparkPost']['Campaign']),
)

# Get the recipients, today's deals, and sending time from the command-line
# Check argument count and validate command-line input.  If a file cannot be opened, then Python will raise an exception
if len(sys.argv) >= 4:
    try:
        fh_recipList = open(sys.argv[1])
    except FileNotFoundError as Err:
        print('Error opening recipients file', Err.filename, ':', Err.strerror)
        exit(1)

    # Get today's selected deal IDs as integers
    templateID = sys.argv[2]

    timeString = sys.argv[3]
    if(not isExpectedDateTimeFormat(timeString)):
        print('Unexpected date/time string value', timeString)
        exit(1)
else:
    printHelp()
    exit(0)

# Open the 'adapter' towards SparkPost
sp = SparkPost(p['apiKey'], p['uri'])
print('Opened connection to',p['uri'])

# Read the recipients from the file specified on the command line.  Build them into batches of N
print('Injecting to SparkPost:')
gs = {}                                         # Fully formed template - no global substitution data required
recipBatch = []
for r in fh_recipList:
    recipBatch.append(r.rstrip() )              # strip the trailing newline character
    if(len(recipBatch) >= p['batchSize'] ):
        sendToRecips(sp, recipBatch, templateID, p['binding'], p['campaign'], gs, p['returnPath'], timeString)
        recipBatch = []                         # Empty out, ready for next batch

# Handle the final batch remaining, if any
if(len(recipBatch) > 0):
    sendToRecips(sp, recipBatch, templateID, p['binding'], p['campaign'], gs, p['returnPath'], timeString)