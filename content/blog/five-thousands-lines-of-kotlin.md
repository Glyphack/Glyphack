---
title: "Five Thousands Lines of Kotlin"
date: 2024-01-21T14:43:03+01:00
draft: false
tags: [programming-language]
---

This post is about my impression of Kotlin as a language after, well you guessed it, writing about five thousand lines of it. I will go through what I don't like about it and whether I would use this language on my own(spoiler: I won't unless I have to.) I started using Kotlin only because of the new job. In my job I worked on server applications only, with the added spice of enterprise software practices.

You've probably heard that Kotlin is much better compared to Java. That is true, it's like a unicorn compared to a horse, but in the end it's just Java with extra features. Kotlin has more features for dealing with nulls, the best feature is the [`.?` operator](https://kotlinlang.org/docs/null-safety.html#safe-calls). This allows you to eliminate the `if (x == null)` from code. I wish they had the same for exceptions.

**Exception Handling**

Continuing with the language features, I think Kotlin lacks tools for [specifying exception types](https://kotlinlang.org/docs/exceptions.html#checked-exceptions) thrown by a function, at least in Java you can annotate what exceptions a function can raise, but Kotlin does not support that.
I think Java is even better in this regard.
This results in ugly try catches on `Exception` everywhere.
I'm not sure why they thought it was a good idea.
Anyone who used a language with support for specifying error types in the function signature knows that it makes it much easier to use the functions and handle exceptions correctly.
In contrast in Kotlin you either have to read through the docs or function code and hope you handled each exception. If you really don't want to fail, you are left with ugly try caches everywhere because you need to catch all exceptions from each statement.

**Editor Support**

Kotlin does not have an official LSP.
LSP stands for Language Server Protocol. Almost all editors work with LSP to provide autocompletion and diagnostics. So the red lines you see in VScode telling what is wrong comes from that.

[The reason](https://discuss.kotlinlang.org/t/any-plan-for-supporting-language-server-protocol/2471) JetBrains does not invest time on LSP is because they want to spend the time on their own editor.
I understand they created really good IDEs and obviously they have a good editor for Kotlin.
But drifting away from open source standards makes it harder for people to use language where they are comfortable.

I used kotlin-language-server while using Kotlin.
One of my problems with it is the slow startup. But this is improved in the recent months. I also [added this feature](https://github.com/neovim/nvim-lspconfig/pull/2930) to Neovim lsp config which helped a lot.
Kotlin is really complex as a language for a couple of people to maintain a language server for it.

**Language Features**

Speaking of how hard it is to maintain a language server for Kotlin we get to the next point.
I think Kotlin has a lot of features, and that is what makes it hard to analyze Kotlin code:

- Class modifiers like `open`
- There are 4 visibility modifiers
- Classes can have 2 constructors
These are not very complex for end user but makes it harder for language tool developers.
I don't think this is needed. This probably satisfies people with boundary fetishes, but you don't need them to get the job done.

But there are also features that makes it harder for end users to reason about the code.

The [extension functions](https://kotlinlang.org/docs/extensions.html) are one, you can mess up the `this` pointer in a class very easily:

```kotlin
class Hello {
    fun sayHi() {
        print("I say ".toHi())
    }
    fun String.toHi(): String {
        return this.uppercase() + "hi"
    }
}
fun main() {
    val h = Hello()
    h.sayHi()
}
```

In this code the `this` in `toHi()` function is not referring to the Hello class anymore.

The next one is the [builder syntax](https://kotlinlang.org/docs/type-safe-builders.html)(it's ironically called type safe builders).
with builders, you can write code like:

```kotlin
class Hello {
    fun sayHi(str: String) {
        buildHello {
         name=str
        }.say()
}
```

This code can create a new class inside the buildHello scope, and then call the say function on it. This looks nice but imagine you want to make the argument name clearer:

```kotlin
fun sayHi(name: String) {
 buildHello {
  name=name
 }.say()
```

Now the point you missed is that name in the buildHello scope is referring to the attribute name of the builder. So that name is not referencing the name in the argument. This is seriously tricky to catch.

You might look and say hey, this makes my code cleaner. Yeah sure, one minute you're writing clean, concise code, and the next you're lost in a sea of extension functions and builders. Good luck debugging.

So my final take on the language features, it's too much!

**Libraries**

Kotlin has access to JVM libraries. Which is a big plus.
The only problem I faced was that the null safety is not fully respected when using Java code with `NotNull` annotation.
@NotNull, indicates that we must never call our method with a null if we want to avoid an exception.
Which is kind of a surprise because being null safe means being null safe everywhere.
But in these functions you can call something that can be null.
IntelliJ and the compiler won't complain about this as well.

But same with Java I don't like that the libraries in the ecosystem rely so much language features as their API. Just give me a goddamn function not an annotation, or a builder, or plugins.

There are some Ktor features that fail during the runtime because it cannot find some plugin that is needed to work properly. Why must this be a runtime problem?

**Why Kotlin Won and Not Scala?**

This question annoys my mind a lot. I also worked with Scala and I think it's certainly a better language. Maybe that's for another post.

But I also stopped doing Scala for one reason, the functional programming community took over the language and every library tried to add functional paradigm and type safety to everything (talking to you, ZIO). Again, just expose a goddamn function.
