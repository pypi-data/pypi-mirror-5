Lending Club Auto Investing Tool
================================

A simple python tool used to watch your LendingClub account and automatically invest and reinvest cash as it becomes available based on a series of personalized investment options and settings.


Disclaimer
==========

I have tested this tool to the best of my ability, but understand that it may have bugs. Use at your own risk!


Why?
====

I built this tool to solve the common annoyance when investing money in
LendingClub. When not all the loans get funded, it becomes a two steps
forward, one step back process of reinvesting the cash every few days
until it's all invested. For large sums of money this process can take
over a month to complete.


How it works
============

When running, it will monitor your account for available cash. If the available cash meets or exceeds a minimum amount you define, it's all automatically invested into a collection of loans that match the criteria that you have set (average interest rates, rate grades, term length, etc.). See the *Options* section for information on these settings.

To put it simply, the tool does the same thing as if you were to:

* Log into your account
* Click Invest and select any filters you want to use
* Select an average interest rate portfolio you want to invest in
* Now click Continue and to through the following two pages to invest in that portfolio.


Source
======

Find the latest version on github: https://github.com/jgillick/LendingClubAutoInvestor

Feel free to fork and contribute!


Requirements
============

* python-daemon
* requests
* beautifulsoup4
* html5lib
* argparse

These can automatically be installed with `pip <http://www.pip-installer.org/en/latest/>`_::

    sudo pip install python-daemon requests beautifulsoup4 html5lib argparse


Install
=======

The tool can be run directly from the bin directory *or* installed globally, by running::

    sudo python ./setup.py install

It can also be installed with PIP::

     sudo pip install lcinvestor


Running
=======

Foreground
----------

To start the tool in the foreground::

    $ lcinvestor

The script will run continuously and print all the output to the screen until you exit it with CTRL+C.

Background (daemon)
-------------------

To run it as a background daemon::

    $ lcinvestor start

All output will be sent to ``/var/log/daemon.log``.

To stop the daemon run::

    $ lcinvestor stop

Help and Usage
--------------

To see the usage info::

    $ lcinvestor --help


Options
=======

When you run the tool, it will take you though a series of prompts to define how to invest your cash.

Email / Password
----------------

This is the email and password you use to sign into LendingClub. Your password will be kept in memory but *never* saved to file.

Minimum cash
------------

When the auto investor runs it will attempt to invest **ALL** available cash in your account into a investment portfolio. This option tells the tool how much money should be in the account before investing. i.e. What is the *minimum* amount of cash you want to invest at a time. For example, $25 can only be invested in a single loan note, whereas $1000 could be invested across up to 40 notes.

Min/Max Percent interest rate
-----------------------------

When the minimum available cash option is met, the auto investor will query the LendingClub API and get a list of possible investment portfolios available at that moment. To pick the appropriate one for you, it needs to know what the minimum and maximum *AVERAGE* interest rate value you will accept. The investment option closest to the maximum value will be chosen and all your available cash will be submitted to it.

This value relates to finding a investment portfolio using the slider on the `Invest page <https://www.lendingclub.com/portfolio/autoInvest.action>`_ on LendingClub.com. It's not possible, at any given time, to define an absolute interest rate value, so we need to know the range that you will accept.

**Note** This does *NOT* filter out individual notes based on interest rate. It defines the average interest across all notes. Use the Advanced Filters to filter out notes by loan grade.

Named portfolio
---------------

You can choose to have all new investments assigned to a named portfolio. You can either choose an existing portfolio or create a new one.

Advanced Filters
----------------

The advanced filters section brings in a few of the filters from the `Invest page <https://www.lendingclub.com/portfolio/autoInvest.action>`_ on LendingClub, such as:

* Filter by loan grade (A - G)
* Exclude loans you're already invested in
* Include loans by their funding progress
* Filter by term length (36 - 50 months)

Final Review
------------

After all the options are set, you will be given a review screen to verify those values. If you approve, type ``Y + <Enter>`` to start the program. It will now check your account every 30 minutes to see if there is enough available cash in your account to invest.


Help out
========

Please help me by forking and committing enhancements!


License
=======
The MIT License (MIT)

Copyright (c) 2013 Jeremy Gillick

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
