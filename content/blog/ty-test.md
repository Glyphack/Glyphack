---
title: "Ty Test Suite"
date: 2025-12-10T16:12:40+01:00
draft: false
tags: [] 
---

[Ty](https://github.com/astral-sh/ty) tests use markdown.
It looked strange, but I'm sold to the idea now.
When I started programming all I found online on testing was about unit tests, end-to-end, black-box, white-box.
So why don’t more tests look like this?

## Unit Tests Are Verbose

Say you’re writing a parser and want to add a unit test. It usually ends up looking like this example from [Writing An Interpreter In Go](https://glyphack.com/s/write-an-interpreter-in-go/):

```go
// parser/parser_test.go
func TestFunctionLiteralParsing(t *testing.T) {
 input := `fn(x, y) { x + y; }`
 l := lexer.New(input)
 p := New(l)
 program := p.ParseProgram()
 checkParserErrors(t, p)

 if len(program.Statements) != 1 {
  t.Fatalf("program.Body does not contain %d statements. got=%d\n",
   1, len(program.Statements))
 }

 stmt, ok := program.Statements[0].(*ast.ExpressionStatement)
 if !ok {
  t.Fatalf("program.Statements[0] is not ast.ExpressionStatement. got=%T",
   program.Statements[0])
 }

 function, ok := stmt.Expression.(*ast.FunctionLiteral)
 if !ok {
  t.Fatalf("stmt.Expression is not ast.FunctionLiteral. got=%T",
   stmt.Expression)
 }

 if len(function.Parameters) != 2 {
  t.Fatalf("function literal parameters wrong. want 2, got=%d\n",
   len(function.Parameters))
 }

 testLiteralExpression(t, function.Parameters[0], "x")
 testLiteralExpression(t, function.Parameters[1], "y")

 if len(function.Body.Statements) != 1 {
  t.Fatalf("function.Body.Statements has not 1 statements. got=%d\n",
   len(function.Body.Statements))
 }

 bodyStmt, ok := function.Body.Statements[0].(*ast.ExpressionStatement)
 if !ok {
  t.Fatalf("function body stmt is not ast.ExpressionStatement. got=%T",
   function.Body.Statements[0])
 }

 testInfixExpression(t, bodyStmt.Expression, "x", "+", "y")
}
```

This test case is a beast[^1].
All this code just to check a one-line function parses correctly.
If we decide to update this test to check, say a function with 3 parameters we need to modify multiple places in this test.
What you can do in this case is to define a function for it:

```go
fn checkParameters(params *function.Parameters, expected []string) {
 // Check expected parametes are in params in order
}
```

So then you can test different combinations of parameters with less lines of code.
Also if you change how parameters are stored in `function.Parameters` you don't need to update individual tests.
We need lots of tiny helpers just to keep tests readable.

## Snapshot the Output

Complex output makes assertions messy and huge.

I learned this technique of storing output of tests from [vim9jit](https://github.com/tjdevries/vim9jit).

For example, [this test](https://github.com/tjdevries/vim9jit/blob/master/crates/vim9-parser/testdata/snapshots/assign.vim) is just the program input.
The test runner feeds it to the parser and stores the output in a snapshot file next to it.
On the next run, it compares the parser’s output to the stored snapshot instead of checking dozens of individual assertions.

For example,  is just the input of the program.
It feeds the input to the parser and stores the [output](https://github.com/tjdevries/vim9jit/blob/master/crates/vim9-parser/testdata/output/vim9_parser__test__assign.snap) next to the test.
Next time the tests run it compares the output of the parser to the previous stored snapshot.
In this method instead of individual asserts we check the output of the parser.

This works especially well for programs that transform data, like parsers and compilers, but you can use it anywhere.
All you need is a method to print state of the program as text.
And you most likely already need to [reveal the internals](https://bernsteinbear.com/blog/walking-around/) of the program for debugging.
Which makes it even more appealing the code is not just for tests.

I used snapshot testing on my project for a while, but hit another problem: snapshots can get [huge](https://github.com/Glyphack/enderpy/blob/dc53f04f8223653b272bc8e806a1d59d33667b4e/typechecker/test_data/output/enderpy_python_type_checker__checker__tests__specialtypes_none.snap#L98).
Checking large snapshots requires having input and output open side by side to compare.
I found myself not reviewing the output carefully because the output was massive.
So snapshots cut boilerplate, but they also make it easy to hide bugs inside massive dumps of text.

## Literate Testing

Ty’s tests live in markdown files.
It's very close to the idea of [literate programming](https://en.wikipedia.org/wiki/Literate_programming#Workflow).
>Implementing literate programming consists of two steps:
>
>1. Weaving: Generating a comprehensive document about the program and its maintenance.
>2. Tangling: Generating machine executable code

You write examples and documentation, and they are the [tests](https://github.com/astral-sh/ruff/blob/main/crates/ty_python_semantic/resources/mdtest/assignment/annotations.md):

![Ty Test Example](/ty-test-example.png)

```python
def f() -> int:
    return 1
 
reveal_type(f())  # revealed: int
```

This test checks how function return types are type-checked.
Adding another test case is easy. You just paste the Python code.
If you get a bug report, you can paste the failing code straight into the tests and reproduce it without extra boilerplate.

1. You write the Python code you want to test.
2. You call `reveal_type` on an expression and write the expected type in a comment.
3. Test runner passes this code to Ty type checker.
4. The test runner feeds this file to Ty, which evaluates each `reveal_type` call and compares the displayed type to the comment.

`reveal_type` is not the only way to assert.
There are more functions like `generic_context` to [check](https://github.com/Glyphack/ruff/blob/bcddab6680f5026718094a630e2891f79488a55a/crates/ty_python_semantic/resources/mdtest/generics/specialize_constrained.md#L150) the generic type information.

Python also uses [this style](https://github.com/python/typing/blob/main/conformance/tests/annotations_methods.py) of testing for type checker conformance tests.
You want to test different type checkers.
They all take Python programs as input.
So let's write test cases as Python programs.

## Other Programs

If a program you're working on is not transforming text then applying this idea directly is not possible.
But so do API servers (JSON responses), database systems (query results), even UI frameworks (rendered HTML).
So by writing the code that reveals the internals as text it is possible to test using the above techniques.

[^1]: In case you're wondering how does a simpler version of this look like. This is example of the [input](https://github.com/Glyphack/enderpy/blob/dc53f04f8223653b272bc8e806a1d59d33667b4e/parser/test_data/inputs/function_def.py#L1) and [output](https://github.com/Glyphack/enderpy/blob/dc53f04f8223653b272bc8e806a1d59d33667b4e/parser/test_data/output/enderpy_python_parser__parser__parser__tests__function_def.snap#L11-L46). The output file is long. But if you have a [good tool](https://insta.rs/) for snapshot tests it's easy to review changes. Otherwise you can split the big input file to smaller ones and have smaller output.
