---
title: "Dev Tools at Work"
date: 2024-12-29T19:32:07+01:00
draft: false
tags: []
---

I was reading this old post from Brad Fitzpatrick, talking about why he thought open source contributors suddenly disappear after joining Google:

> - They're busy. Google seems to suck everybody's free time, and then some. It's not that Google is forcing them to work all the time, but they are anyway because there are so many cool things that can be done. I often joke that I have seven 20% projects.
> - The Google development environment is so nice. The source control, build system, code review tools, debuggers, profilers, submit queues, continuous builds, test bots, documentation, and all associated machinery and processes are incredibly well done. It's very easy to hack on anything, anywhere and submit patches to anybody, and notably: to find who or what list to submit patches to. Generally submitting a patch is the best way to even start a discussion about a feature, showing that you're serious, even if your patch is wrong.

<https://brad.livejournal.com/2409049.html>

I cannot imagine how the work is so fun there than people vanish into the air after joining google.
Or how someone gets caught up in seven different 20% projects because the environment lets you do that much work.

I like being busy when there is a lot to work on.
Most of the time what happens is that people are busy because they are kept busy by the tasks around work.

Let me tell you a story about John. (It's not a real John.)

John works at a 50 people company. He works on tools for sales and marketing to do their work faster.
His tools are mostly scripts. He makes a website to make the interaction with scripts easier.

One day he has an idea of a new mini product.
Nothing earth-shattering, mind you - just a simple integration between two tools that would save the marketing team from having to copy-paste discount codes. In Brad's Google utopia, John would just write the code, submit a patch, and boom - problem solved, everyone's happy.

First, John has to talk to Sarah. But wait, he can't just _talk_ to Sarah.
That would be far too efficient.
He has to go through Sarah's manager, who needs to talk to Sarah, who then needs to talk back to her manager, who needs to update some road map that probably hasn't been looked at since last OKR planning.

So this simple conversation that could lead to a possibly good thing cannot happen simply.
It Needs to happen in a group chat when everyone says their opinion (which takes time from the readers as well as the author) and have some back and forth discussion.

Because of this John has to be more thoughtful about the suggestions.
It's okay to suggest something not useful a few times but if it becomes a couple of times per week then everyone will get tired from him.

Although he does not actively give ideas and prototype them. He posts a few every month or so, then he goes off writing a long proposal for both teams to accept it and then moves it to their engineering road map to be done somewhere in the next months.
He's lucky if he can deliver 1 of his suggestions every quarter.
This seems dangerous, he might get fired right?
No, John's a hero because he's mastered the art of producing artifacts - not actual, useful code, mind you, but the kind of artifacts that look good in performance reviews. Meeting notes. Project proposals. Progress updates. It's like a cargo cult of productivity.

Few months later the something similar happens.
Sarah wants a small new feature to make her work more enjoyable.
Engineering and sales teams chat, they decide that this bug is not easy to fix.
But there is an easy work around that adds few more steps to Sarah's work.
So they decide to fix the bug when the engineering team has some free time.
The free time definitely does not happen a lot.
Sarah's work is not much slower but it's annoying, she might make a mistake because someone else product is not working.
But it's hard to measure how annoying the product is in numbers, so people only measure the time it saves from the work.

---

I've seen this story happening over and over again, and I've been on the both sides.

John can't even prototype the damn thing. Because in this brave new world of corporate efficiency, actually _building something_ to see if it works is considered too risky. Better to spend six months writing proposals about the thing you want to build than actually building it in a week to see if it's any good.

I'm not saying all planning, design, and management is unnecessary.
It's definitely easier to do it right at the beginning than to migrate a live system.
I'm okay with thinking carefully about these critical components.
Instead of slowing down everything, just try out most of the stuff but think about irreversible or hard to migrate decisions like how data is stored.

Also doing something gives you more information.
The feedback from acting tells where to go next.
This is something you don't get as much from sitting and discussing an idea.

If people don't have the authority to prototype something then the rate of generating and trying out ideas will decrease.
A lot of times the ideas will not be useful and be discarded.
Trying out ideas teaches people and give them more experience.
Makes them better in generating next ideas.
Just shipping the thing and deciding what to do next is faster and more fun.

We should allow people use their curiosity and don't block them with processes.

**Having good tools**

There are countless times I found projects that have out-of-date documents, misconfigured tools, examples that won't run anymore.
I honestly have no idea how someone can be maintaining a project where `Makefile` is broken. Do you even use it?

It takes time and skill to create and maintain good tools.
And I think the reason is that the incentive for working on tools is not there.
The author of the projects make this beautiful `README`, Makefile, example code that would make everyone get up and running with project in seconds. Why? Because they're trying to get that promotion

Fast-forward six months and the project document is out of date, the Makefile is so broken that you make your own scripts to work on the project.
When tools and projects don't have good developer tools you can't just start working on a project to evaluate an idea.
Want to try out a new idea on the codebase? Good luck with that.

The typical experience goes something like this: you clone the repo (assuming you can find it), follow the setup instructions, and then you hit some obscure error message as result of mixing 10 tools. With the poor error handling you have to dig in the code, find which one is not working as expected and start fixing code or your environment.

And this isn't just annoying - it's toxic to innovation. How the hell is anyone supposed to prototype big ideas when they can't even get the damn thing to compile?

Document the contributing process. Constantly update the docs and review that in the code review.
Make sure the examples work, the tools integrate nicely in a project.
For example if your project has a debugger make sure your changes won't break the debugger.
Make sure the app runs locally.
Test this whenever someone new joins the team.

You know what? Maybe we should try out this crazy idea of letting people actually do work and see the result.
I'm just saying, MAYBE, MAYBE just doing something helps you find out if something is good.
Maybe just write the documentation and update it instead of writing proposals about writing documentations and how the build system should work (when it's broken).

---

I'm sad that I haven't worked at a place that matches what Brad said about Google. But it's probably about google at that time and things might be different now.
The bright side is that open source is much better these days. I experienced this in open source projects. Good tools, fast builds, and great developer setup guides.
People care about good experience there.

P.S. If you're reading this from Google circa 2009, please send help. And your build system and your developer tools.
