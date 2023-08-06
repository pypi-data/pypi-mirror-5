===================
Django Cron Monitor
===================

Django Cron Monitor is a Django app that provides a web dashboard and script for monitoring arbitrary cron jobs. It is intended for use on a Unix environment.

More detailed documentation and set-up are in the "docs/html" directory.

Features
============
* Tracks the start time, run time, and exit codes of commands
* Color codes output based on whether it is from standard out or standard error
* Can send email based on a job's exit code and standard error output
