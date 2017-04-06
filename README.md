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

Set up a basic sparkpost.ini file:
```ini
[SparkPost]
Authorization = ##myAPIkey##
```

Replace `##myAPIkey##` with your specific, private API key. 

The full suite of options is as follows:
```ini
[SparkPost]
Authorization = ##myAPIkey##
Host = demo.sparkpostelite.com

#Campaign setup
Binding = outbound
Campaign = avocado-saladcopter
Return-Path = bounces@elite.trysparkpost.com
GlobalSub = {"subject": "Fresh avocado delivered to your door in 30 minutes by our flying saladcopter"}
BatchSize = 2000
```
The `Host`, `Binding` and `Return-Path` attributes are needed for SparkPost Enterprise service usage; you can omit them for [sparkpost.com](https://www.sparkpost.com/).

The `BatchSize` attribute is optional.  If omitted, a default of 10000 is used. The Best Practices article below discusses this.

The `Campaign` attribute is optional, free format text and is helpful for filtering reports on the UI.

The `GlobalSub` attribute is optional, JSON-formatted text, enabling you to set [template substitution values](https://developers.sparkpost.com/api/substitutions-reference.html)

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
$ ./sparkySched.py recips_100k.csv avocado-goodness 2017-04-06T12:35:00+01:00
Opened connection to https://demo.sparkpostelite.com
Injecting to SparkPost:
To 10000 recips: template "avocado-goodness" start_time 2017-04-06T12:35:00+01:00 : OK TxID 48535365195681112 in 8.143 seconds
To 10000 recips: template "avocado-goodness" start_time 2017-04-06T12:35:00+01:00 : OK TxID 66549763839380444 in 6.076 seconds
```

## Performance considerations
You'll get the very best performance if you are able to host the tool "close" to the SparkPost injection point i.e. low latency.

A real production injector can also make use of concurrency - see [best practices](https://support.sparkpost.com/customer/portal/articles/2249268).

## TODO / possible extensions
Per-recipient data / metadata could be included via extensions to the command-line parameters and recipients file format.

## See Also

[Transmission API call - options attributes start_time](https://developers.sparkpost.com/api/transmissions.html#header-options-attributes)

[SparkPost Developer Hub](https://developers.sparkpost.com/)

[python-sparkpost library](https://github.com/sparkpost/python-sparkpost)

[Getting Started on SparkPost Enterprise](https://support.sparkpost.com/customer/portal/articles/2162798-getting-started-on-sparkpost-enterprise)

[Smart Sink](https://support.sparkpost.com/customer/portal/articles/2560839-how-do-i-test-using-the-sink-server-on-sparkpost-)
