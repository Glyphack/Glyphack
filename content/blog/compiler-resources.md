---
title: "Compilers Resources"
date: 2023-09-15T19:50:19+02:00
draft: false
tags: [compilers] 
---

This post is a compilation of great resources I found while building a type checker for Python. 
These resources are free and highly focused on specific topics, making them ideal for learning by doing rather than sifting through extensive materials.

## Parser

When it comes to writing a parser, your approach depends on your project's goals.
For compilers or interpreters, you can use a parser generator.
However, if you're working on tools like formatters or language servers, your parser needs to handle broken code gracefully.

- [**"Write JS Parser in Rust"**](https://boshen.github.io/javascript-parser-in-rust/) by Boshen is an excellent introductory guide.
- For resilient parsing, check out this tutorial on [**resilient LL parsing**](https://matklad.github.io/2023/05/21/resilient-ll-parsing-tutorial.html).
- Your language's official documentation. For Python, there is [**Python AST module**](https://docs.python.org/3/library/ast.html).
- If you're interested in RustPython, they offer an example implementation of a lexer [**here**](https://rustpython.github.io/website/rustpython_parser/index.html).

## Stanford Compilers Class

For a comprehensive understanding of relevant topics, consider following the [**Stanford Compilers Class**](http://openclassroom.stanford.edu/MainFolder/CoursePage.php?course=Compilers). Although I haven't watched it personally, I found this [**guide**](https://pgrandinetti.github.io/compilers/) based on the class quite helpful.

## Crafting Interpreters

It goes without saying that [**"Crafting Interpreters"**](https://craftinginterpreters.com/) is an indispensable resource for this journey. I recommend reading it chapter by chapter as you build your project.


## Symbol Table

This [**series on the Python symbol table implementation**](https://eli.thegreenplace.net/2010/09/18/python-internals-symbol-tables-part-1/)
from Eli Bendersky is useful for learning how does a symbol table works:

- RustPython's [**SymbolTable**](https://rustpython.github.io/website/rustpython_compiler/symboltable/struct.SymbolTable.html) implementation.

## Semantic Analyzer

While resources specific to the semantic analysis phase are scarce, you can find inspiration and solutions in existing projects:

- MyPy offers valuable insights into semantic analysis on their [**wiki**](https://github.com/python/mypy/wiki/Semantic-Analyzer).
- Pyright's [**binder.ts**](https://github.com/microsoft/pyright/blob/eb98cdda4ecfb4d2ce2fb1d4b9ce7848ab439c32/packages/pyright-internal/src/analyzer/binder.ts) is another resource worth exploring.

## Type Checking

To delve deeper into type checking, it's often best to study code from various projects:

- Check out the design of [**pyanalyze**](https://github.com/quora/pyanalyze/blob/master/docs/design.md) for Python.
- For MyPy, the [**Type Checker**](https://github.com/python/mypy/wiki/Type-Checker) wiki provides valuable insights.
- Dive into the internal details of the [**Jedi language server**](https://github.com/quora/pyanalyze/blob/master/docs/design.md).

## Programming Language Zoo

If your language closely resembles one of those in the [**Programming Languages Zoo**](https://plzoo.andrej.com/language/poly.html), studying their code can be immensely helpful due to their brevity and simplicity.

## Explaining Rust Analyzer

For a comprehensive understanding of language servers, file systems, updates, and testing, check out this [**YouTube playlist**](https://www.youtube.com/playlist?list=PLhb66M_x9UmrqXhQuIpWC5VgTdrGxMx3y).

## LSP (Language Server Protocol)

Implementing the Language Server Protocol (LSP) can be simplified with [**Tower LSP**](https://github.com/ebkalderon/tower-lsp), a powerful tool for quick setup. If you choose to implement the LSP protocol yourself, you can use it as a reference.

## Oxc

you can explore the [**oxc GitHub repository**](https://github.com/web-infra-dev/oxc). This repository provides a great implementation of a set of JS tools.
You can delve into different packages within the codebase to understand the design patterns used for each part and how they are implemented.


## Final Words

After this journey I found out that nothing is more fun than compilers.
If you know more resources, please send them to me.
