---
title: "A better go test"
date: 2024-08-24T15:15:06+02:00
draft: false
tags: [projects]
---

My job now involves doing some Golang work and this post is about how `go test` command can be improved.

Until now, I never actually thought about improving the test command for a language.
But with Golang I have serious problems with reporting test results on command line.
Test output is not readable, The usual test flags you expect are not there.

- [Fail fast option does not work](https://github.com/golang/go/pull/62714)
- [You cannot see the list of failed tests](https://stackoverflow.com/questions/25380799/listing-of-pass-and-failed-test-cases-in-go)
- [Does not offer rerun options like pytest](https://docs.pytest.org/en/7.1.x/how-to/cache.html)

I noticed the problem when I started working on a quite large golang project with a lot of tests.
When I run the tests it starts printing a lot of information, most of it are not important.

I found [gotestsum](https://github.com/gotestyourself/gotestsum) package which seems to do what I want.
I like it, but it seems to focus on other things that I don't find problematic.
For example, it has watch option, which is not really needed for the test runner.
You have other tools to watch and run commands.

Happy that I found an opportunity I created [gotest](https://github.com/Glyphack/gotest).
It's a very simple tool. It takes in the output of `go test` command and organizes output to a human friendly output. I'm planning to add more commands and see how far can I improve the testing on CLI. You don't have to install an IDE just for running tests easily, it's not Java.


**Why not contributing to Golang?**

I think some of these features could be added in the `go test`, and I'm going to use this project as an experiment to see how they turn out to be.


If you are interested let me know.
