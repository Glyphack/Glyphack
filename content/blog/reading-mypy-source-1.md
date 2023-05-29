---
title: "Reading Mypy Source 1"
date: 2023-05-26T20:08:09+02:00
draft: true
tags: []
---

Import resolution: default is to follow
ignore missing
std lib imports
3rd party imports

Finds all the sources and pass to type
checker
<https://github.com/python/mypy/blob/ac6dc18545c9eafbf576e1151f7f698ec1f1b256/mypy/find_sources.py#L21>

### Builder

Creates a path to where we can search for type files. Python interpreter, 3rd party libs, and user files.

Build manager is the object doing all the work
<https://github.com/python/mypy/blob/ac6dc18545c9eafbf576e1151f7f698ec1f1b256/mypy/build.py#L550>

? checking for presence of some modules from the type. why?
<https://github.com/python/mypy/blob/ac6dc18545c9eafbf576e1151f7f698ec1f1b256/mypy/build.py#L658>

Might be interesting Check dump graph
<https://github.com/python/mypy/blob/ac6dc18545c9eafbf576e1151f7f698ec1f1b256/mypy/build.py#L2896>

This is what happens after build is called:
<https://github.com/python/mypy/blob/master/mypy/build.py#LL1674C3-L1674C3>

The actual dispatch, here we also create dep graph for files.
<https://github.com/python/mypy/blob/ac6dc18545c9eafbf576e1151f7f698ec1f1b256/mypy/build.py#L2868>
