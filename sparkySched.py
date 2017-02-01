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
# Author: Steve Tuck (January 2017)
#

from __future__ import print_function

import configparser
from sparkpost import SparkPost
from datetime import datetime,timedelta
from sparkpost.exceptions import SparkPostAPIException

# Strip initial and final quotes from strings, if present
def stripQuotes(s):
    if s.startswith('"') and s.endswith('"'):
        s = s[1:-1]
    return s

# Get connection parameters from .ini file
config = configparser.ConfigParser()
config.read('sparkpost.ini')
apiKey = stripQuotes(config['SparkPost']['Authorization'])
uri = 'https://' + stripQuotes(config['SparkPost']['Host'])
sp = SparkPost(apiKey+'.', uri)

# Schedule this send for N seconds in the future
st = datetime.utcnow()+timedelta(seconds=300)
stStr = st.strftime('%Y-%m-%dT%H:%M:%S')
print('Scheduled send: ', stStr, ' UTC to service: ', uri)

sendObj = dict(
    recipients = ['test@sparkysched.sink.sparkpostmail.com'],
    html = '<p>Hello world</p>',
    from_email = 'stevet-test@elite.trysparkpost.com',
    subject = 'This is a scheduled transmission sent via python-sparkpost',
    track_opens = True,
    track_clicks = True,
    start_time = stStr,
    campaign = 'sparkySched Test',              # Note attribute is called campaign, not campaign_id
    return_path =  'bounces@elite.trysparkpost.com',
    metadata = {"binding":  "outbound"}
)

for i in range(0,1000):
    try:
        response = sp.transmissions.send(**sendObj)
        print('Message injected: ID='+response['id'])
    except SparkPostAPIException as err:
        print('SparkPost returned error code', err.response.status_code, ':',err.errors)
        exit(1)
