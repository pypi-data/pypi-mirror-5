===============================
PyJenkins
===============================

Python wrapper around the Jenkins JSON API

* Free software: MIT license
* Documentation: http://jenkins.rtfd.org.

Features
--------

Query Jenkins jobs and builds, and trigger a build.


Installation
------------

    pip install pyjenkins

Usage
-----

    >>> from pyjenkins import Jenkins
    >>> jenkins = Jenkins("http://jenkins.example.com/", 'username', 'password')
    >>> job = jenkins.get_job_by_name('my-job')
    >>> build = job.build('auth-token')
    >>> build.started
    False
    ...
    >>> build.refresh()
    >>> build.started
    True
    >>> build.complete
    False
    >>> build.estimated_duration
    60234
    ...
    >>> build.complete
    True
    >>> build.successful
    True
