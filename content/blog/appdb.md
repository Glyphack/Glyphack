---
title: "Application as a Database"
date: 2026-04-02T08:53:48+02:00
draft: false
tags: [] 
---


When I started programming professionally, I got recommended some programming books that teach you how to write good code and use well known patterns.
Years after that I feel it was just preference of the author for how to write code.
There's only one important note about coding style and that's [consistency](https://glyphack.com/s/the-practice-of-programming/).

So after a while of programming I have formed my preference: Make data available throughout the whole program, and to not duplicate any data.
I'm going to explain this style in this post.

## Make Data Accessible

Every part of your program should be able to lookup whatever is needed from the context.
Similar to how a web server has a database and every endpoint handler has access to the database.

This is against the idea of isolating pieces of code behind interfaces.
Every layer you add to your program means duplicating data structures.
Each layer loses some information when you copy the data to next layer.

If your program has a user object and you also have a layer for interacting with database then you also have a user object in database.
Your code needs to copy bytes around for transforming application user to database user.
This means a lot of useless code for copying and hurting performance of your application.

How many layers can we remove? PostgreSQL can [return a complete HTTP response](https://github.com/sivers/sivers#html-in-postgresql) if it fits the needs of your application why not?

I like information hiding. It's good to hide complexity of something behind an interface.
But hiding the data makes changing program harder since you don't have access to the data to perform something.
This means constantly passing more arguments and values to each function to perform tasks.

**How do you allow access to data everywhere?** 

One way to do this is to have a database class that contains all of your application information and pass that through classes.
This means passing something throughout the program.
This is a trade off, it changes all of your program. But as a result you have access to everything.
Then in every part of the program you can access other data structures using the database.

Another way of doing this is to just include all the information available when passing values back from functions.
Whenever in a program I call an external endpoint I pass the full response object back.
The function that calls external service only knows how to handle HTTP errors in general way.
But other parts of the program can do what is more appropriate in that context.
So instead of taking a response and transforming it into some internal representation I have create an object that wraps the response with additional information.
The downside is obviously more memory usage.
But this is something you can get rid of later once you are sure the data is not needed.

I've seen this idea to have a database like object being used in other projects like:
- Atom in Clojure
- ty and Rust analyzer

A simple compiler architecture performs these passes on the code:

```
Parser -> Semantic Analyzer -> Type Checker -> Code Generator
```

While it can be seen as something that you can just perform each pass and just pass the output to next step. This solution is not optimal.
For the type checker to provide good error messages it needs the source code, or to suggest a fix.
Which means not only you need output of the parser but you also need the input.
You don't take something transform it into another object that loses information.
Instead, you add more information to what you already have.

To solve this problem you can create a data structure containing all the information produced by your program.
In every stage you have access to this data structure.

Without this structure you would have something like:

```python
def parse(source: str) -> dict: ...

# Now in type check you don't have the source anymore.
# you can pass the source as well
# This means a group of related values that have to be passed everywhere.
def type_check(ast: dict) -> dict: ...
```

Example of this structure:

```python
class CompilerDB:
    def __init__(self, source: str):
        self.source = source
        self.ast = {}      
        self.symbols = {}  
        self.diagnostics = []

def parse(db: CompilerDB): ...
def type_check(db: CompilerDB): ...
```

[This is a good introduction for full implementation](https://petevilter.me/post/datalog-typechecking).

You can either have an object that contains AST from parser, symbol table from semantic analyzer.

Or you can store the data in [normalized](https://www.dataorienteddesign.com/dodbook/node3.html#SECTION00340000000000000000) way and keep references to it. A function in symbol table can have a node ID to reference its source code from AST.
Think about what's the relation between these objects. Since they need to reference each using IDs.
Going with latter and having IDs also helps with easier caching and incremental computation in your program.

## Data Deduplication

After every part of the program is able to access any information you can easily avoid duplicating logic and data.
The reason is now you can avoid all the intermediate objects that only transferred one value from a layer to another.
Which means now for every concept you have one class for it in your program.
Once you have the data structures, think about ownership of the values.
Each value would have one owner and others would store a pointer to that data.
This is the source of truth for that concept.

Without the data access you need the copy of values from class to class so you have access to that value in places where it's needed.
Without that limitation, you don't need to copy anything.

But there's another gotcha here. You might end up duplicating values from objects in different places.
In the example:
```
players: Dict[str, Player]
```
Where key of this hashmap is player username.
This data modeling is duplicating the player username.
This means whenever you need to update a player, you also need to update this hashmap as well.
But it's not gonna stop at the hashmap since you start referring to the player using username throughout the code.

Instead, using a stable ID (like [generational indexes](https://verdagon.dev/blog/generational-references)) would be a good choice.


Also you need to create structs that can hold all the information related to the same concept in one class or struct.
This helps with having a struct holding all information about something and just having an ID to access that struct means you have all the information.

Once you have that a function like `get_player(db, id)` can return you the player and you can access username from the player object.

There's one place where I like to have methods to access or set a field on an object. It's for easier code navigation.
LSPs don't have a way to only show usages of an attribute where it was assigned. In that case having a method that assigns the attribute can help with finding them more easily.
Similarly constructor methods can help with finding all places where something is created.

---

The push in software architecture to isolate pieces of code and data is popular in gigantic codebases.
In that environment, guiding programmers with the isolation works better.

But in most cases, you can free yourself from the arbitrary constraints and write code with less indirection.

And ask yourself [have you tried rubbing a database on it?](https://www.hytradboi.com/)
