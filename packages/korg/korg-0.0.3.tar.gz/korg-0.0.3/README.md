Why a logstash / grok port to Python?
=====================================

I am not much into Ruby but I like the logstash approach to logfile parsing. So I want to use this in Python.

One solution would be to use the C version of logstash / grok (https://github.com/jordansissel/grok) and to write a wrapper:

* https://github.com/kiwi0530/python-grok
* https://github.com/emgee/libgrok-py

Basically grok assembles regular expressions. I already know that in Python file processing with regular expressions is blazingly fast so I choose to port it to Python. Since a grok package already exists in Python for something completely different I had to reverse engineer it. Thus the name korg.


Status
======

* Base functionality is implemented including tests
* Logstash patterns are included
* Some grok features are still missing (not sure which ones are necessary)

I made some first benchmarks to verify whether my performance requirements can be realized with this approach. Please do not use this results in any blog posts or articles since this is not a complete benchmark (from a statistical view point the sample size is way too small).


**Processing a 1.7MB apache access log with korg**

	..
	200
	200
	404
	200
	200

	real	0m0.248s
	user	0m0.172s
	sys 	0m0.040s


**Processing the same logfile with logstash**

	..
	200
	200
	404
	200
	200
	^CSIGINT received, shutting down. {:level=>:warn}

	real	0m11.752s
	user	0m23.948s
	sys 	0m0.528s

Note: both implementations read in all available patterns from the 'patterns' folder.


Resources
=========

* http://jpmens.net/2012/08/06/my-logstash-and-graylog2-notes/
* http://grokdebug.herokuapp.com/
