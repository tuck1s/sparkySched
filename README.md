# sparkySched   
Simple command-line tool to make scheduled transmissions through SparkPost using a stored template, with
- recipient list
- template ID
- sending time

specified through parameters.

## Pre-requisites
Install the [python-sparkpost](https://github.com/sparkpost/python-sparkpost) library using
```
pip install sparkpost
```

Set up a sparkpost.ini file as follows.
  
```
[SparkPost]
# SparkPost Enterprise EU values
Authorization = "##myAPIkey##"
Host = "demo.sparkpostelite.com"
Return-Path = "bounces@elite.trysparkpost.com"
Binding = "outbound"
BatchSize = "10000"
Campaign = "Daily send test 10k batches"
```

The surrounding quotes are needed.

Replace `##myAPIkey##` with your specific, private API key. 

The `host`, `Return-Path` and `Binding` attributes are only needed for SparkPost Enterprise service usage; you can omit them for [sparkpost.com](https://www.sparkpost.com/).

The `BatchSize` attribute can be left at 10000, the Best Practices article below discusses this.

The `Campaign` attribute is free format text and is helpful for filtering reports on the UI.

The tool injects messages using the specified local recipients file and existing SparkPost stored template (referred to by template_ID),  with a scheduled start time.

An example recipients file that is destined for the [Smart Sink](https://support.sparkpost.com/customer/portal/articles/2560839-how-do-i-test-using-the-sink-server-on-sparkpost-) is included for test purposes.
They will show up as actual deliveries in your account (because they are actually getting delivered; and they count towards your account volume allowance).

## Usage
```
$ ./sparkySched.py 

NAME
   ./sparkySched.py
   Simple command-line tool to trigger bulk sends through SparkPost using a stored template.

SYNOPSIS
  ./sparkySched.py recipient_list template_id sending_time

MANDATORY PARAMETERS
    recipient_list       filename, containing plain text list of email addresses
    template_id          SparkPost named template
    sending_time         In ISO format, interpreted as UTC (Greenwich Mean Time) as in YYYY-MM-DDTHH:MM:SS
                             with optional timezone offset as in YYYY-MM-DDTHH:MM:SS±HH:MM
```

## Example output

```
$ ./sparkySched.py recips_100k.csv my-dry-run 2017-03-20T19:10:00+00:00
Opened connection to https://demo.sparkpostelite.com
Injecting to SparkPost:
To 10000 recips: template "my-dry-run" binding "outbound" campaign "Daily send test 10k batches" start_time 2017-03-20T19:10:00+00:00 : OK TxID 66538125845299279 in 13.311 seconds
To 10000 recips: template "my-dry-run" binding "outbound" campaign "Daily send test 10k batches" start_time 2017-03-20T19:10:00+00:00 : OK TxID 48523727151264958 in 14.656 seconds
To 10000 recips: template "my-dry-run" binding "outbound" campaign "Daily send test 10k batches" start_time 2017-03-20T19:10:00+00:00 : OK TxID 66538125845299281 in 12.074 seconds
To 10000 recips: template "my-dry-run" binding "outbound" campaign "Daily send test 10k batches" start_time 2017-03-20T19:10:00+00:00 : OK TxID 48523727151264960 in 15.122 seconds
To 10000 recips: template "my-dry-run" binding "outbound" campaign "Daily send test 10k batches" start_time 2017-03-20T19:10:00+00:00 : OK TxID 30509328364958224 in 10.332 seconds
To 10000 recips: template "my-dry-run" binding "outbound" campaign "Daily send test 10k batches" start_time 2017-03-20T19:10:00+00:00 : OK TxID 48523727151264994 in 15.058 seconds
To 10000 recips: template "my-dry-run" binding "outbound" campaign "Daily send test 10k batches" start_time 2017-03-20T19:10:00+00:00 : OK TxID 30509328364958227 in 9.992 seconds
To 10000 recips: template "my-dry-run" binding "outbound" campaign "Daily send test 10k batches" start_time 2017-03-20T19:10:00+00:00 : OK TxID 48523727151265006 in 39.808 seconds
To 10000 recips: template "my-dry-run" binding "outbound" campaign "Daily send test 10k batches" start_time 2017-03-20T19:10:00+00:00 : OK TxID 30509328364958273 in 12.413 seconds
To 10000 recips: template "my-dry-run" binding "outbound" campaign "Daily send test 10k batches" start_time 2017-03-20T19:10:00+00:00 : OK TxID 66538125845299402 in 10.705 seconds
$
```

##Performance considerations
You'll get the very best performance if you are able to host the tool "close" to the SparkPost injection point i.e. low latency.

A real production injector should also make use of concurrency - see [best practices](https://support.sparkpost.com/customer/portal/articles/2249268), but please note this code is deliberately sending single-recipient-per-call.

## TODO / possible extensions
Global substitution data / metadata, and per-recipient data / metadata could be included via extensions to the command-line parameters and recipients file format.

##See Also

[Transmission API call - options attributes start_time](https://developers.sparkpost.com/api/transmissions.html#header-options-attributes)

[SparkPost Developer Hub](https://developers.sparkpost.com/)

[python-sparkpost library](https://github.com/sparkpost/python-sparkpost)

[Getting Started on SparkPost Enterprise](https://support.sparkpost.com/customer/portal/articles/2162798-getting-started-on-sparkpost-enterprise)

[Smart Sink](https://support.sparkpost.com/customer/portal/articles/2560839-how-do-i-test-using-the-sink-server-on-sparkpost-)
