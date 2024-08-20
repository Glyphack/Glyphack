---
title: "Pytest Dev Sprint 2024"
date: 2024-08-20T19:35:10+02:00
draft: false
tags: ["open-source"]
---

It was about 3 Months ago that a interesting message showed upon my GitHub feed.
It was from [The-Compiler](https://github.com/The-Compiler) arranging a 5 day [Pytest development sprint](https://github.com/pytest-dev/sprint/) in Austria.
I was following him for his open source work.
I finally got access to something interesting from following people whom work I like.

I did not know much about the event, my guess was that there is going to be some coding and meeting other Pytest community.
So I shared the news with [my friend](https://github.com/farbodahm), and we signed up for it.

This was the first in person open source development event I ever joined.
The uncertainty give a mix of excitement and nervousness.

The sprint was organized at [Omicron](https://www.omicronenergy.com/en/) in [Klaus, Vorarlberg](https://www.openstreetmap.org/#map=15/47.3075/9.6207).
We were staying at a hotel in Feldkirch the hotel was right above the train station.
Every morning we took a 10-minute train ride form Feldkirch to Klaus.

Other than us there were 5 pytest maintainers and 2 other contributors from Omicron. Genuinely helpful people.

I worked on two refactorings during that week.
Pytest codebase is very old, I found some pieces from 12 years ago.
These are written when a lot of python features were not introduced.
So there are a lot of improvements both to code and to functionality by using better methods that are introduced to python.

Pytest codebase is big, has a lot of features, but it was easy for me to navigate through it.
Code is kept close together, not much abstractions and mostly python structures themselves are used.
I wish software at companies were like this.

The first issue I fixed was to make pytest fixtures an actual object and showing better error messages when a fixture is used in test summary.
Previously fixtures were created by using monkey patching a function to wrap a fixture and in the code there were checks on functions to find if it is a function wrapper or not.
I replaced it with a new class to contain the fixtures, and it is then easier to check for fixtures in the code using `isinstance` calls.

The second refactor I worked on turned out to be way bigger and ambitious than I imagined.
It's related to the beautiful error messages you see when tests fail that show you debug information.
This is done by rewriting the assert statement in tests and adding additional information.
There was this file in the codebase called `assert_rewrite.py` I basically started to rewrite that file.
That file I think is one of the main reasons why pytest is so pleasant to work with.
It takes in your plain tests and rewrites the AST to make them more informative and the result is printed out. So when your test fails you see nice error message with debugging traces in the output following your test code that failed.
This genius trick required genius code. Which is hard to understand.
We wanted to make some adjustments in that part and realized there is an opportunity to rewrite it and make it simpler.
There are definitely more ways to do something that was done 11 years ago.
I don't think there is very big gains in refactoring this part.
It's more of a fun challenge and maybe the new code allow adding more features.

That week I had a great time. Felt really alive and happy.
From the morning I woke up and got ready to go and program.
The place that we had and the room full of people ready for talking about problems and reviewing your work.

I don't know why it is so much different than having a job as a programmer.
Maybe [money really ruins the joy](https://world.hey.com/dhh/i-won-t-let-you-pay-me-for-my-open-source-d7cf4568).

On the 4th day we went to visit the water power plant near Feldkirch.
A lot of stuff were mechanical.
Stats were shown in the mechanical gauges.
I don't blame them if they don't trust in software enough for this.
We can't even get basic CRUD apps to work these days.

I'm glad that I had followed Florian, and saw the announcement in my GitHub feed. Another good reason to find good people and follow them on GitHub.

Oh lastly, I started using [qutebrowser](https://qutebrowser.org/doc/quickstart.html) during this sprint. I'm very happy with my decision. It's an efficient and fast, just like vim. It works with everything except for crappy websites. For example google sometimes does not let you log in to an account from this browser (how much more they have to work to convince you that they are taking control of the web and browsers?).
But I'm using it as my development browser now. It works perfect for websites showing information. Let's see if I will start creating scripts to have fun and automate some more stuff in the browser.

Follow people you like on GitHub. On LinkedIn, you find show offs and announcements by sales and PR on GitHub you find real things.
