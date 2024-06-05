---
title: "Compilers Resources"
date: 2023-09-15T19:50:19+02:00
draft: false
tags: [compilers] 
---

This post is a compilation of great resources I found while building a type checker for Python. 
These resources are free and highly focused on specific topics, making them ideal for learning by doing rather than going through extensive materials.

## Parser

When it comes to writing a parser, your approach depends on your project's goals.
For compilers or interpreters, you can use a parser generator.
However, if you're working on tools like formatters or language servers, your parser needs to handle broken code gracefully. This can be either done with a tool like treesitter that can handle broken code to some extent and also by writing your own. Of course writing your own is more fun.

- [**"Write JS Parser in Rust"**](https://boshen.github.io/javascript-parser-in-rust/) by Boshen is an excellent introductory guide.
- For resilient parsing, check out this tutorial on [**resilient LL parsing**](https://matklad.github.io/2023/05/21/resilient-ll-parsing-tutorial.html).
- Your language's official documentation. For Python, there is [**Python AST module**](https://docs.python.org/3/library/ast.html).
- Look into implementation of open source linters or compilers. [**RustPython Lexer**](https://github.com/RustPython/Parser/blob/main/parser/src/lexer.rs) is a good one for python.

## Compilers & Interpreters

[**"Crafting Interpreters"**](https://craftinginterpreters.com/) is an essential resource for compilers. I recommend reading it chapter by chapter as you build your project.

For a comprehensive understanding of relevant topics, consider following the [**Stanford Compilers Class**](http://openclassroom.stanford.edu/MainFolder/CoursePage.php?course=Compilers). Although I haven't watched it personally, I found this [**guide**](https://pgrandinetti.github.io/compilers/) based on the class quite helpful.

Reading through finished implementations is pretty important. 
[**Programming Languages Zoo**](https://plzoo.andrej.com/language/poly.html) is one resource for this.

### Symbol Table

For symbol table you need to check the language implementation and know the scoping rules, private/public, and different kinds of symbols. There's no all in one solution.

This [**series on the Python symbol table implementation**](https://eli.thegreenplace.net/2010/09/18/python-internals-symbol-tables-part-1/)
from Eli Bendersky is useful for learning how does a symbol table works.

- RustPython's [**SymbolTable**](https://rustpython.github.io/website/rustpython_compiler/symboltable/struct.SymbolTable.html) implementation.

## Semantic Analyzer

While resources specific to the semantic analysis phase are scarce, you can find inspiration and solutions in existing projects:

- MyPy [**wiki**](https://github.com/python/mypy/wiki/Semantic-Analyzer).
- Pyright's [**binder.ts**](https://github.com/microsoft/pyright/blob/eb98cdda4ecfb4d2ce2fb1d4b9ce7848ab439c32/packages/pyright-internal/src/analyzer/binder.ts) is an example of you would do it.

## Type Checking

For type checking you are mostly interested in the type rules in that language.
Therefore it's good to check other type checker implementations.
They will teach you the rules and how to do it.

- design of [**pyanalyze**](https://github.com/quora/pyanalyze/blob/master/docs/design.md) for Python.
- For MyPy, the [**Type Checker**](https://github.com/python/mypy/wiki/Type-Checker) wiki.
- internal details of [**Jedi language server**](https://github.com/quora/pyanalyze/blob/master/docs/design.md).
- Pyright [**internals**](https://github.com/microsoft/pyright/blob/main/docs/internals.md)

## LSP (Language Server Protocol)

For a comprehensive understanding of language servers, file systems, updates, and testing, check out this [**Explaining Rust AnalyzerYouTube playlist**](https://www.youtube.com/playlist?list=PLhb66M_x9UmrqXhQuIpWC5VgTdrGxMx3y) from [Matkald](https://matklad.github.io/).

[**LSP specifications**](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/) are very easy to read. It's long but you don't need everything in the beginning.
To skip the part of defning every structure yourself you can use [**Tower LSP**](https://github.com/ebkalderon/tower-lsp).

## Linters

Same as with type checking, for linters it's best to look into implementations and learn from them.

The following tools are useful to understand how analysis is done and errors are reported:
- [**oxc**](https://github.com/web-infra-dev/oxc)
- [Ruff](https://github.com/astral-sh/ruff)


## Final Words

Compilers are super fun. If you have more resources please send them to me.
