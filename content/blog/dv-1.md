---
title: "Devlog 0001: Contributing to Ruff, Profiling, Python Types Conformance Tests"
date: 2024-02-03T10:56:48+01:00
draft: false
tags: ["devlog"]
---

Last week I wanted to start contributing to rust.
I was working on Adding [uninitialized attribute access check](https://github.com/astral-sh/ruff/pull/9513) to Ruff.

I did it and learned a lot about how to track attributes in Python code.
A gist of it would be, you need to go over the class, in each function when something is assigned to a name you need to check if that name is self or cls.
And you do this by checking if it matches the first argument of that function.
Then if the function is a class method it's cls and otherwise self.

I also learned about profiling.
After finishing the implementation I realized the benchmarks are failing.
So I need see how did I mess up the performance. It is not because of the rule but because of the code I added to the visitor to keep track of attribute initialization and access.
But first we need to profile.

I found two resources for doing it.
Maybe I can do a separate note on Rust profiling.
[Rust Performance Book](https://nnethercote.github.io/perf-book/) which has a profiling section.
[Amazing guide for Ruff Only](https://docs.astral.sh/ruff/contributing/#profiling-projects)

The interesting part is that Macos is not good for profiling, or at least I could not easily learn to use the tools.
I used cargo instruments, the output can be opened with instruments app. Instruments app is dog shit.
I expected some kind of home page, documentation or something when I search for it like [this](https://jetbrains.com/help/idea/profiler-intro.html).
But nothing.

So I could not find traces for the functions I added(skill issue.) I gave up.

In the end I ended up using [Samply](https://github.com/mstange/samply) which was better.

I also used the cargo benchmark and [critcmp](https://github.com/BurntSushi/critcmp) to compare results between my commits and found the perf issue.

It was caused because I added a new vector to each scope to keep track of undefined attribute accesses.
But I realized I can just have a global vector for the whole file and store the undefined attribute along with it's scope.

With a vector on every scope and many allocations:

```
linter/default-rules/large/dataset.py       1.00    455.7±6.28µs    89.3 MB/sec    1.14   519.6±19.69µs    78.3 MB/sec
linter/default-rules/numpy/ctypeslib.py     1.00     86.9±1.62µs   191.5 MB/sec    1.14     99.3±6.53µs   167.8 MB/sec
linter/default-rules/numpy/globals.py       1.00     12.5±0.19µs   236.4 MB/sec    1.05     13.1±0.10µs   225.1 MB/sec
linter/default-rules/pydantic/types.py      1.00    194.5±4.85µs   131.2 MB/sec    1.16   226.3±42.70µs   112.7 MB/sec
linter/default-rules/unicode/pypinyin.py    1.00     31.7±0.29µs   132.6 MB/sec    1.06     33.7±1.64µs   124.7 MB/sec
```

After using a global vector for the whole program:

```
linter/default-rules/large/dataset.py       1.00    455.7±6.28µs    89.3 MB/sec    1.03    469.9±5.46µs    86.6 MB/sec
linter/default-rules/numpy/ctypeslib.py     1.00     86.9±1.62µs   191.5 MB/sec    1.02     88.8±1.47µs   187.6 MB/sec
linter/default-rules/numpy/globals.py       1.00     12.5±0.19µs   236.4 MB/sec    1.04     13.0±0.10µs   227.1 MB/sec
linter/default-rules/pydantic/types.py      1.00    194.5±4.85µs   131.2 MB/sec    1.03    201.2±4.70µs   126.8 MB/sec
linter/default-rules/unicode/pypinyin.py    1.00     31.7±0.29µs   132.6 MB/sec    1.03     32.7±0.28µs   128.7 MB/sec
```

I also learned that codespeed is a wonderful tool for exploring performance changes between my commits.
[Example](https://codspeed.io/astral-sh/ruff/branches/Glyphack:linter-pylint-E0203), next time I use this.

For enderpy I was looking for a test suite that I can develop against until my type checker is complete.
Luckily it exists! You can view it [here](https://github.com/python/typing/tree/main/conformance).
It does not have a basic test case were you only have functions and variables but that one is easy to come up with myself.
