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
# Author: Steve Tuck (April 2017)
#

from __future__ import print_function
import configparser, time, json, sys, os, csv
from sparkpost import SparkPost
from datetime import datetime,timedelta
from sparkpost.exceptions import SparkPostAPIException

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

# Validate SparkPost start_time format, slightly different to Python datetime (which has no : in timezone offset format specifier)
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

# Inject the messages into SparkPost for a batch of recipients, using the specified transmission parameters
def sendToRecips(sp, recipBatch, sendObj):
    print('To', str(len(recipBatch)).rjust(5, ' '),'recips: template "'+sendObj['template']+'" start_time '+sendObj['start_time']+': ',end='', flush=True)

    # Compose in additional API-call parameters
    sendObj.update({
        'recipients': recipBatch,
        'track_opens':  True,
        'track_clicks': True,
        'use_draft_template': False
    })
    startT = time.time()
    try:
        res = sp.transmissions.send(**sendObj)
        endT = time.time()
        if res['total_accepted_recipients'] != len(recipBatch):
            print(res)
        else:
            print('OK - in', round(endT - startT, 3), 'seconds')
    except SparkPostAPIException as err:
        print('error code', err.status, ':', err.errors)
        exit(1)

# -----------------------------------------------------------------------------------------
# Main code
# -----------------------------------------------------------------------------------------
# Get parameters from .ini file
configFile = 'sparkpost.ini'
config = configparser.ConfigParser()
config.read_file(open(configFile))
cfg = config['SparkPost']
apiKey = cfg.get('Authorization', '')           # API key is mandatory
if not apiKey:
    print('Error: missing Authorization line in ' + configFile)
    exit(1)
baseUri = 'https://' + cfg.get('Host', 'api.sparkpost.com')     # optional, default to public service

# Open the adapter towards SparkPost
sp = SparkPost(api_key = apiKey, base_uri = baseUri)
print('Opened connection to', baseUri)

# Compose optional transmission parameters from the .ini file, if present
txOpts = {}
if cfg.get('Binding'):
    txOpts['metadata'] = {"binding": cfg.get('Binding')}
if cfg.get('Return-Path'):
    txOpts['return_path'] = cfg.get('Return-Path')
if cfg.get('Campaign'):
    txOpts['campaign']  = cfg.get('Campaign')
if cfg.get('GlobalSub'):
    txOpts['substitution_data'] = json.loads(cfg.get('GlobalSub'))

batchSize = cfg.getint('BatchSize', 10000)      # Use default batch size if not given in the .ini file

# Get the recipient-list filename, template ID and sending time from the command-line
# Check argument count and validate command-line input.
if len(sys.argv) >= 4:
    try:
        fh_recipList = open(sys.argv[1])
    except FileNotFoundError as Err:
        print('Error opening recipients file', Err.filename, ':', Err.strerror)
        exit(1)

    txOpts['template'] = sys.argv[2]

    txOpts['start_time'] = sys.argv[3]
    if not isExpectedDateTimeFormat(txOpts['start_time']):
        print('Unexpected date/time string value', txOpts['start_time'])
        exit(1)
else:
    printHelp()
    exit(0)

# Read the recipients from the file specified on the command line.  Build them into batches of N
print('Injecting to SparkPost:')
recipBatch = []
f = csv.reader(fh_recipList)

for r in f:
    if f.line_num == 1:                         # Check if header row present
        if 'email' in r:                        # we've got an email header-row field - continue
            hdr = r
            continue
        elif '@' in r[0] and len(r) == 1:       # Also accept headerless format with just email addresses
            hdr = ['email']
            continue
        else:
            print('Invalid .csv file header - must contain "email" field')
            exit(1)
    else:
        # Parse values from the line of the file into a row object
        row = {}
        for i,h in enumerate(hdr):
            if r[i]:                                        # Only parse non-empty fields from this line
                if h == 'email':
                    row['address'] = {h: r[i]}              # begin the address
                elif h == 'name':
                    row['address'].update(name = r[i])      # add into the existing address structure
                elif h == 'return_path':
                    row[h] = r[i]                   # simple string field
                elif (h == 'metadata' or h == 'substitution_data' or h == 'tags'):
                    row[h] = json.loads(r[i])       # parse these fields as JSON text into dict objects
                else:
                    print('Unexpected .csv file field name found: ', h)
                    exit(1)

        recipBatch.append(row)
        if len(recipBatch) >= batchSize:
            sendToRecips(sp, recipBatch, txOpts)
            recipBatch = []                     # Empty out, ready for next batch
# Handle the final batch remaining, if any
if len(recipBatch) > 0:
    sendToRecips(sp, recipBatch, txOpts)