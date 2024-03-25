---
title: "Devlog 0002 Enderpy Generics Type Inference"
date: 2024-03-25T16:46:15+01:00
draft: false
tags: []
---

I implemented Generic classes and functions this week in Enderpy. I'm happy that now my code can now read and infer types of [this conformance test](https://github.com/python/typing/blob/main/conformance/tests/generics_basic.py#L114).

I chose to skip implementing generics with syntax `def f[T](): T` because of the [scoping behavior](https://peps.python.org/pep-0695/#scoping-behavior).
They are also tested extensively in this [test case](https://github.com/python/typing/blob/main/conformance/tests/generics_syntax_scoping.py).

Another strange thing I found in the `typeshed` repo is that in the `sys/__init__.py` file there is a `import sys` in the beginning.
Making this a cyclic import. I think the reason is to use the `sys.version` and `sys.platform` in the type definitions.
But in the type checker I manually skip resolving this import because it resolves to itself.

The current implementation I came up with for the generic does not infer the actual type of generic in the type evaluation phase. So if the type checker asks the type of parameter that is generic type it gets back a generic parameter node in the returned type.
I'm planning to add the functionality to infer the type of the generic parameter based on the types passed as the generic type to type checker.

This is how the code works right now:

1. The type parameters are inserted in the symbol table like other variables.
2. When the type evaluator resolves a type annotation that is referring to typing. TypeVar it considers that a type parameter type.
3. When the classes have a base class of `typing.Generic[T]` the type evaluator tries to find the type parameter, and adds the type parameter to the inferred class type.

The next step is to continue the generics test cases and implement the type inference for the generic types.
