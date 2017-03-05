# sparkySched   
Simple command-line tool to make scheduled transmissions through SparkPost.

## Pre-requisites
Install the [python-sparkpost](https://github.com/sparkpost/python-sparkpost) library using
```
pip install sparkpost
```

Set up a sparkpost.ini file as follows.
  
```
[SparkPost]
# SparkPost.com values
Authorization = "##myAPIkey##"
```

or

```
[SparkPost]
# SparkPost Enterprise values
Authorization = "##myAPIkey##"
Host = "demo.sparkpostelite.com"
```

The `host` attribute is only needed for SparkPost Enterprise service usage; you can omit it for [sparkpost.com](https://www.sparkpost.com/).

The surrounding quotes are needed.

Replace ##myAPIkey## with your specific, private API key. 

##Usage
As written, the tool injects serially 1000 messages, with a start time scheduled for 300 seconds into the future.

The messages are destined for the [Smart Sink](https://support.sparkpost.com/customer/portal/articles/2560839-how-do-i-test-using-the-sink-server-on-sparkpost-).  They will show up as actual deliveries in your account (because they are actually getting delivered; and they count towards your account volume allowance).
```
$ ./sparkySched.py 
Scheduled send:  2017-03-05T14:24:55  UTC to service:  https://demo.sparkpostelite.com
Message injected: ID=48513559285872950
Message injected: ID=66527959062029757
Message injected: ID=30499159685870927
Message injected: ID=48513559285872951
:
:
```

##Performance considerations
You'll get the very best performance if you are able to host the tool "close" to the SparkPost injection point i.e. low latency.

A real production injector should also make use of concurrency - see [best practices](https://support.sparkpost.com/customer/portal/articles/2249268), but please note this code is deliberately sending single-recipient-per-call.

##See Also

[Transmission API call - options attributes start_time](https://developers.sparkpost.com/api/transmissions.html#header-options-attributes)

[SparkPost Developer Hub](https://developers.sparkpost.com/)

[python-sparkpost library](https://github.com/sparkpost/python-sparkpost)

[Getting Started on SparkPost Enterprise](https://support.sparkpost.com/customer/portal/articles/2162798-getting-started-on-sparkpost-enterprise)

[Smart Sink](https://support.sparkpost.com/customer/portal/articles/2560839-how-do-i-test-using-the-sink-server-on-sparkpost-)
