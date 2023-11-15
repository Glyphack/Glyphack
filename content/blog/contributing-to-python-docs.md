---
title: "TIL Secret to Open Source Contribution & Contributing to Python Docs"
date: 2023-09-19T22:23:48+02:00
draft: false
tags: [TIL] 
---

I think I learned something about contributing to open source that, if I knew a couple of years back, I could have done much more open source contributions.

A while back, I started creating a [hand-written parser for Python](https://github.com/Glyphack/enderpy).
I ended up also contributing some fixes to Python docs.
This was particularly interesting to me because it did not require really advanced knowledge, and the stuff there that was incorrect or outdated had been there for years.
So why didn't I do this earlier?

It was because I never exposed myself to the opportunity.
I usually avoided reading docs from start to finish or diving into the code of the tool I was using.

The [first](https://github.com/python/cpython/pull/104986) & [second PR](https://github.com/python/cpython/pull/104986) were the result of reading the grammar and `ast` package docs and finding inconsistencies.

Also after I was working on my type checker I started reading PEPs and playing around with other Python type checkers such as pyright.
Then suddenly ( I found )[https://github.com/quora/pyanalyze/issues/707] a rule in PEP-586(https://peps.python.org/pep-0586/#illegal-parameters-for-literal-at-type-check-time)
which was not possible to implement with Python ast structure.
I haven't started an issue for this one yet because it requires more effort but it's another opportunity.

I think that when we start programming journey, it's best to be exposed to these opportunities of reading the actual framework/tool documentation.
Or just, in general, look more into the source/docs rather than reaching for tutorials.
