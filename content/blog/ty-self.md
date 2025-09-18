---
title: "Adding Support for Self to Ty"
date: 2025-09-18T19:20:37+02:00
draft: false
tags: [] 
---

I am reading [No Ordinary Genius](https://glyphack.com/s/no-ordinary-genius/) and the book is saying how nice it is when some technical writing includes everything you need to understand a subject. In its own words:
> I find it very discomforting now that there are many books that claim to explain a subject, in which there's some concept or other which is very poorly explained, and therefore it's not there—no matter how hard you study that book, you'll never come out the other end.
> You'd have to know the concept wasn't there, and that's hard to do when you're first learning a subject. The problem is not that you are foolish or incapable, but that the writing isn't there. I was lucky in that the sources I had always had everything in them; even if it was in very condensed form, it was all explained very carefully.

Also, reading through the implementation of [PEP 695](https://jellezijlstra.github.io/pep695.html), it's a great example of the case above, where it explains the subject perfectly.

I didn't write this way before, but I'm trying my best this time.

After my last attempt at writing a [Python type checker](https://glyphack.com/dv-2/), and failing, I started looking into [Ty](https://github.com/astral-sh/ty/) to learn how Python typing works and how to implement this in Rust without blood and sweat.
So I've been casually contributing to Ty in my free time.
About 5 months ago, when I was browsing Ty issues I found that it [does not support the `Self` type yet](https://github.com/astral-sh/ty/issues/159).
It looked like a fun thing, so I started working on it.

In this post, I explain how this was implemented, the areas of code it touched, and the challenges along the way.

## Self type

`self` is a type in Python that refers to the class itself.

```python
class Person:
  def name(self): ... # self is referring to Person
```

This part of the [typing spec](https://typing.python.org/en/latest/spec/generics.html#self) explains a strategy to determine a type for the `self` argument in the above code.

How does this `self` type work under the hood? It's all [syntactic sugar](https://en.wikipedia.org/wiki/Syntactic_sugar):

```python
from typing import TypeVar

Self = TypeVar("Self", bound="Person")

class Person:
  def name(self: Self): ... # self is referring to Person
```

And if you are not familiar with `TypeVar`, it simply means:

1. Any type that can be used in place of `Person` can be used in place of the `Self` type.
2. Any type that is a subclass of `Person` can also be used in place of the `Self` variable.

How do you annotate `self` arguments in methods?
Writing a type variable just for every class would be tedious.
We can leave that to typeshed.

The `typing` module provides `Self` as a symbol that any Python code can use to refer to the class. So we can replace the handmade `Self` in the code above with `from typing import Self`.

```python
from typing import Self

class Person:
  def name(self: Self): ... # same as the previous code
```

## What Is the Type of `Self`

Now, for a type checker, the question would be what the type of a variable should be when it's annotated with `Self`. Normally, you would check the definition for the symbol to see what it defines.

If we look at the actual [definition](https://github.com/python/typeshed/blob/cb0fbd891336df9410d297de863fb3dd9731067c/stdlib/typing.pyi#L255) of `Self` in typeshed, we find:

```py
Self: _SpecialForm
```

What is a `_SpecialForm`?

Special forms in typeshed are types that do not have a complete definition in the code; instead, the behavior of that type is defined by the typing spec. There are many types in Python like this: `Optional`, `Literal`, etc.

So, based on the spec, the suggested strategy for implementing `Self` in a type checker would be:

1. When you encounter `Self`, add a synthetic `TypeVar` above the usage.
2. Replace `Self` with the new type the type checker just added.
3. Use the new type for the rest of type checking.

Also, there are [invalid](https://typing.python.org/en/latest/spec/generics.html#valid-locations-for-self) uses of `Self`. They don't change how type checking happens, but they help with eliminating some edge cases.

One question could be, why wouldn't we have a type in our type system called `Self` that contains what class it was used on so you can know what this type means during type checking?
I guess this can be done, but one nice feature of changing `Self` into a `TypeVar` is that you don't need to touch the rest of the type checker. It will be handled by the same code that handles a `TypeVar` so there will be less code (and fewer bugs, because the logic would otherwise be duplicated).

But implementing this in a type checker would be a few more steps than just this explanation.
That's why I love learning by making instead of just reading about it.

## Support for `typing.Self` Annotation

This step is the easiest one: if the user annotates anything with `Self`, then perform the above replacement and return the correct type for `Self`.
I did this in [this PR](https://github.com/astral-sh/ruff/pull/17689).

### Binding Self

This looked simple to me at the time, but now after a few months of tinkering with the `Self` type support I know more edge cases.
One decision here is where we should bind `Self`.

Binding a type variable means which class or function (or module) should contain the definition for the type variable. Maybe this is clearer with the new type parameter syntax defined in [PEP 695](https://peps.python.org/pep-0695/):

```python
# Option 1 bind to class

class Person[Self: "Person"]:
  def name(self: Self): ...

# Option 2 bind to method

class Person:
  def name[Self: "Person"](self: Self): ...
```

In the code above, first, the type variable is bound to the `Person` class, and the second example binds it to the method.

The difference between these approaches is in situations where the user creates a subclass of the class. From [this discussion](https://discuss.python.org/t/unsoundness-of-contravariant-self-type/86338):

```python
from typing import Self
class Base:
    def foo(self, x: Self) -> None:
         pass

class Derived(Base):
    def foo(self, x: Self) -> None:
        x.bar()

    def bar(self) -> None:
        pass

def test(a: Base, b: Base) -> None:
    a.foo(b)
test(Derived(), Base())
```

In this example, the method `foo` that redefines the `foo` method in `Base` does so in an incompatible manner. `Base.foo` considers `x` to be `Base`-like, but `Derived.foo` considers `x` to be `Derived`-like.

If the `Self` type variable is bound to the method, it's more natural for the type checker to reject this override.
Because when checking the signatures we don't need extra information and it's clear that overriding something that accepted the base class with the child class violates the [Liskov Substitution Principle](https://en.wikipedia.org/wiki/Liskov_substitution_principle).

```python
class Base:
    def foo[Self: "Base"](self, x: Self) -> None: ...

class Derived(Base):
    def foo[Self: "Derived"](self, x: Self) -> None: ...
```

It's not impossible to achieve the same behavior by binding `Self` to the class but this now makes it more trivial to detect problems like this. A type checker is full of exceptions and special cases already and being able to remove problems like this is a good thing.

So that's how [Ty binds the `Self` argument](https://github.com/astral-sh/ruff/pull/20366).

## Implicit `self` type

The next part of this change is unannotated `self` usage.
Most Python code in the wild does not annotate the `self` argument with `typing.Self` so the `self` argument is considered to have this type annotation implicitly.

For a type checker we need to assume that the following:

```python
class A:
  def foo(self): ...
```

is equivalent to:

```python
class A:
  def foo(self: Self): ...
```

So next I worked on adding this implicit annotation to the `self` argument.

This implementation would touch two main areas of code:

- Uses of `self`: when you type `self` in method bodies
- Method calls: when you call a method on a class like `Foo().bar()`

## `self` in method bodies

Imagine the type checker wants to know what is the return type of `A.foo` in this code:

```python
class A:
  def foo(self):
    return self
```

Ty looks up `self` in the function scope, finds that it refers to the first argument.
After performing a couple of checks (are we in a class? Is it a `classmethod` or `staticmethod`?)
it can identify that we are pointing to the first argument of a normal method, which has `self`, so it considers the type annotation to be `typing.Self`.

And that's the whole logic I implement in [this PR](https://github.com/astral-sh/ruff/pull/18473).

But if you look at the scrollbar you see we are not finished yet and there is something awaiting us.
That's true.

After adding this implicit annotation, Ty has to do a lot more work than in previous versions.
Because the type of `self` was previously unknown, it bypassed a lot of type-checking rules.

After I made and sent the PR the CI identified a crash in the new code.
Ty has a nice CI.
In each PR it runs the new version of the type checker on a bunch of Python codebases using [mypy_primer](https://github.com/hauntsaninja/mypy_primer) and compares the new Ty and old Ty diagnostics.
The idea is very similar to [fuzzing](https://en.wikipedia.org/wiki/Fuzzing).
By running the type checker on numerous codebases some bugs are surfaced that are hard to think of.

This CI is also nice for checking impact of a new change across the Python ecosystem.
You can implement a new rule and see how many new diagnostics are we going to emit and are they correct.

This stage of testing uncovered a couple of panics in my code.

### Salsa

To get to what caused the panic we need to take a step back and look at Ty data structures for representing types.

Ty uses a library called [salsa-rs](https://github.com/salsa-rs/salsa), which is an incremental recompilation tool.
In case of a type checker, it helps when you are checking multiple Python files and one of the files changes; you only need to check the changed file without recomputing types for the whole project.

This is an example defined type using Salsa interned structs:

```rust
#[salsa::interned(debug, heap_size=ruff_memory_usage::heap_size)]
#[derive(PartialOrd, Ord)]
pub struct ClassLiteral<'db> {
    /// Name of the class at definition
    #[returns(ref)]
    pub(crate) name: ast::name::Name,

    pub(crate) body_scope: ScopeId<'db>,

    pub(crate) known: Option<KnownClass>,

    /// If this class is deprecated, this holds the deprecation message.
    pub(crate) deprecated: Option<DeprecatedInstance<'db>>,

    pub(crate) dataclass_params: Option<DataclassParams>,
    pub(crate) dataclass_transformer_params: Option<DataclassTransformerParams>,
}
```

[source](https://github.com/astral-sh/ruff/blob/59c8fda3f8f3bf2cc5c1ae34e7ca9dbea4d0278f/crates/ty_python_semantic/src/types/class.rs#L1331)

Notice the `salsa::interned` usage and `db` lifetime.

Interning a struct means when creating an instance of this struct Salsa will store the value and give you an ID; you can later use this ID and query the Salsa DB to get back the object.
Similar to how pointers work, but in this case this is an ID, and I think it helps with making the type serializable so you can do incremental computation nicely.

Also, having IDs is nicer to work with because you can pass values by copying and have fewer issues with the borrow checker.

Other than incremental recompilation, Salsa provides another awesome feature for type checkers, [cycle handling](https://salsa-rs.github.io/salsa/cycles.html).

Let's start with a simple example where this would be useful.
This was the first infinite recursion bug I faced while type checking the Python standard library:

```python
class str(Sequence[str]):
  ...
```

[source](https://github.com/python/typeshed/blob/cb0fbd891336df9410d297de863fb3dd9731067c/stdlib/builtins.pyi#L476)

Let's see this code through the lens of a type checker.
There is a function like this:

```rust
fn infer_class_type(class_def: ClassDefinition) -> ClassType:
  // We definitely need to check the base classes of this class to find what its type is
  for base in class_def.bases:
    let base_type = infer_class_type(base);
  // rest of the code
```

This is how the above code will have infinite recursion:

1. Try to infer type of `Str`
2. Infer type of `Sequence[Str]` base to know what things `Str` inherits from the base
3. `Sequence` has a generic parameter and here we are using `Str` to figure out what the type of `Sequence[Str]` is we need to infer `Str`
4. We are back to step 1

This is called a cycle, and we need a mechanism to stop it. The good news is that Salsa has a cycle resolution algorithm. It works based on fixed-point iteration.

What happens in this case is that at step 3, when we are going back to step 1, Salsa can detect this (because it tracks the function calls) and Ty in this case can provide a cycle fallback value.
This will tell salsa to consider `Str` as `Any` and finish the recursive calls.
This way we end up with some type for `Str`. Is this enough? No.
Next is that we repeat this process now with the type we have for `Str` and at some point this should converge.
Meaning that determining the type again with the value we got from the previous process should give the same type.
This way you can be sure the outcome type is final.

### Cycle Panic: Accumulating Literals

So now we can go back to the implicit self annotation and explore the panic that happened.
The code that caused a panic could be reduced to:

```python
class A:
  def __init__(self):
    self.n = 1
    
  def incr(self):
    self.n = self.n + 1
```

This example is a bit more complicated to understand why there is infinite recursion.

First Ty tries to be very precise in the returned type.
While you can say that type of `n` is an integer.
Ty considers that `n` could be `Literal[1 | 2 | ...]` It knows that the `Literal` type can be expanded many times because it does not precisely know how many times `incr` might be called.
Ty tries to infer `self.n` and it sees that it requires to know about `self.n`.
`self.n` is initially 1 so then `self.n` will be 2. Now with the value of 2 we infer `self.n` again (because of the fixed-point iteration algorithm from previous section.)
This process happens for 200 times and Salsa panics because the cycle did not converge.

The fix for this would be easy, we just need an upper bound on how long we want to consider `self.n` a literal value before it becomes an integer.
If we set this upper limit to anything lower than 200 then in one of the iterations Salsa will see that `self.n` had type `int` and the result is also `int` so the cycle stops.

### Cycle Panic: Divergent Value

After fixing this I found [another panic](https://github.com/astral-sh/ty/issues/692) happening. This panic has a different nature.
This is a reduced version of the original code that reproduces the issue:

```python
from typing import Literal

class Toggle:
    def __init__(self: "Toggle"):
        if not self.x:
            self.x: Literal[True] = True
```

In this strange-looking code the definition of `self.x` is under an if statement that checks for `self.x` so this is an access before defining the value.
For the type checker it does not matter if the code is invalid or not. It will type-check it to provide feedback for the user.

Now let's see through the lens of the type checker what happens when inferring the type of `self.x`:

1. This attribute is guarded by an if statement, we first need to check if the condition is met then the value is True
2. Condition is `self.x` so we need to infer type of `self.x`
3. Salsa cycle recovery assumes the type of `self.x` is unknown and the if would be false
4. Type of `self.x` is `Literal[True]` now.
5. To complete the fixed point iteration now infer type of `self.x` again with the determined type
6. Type of `self.x` is unknown because `not self.x` is false and the if does not execute so `self.x` would not be defined
7. The cycle recovery goes back to step 5 now with the type unknown and it repeats
In the end, the type of `self.x` will alternate between unknown and `Literal[True]`.
But it will never be one type.

This example is also nice because it highlights why convergence for the cycles is important.
If we simply substitute a value for `self.x` when there is a cycle and conclude we are not seeing all the possible cases.
We either see `Literal[True]` type or unbound value and a runtime error case.
And in this case seeing the `Literal[True]` sounds like a better idea because the `self.x` might be set by the user, outside of the function.
It's hard to decide these.
Because the Python code could run without a runtime error but type-checking would be more complex.

[David](https://github.com/sharkdp) suggested [a solution](https://github.com/astral-sh/ruff/pull/19579) that fixed this issue.

The solution here is to disable the reachability analysis when an attribute is not defined.
This means that when Ty is checking the code above instead of trying to see if the `not self.x` is true or not it considers that it is either true or false.
Then based on if we consider this ambiguous value true or false to run the if or not.

The solution involves keeping track of all the names and attribute accesses that happen when type checking an expression and returning a boolean to indicate if all subexpressions are definitely defined.
Definitely defined means it won't cause a runtime error when you use that expression.
In the case above if we don't assign `x` to the instance before calling the method it results in a runtime error.

```rust
    let inference = infer_expression_types(db, expression);

    if !inference.all_places_definitely_bound() {
        return Truthiness::Ambiguous;
    }
  // if it is bound then check the truthiness of the inferred type
```

### Performance Regression 1

<https://github.com/astral-sh/ty/issues/758>

The next problem that I found using `mypy_primer` was that the code was running slow.
The result was scary:

```
/tmp/mypy_primer/ty_old/target/debug/ty on mongo-python-driver took 1.96s
/tmp/mypy_primer/ty_new/target/debug/ty on mongo-python-driver took 98.62s
```

The new version of the code is almost 50 times slower.

Since this was not the only one, I used [this Python script](https://gist.github.com/Glyphack/6f430f90c3c28954f89216c7b87b61d4) to list projects that ran slow in type checking or never finished.

This case was slow was because of attribute assignments guarded by themselves.

The guard means more than only if statements, for example in this code:

```python
class A:
  def a(self):
    self.foo = False
    self.bar = False
    
  def f(self):
    if self.foo:
      return
    if self.bar:
      raise Exception()
    
    self.baz = 1
```

For the type checker the `self.baz` is defined if `self.bar` and `self.foo` are false. So its definition is guarded by those checks.
This is what reachability analyzer does in the type checker to find what is reachable and thus defined and what is not.

Also note that `self.baz` is an implicit attribute. Ty does not know if `A.a` is always called before `A.f`. So it needs to consider both it might or might not be defined. Usually type checkers don't emit diagnostic for accessing these attributes. A lot of Python code is written like this.

Now getting back to the problem. If `baz` is guarded by `bar` and `foo` if we add another line to make `foo` and `bar` dependant on `baz` then we have a cycle and we get closer to the [problem](https://github.com/astral-sh/ty/issues/758) I faced.

It's not hard to identify there's a long cycle happening. Salsa has traces so by running Ty with `-vvv` we can get the traces and it looks something like this:

```
TRACE ty_project::db: Salsa event: Event { thread_id: ThreadId(2), kind: WillIterateCycle { database_key: member_lookup_with_policy_(Id(f4e2)), iteration_count: IterationCount(1), fell_back: false } }
```

To decode what the Id `f4e2` is referring to we just need to check rest of the traces. Find somewhere the Id is mentioned and try to map it to source code.

I wrote so many `eprintln!`s in the code to figure out what is going wrong.

And when implementing the fix in the previous topic, I was benchmarking this as well and the cycle count was reducing with the fix here too, but it was not enough to make it fast.

To improve the performance here, David found [a solution](https://github.com/astral-sh/ruff/pull/20128) to disable checking if an implicit instance attribute is bound or not.

Here we don't want to give an error if user tries to access `A.foo` because the method `A.a` might be called before and the attribute actually exists.
These are called implicit attributes that are not defined in the `__init__` method and instead are implicitly added to the instance in other ways.

### Performance Regression 2

The [next problem](https://github.com/astral-sh/ty/issues/1111) was found when type checking the SymPy codebase. The problem is not specific to SymPy though. It also happened on other repositories.

The problem happens when there are attributes which all depend on each other for values.
The reason is unknown to me. I think it's a little bit related to the previous performance regression.
Somehow when these attributes depend on each other when A needs to be inferred we need B and for B we need C and for C we need A and B so cycle counts start increasing.
This means Ty spends a lot of time iterating to find a value for A, B, and C but it needs *a lot* of iterations to converge.

This was a big problem, it meant that type checking on some packages took a long time.
And I could not fix this issue.
Even with the previous one I spent too many days adding prints to the code to understand what is happening and understand flow of the code.
But this one was harder than that.
I had to leave it to Astral team to figure this part out.

The fix isn't there yet.
We'll get there eventually and the fix for this one might be in the [Salsa library](https://github.com/salsa-rs/salsa/issues/841).
It would have been fun if I had the time to investigate this myself and learn more about Salsa.

## `self` in method calls

Why does inferring `self` in method calls require a different solution than the one above?

Consider the following examples:

```python
class A:
  def foo(self):
    print(self) # the type checker sees self and tries to find it in the scope.

a = A()
a.foo() # Here Python implicitly passes `a` as the first argument of `foo`. So that's what the type checker does as well.
```

In the first part of the code when we refer to `self` in the method body the type checker finds that variable and sees that it's a method argument. Then the code that we talked in previous section takes care of assigning its type implicitly.

In the second part of the code when we call any method on a class we are passing the instance as the value for the `self` argument, even though it's not passed in the parentheses.
You can check this by doing `A.foo(A())` and see that it's just syntactic sugar for it.

In the second example Ty checks whether you are passing valid arguments to the method, i.e., whether `a` is assignable to `self`.

This requires two different codes to handle the type checking.
I think the real reason is because of generics.
When we are inferring types in a method body the function or class is not specialized yet.
Meaning that we don't know what type parameters are referring to (`typing.Self` or others.)
But when a call is happening the value is specialized, so it makes sense that we need some separate code to handle these.

When functions are called Ty [makes a signature](https://github.com/astral-sh/ruff/blob/59c8fda3f8f3bf2cc5c1ae34e7ca9dbea4d0278f/crates/ty_python_semantic/src/types/signatures.rs#L1156) for the function and tries to match the passed arguments with defined ones.

And here I needed to add the extra code that [would add the synthetic type annotation](https://github.com/astral-sh/ruff/pull/18007) to `self`.

With these kinds of changes you expect some performance regressions.
Because previously a type was unknown and a lot of type checking rules did not apply but now they are.
But along the way we found one speed improvement that could also simplify the type inference.
The trick was to annotate the `self` with the class name if the function is not already generic:

```python
class A:
  def foo(self: "A"): ...
```

Here annotating `self` with `"A"` or the type variable version would not make any difference.
And since the method is not generic we don't make it generic only because it has `self`.
Remember, we bind the `Self` type variable to the method, so the method that contains `self` has a type variable, and is therefore generic.
When a method is generic on every use we need to solve the generic parameters.
Meaning to check how the method is used and replace an example `T` generic parameter with what it should be at the use.
And this is redundant here, so I tried to apply this, and the result was a couple hundred milliseconds faster when type checking the pandas package. It had the biggest difference around 500 milliseconds.

The credit for this goes to [Carl](https://github.com/carljm).

As you can see in the PR above this change surfaced some issues around handling generics.
Since previously the `self` type was unknown a lot of assignability issues were not reported.

But there was one way to make progress on this PR easier. Since these issues could be reproduced on main.
I could file issues for them (here is [an example](https://github.com/astral-sh/ty/issues/1131)) to fix them in a separate PR.
David helped me a lot with resolving these issues. So sadly I don't have more information to share about the issues.

## Future Work

As of now, the support for implicit `self` type is not in Ty yet.
There are some improvements to add to have a correct implementation that works on different Python codebases.
Probably in a couple of weeks, it's going to land in Ty.
I spent time on this feature and the challenge made me happy.
I'm glad to see it's getting close.

## Acknowledgments

What I implemented here was mostly guided by the Astral team. If you count overall their contribution was far more than me on this topic.

David helped implement fixes for false-positives and panics related to implicit `self` to help me make progress.

Carl provided a lot of guidance for the implementation.

Douglas helped me a lot with generics and. He [solved](https://github.com/astral-sh/ruff/pull/19604) the first blocker for supporting `self` in method calls.
