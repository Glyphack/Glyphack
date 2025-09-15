---
created: 2025-09-07
category:
  - "[[Books|Books]]"
title: Data Oriented Design
author: Richard Fabian
isbn13: 978-1916478701
link: https://www.dataorienteddesign.com/dodbook/
rating:
tags:
layout: book
share: "true"
---
I found this book in [Andrew Kelly's talk on data oriented design](https://www.youtube.com/watch?v=IroPQ150F6c).

I picked up this book when I started building a [logic gate simulator](https://github.com/Glyphack/simu) in Rust.
In the simulator there are objects like gates and wires and information about how they are positioned, connected and power status.
This makes it a good candidate for data oriented design mostly because I can avoid putting too much information in one single object.
Why is having too much information in one object a bad thing? Mostly because mutating the object is harder.
If I keep a list of pointers in one object if it's connected or not then updating that object would be hard because the pointer might get invalidated and borrowing rules will note allow it.
One solution to this is using smart pointers because `Rc<RefCell>` will allow cloning the pointer and to mutate it.

Another solution is giving objects IDs and having a database like functionality in the project to allow accessing the object with an ID.
This is basically turning off the safety features from Rust borrow checker. 
I enjoy this style right now because it allows saving the state in load it easily.

The book explains a lot and it also trying very hard to convince this is a better style of programming. The same vibe you get listening to a functional programming talk.
I didn't enjoy that but reading through the normalization chapter explains how the different features of the game can be implemented independently.
One example is that you can separate the power on/off state of objects by not storing that information on the object but in a separate `Vec<bool>` and lookup the status from this table.

I enjoyed some sections and some sections were hard to understand and apply for me.
There are nice tricks like removing booleans and using seeds to generate objects consistently [just in time](https://www.dataorienteddesign.com/dodbook/node6.html#SECTION00630000000000000000).

What I missed from the book was a chapter helping to implement a small game in data oriented design using vectors and maps.
A [friend](https://kevinlynagh.com/) of mine sent me this [blog post](https://kyju.org/blog/rustconf-2018-keynote/) which is a perfect source for implementing data oriented design in Rust.
So I highly recommend reading that before the book. It gives you applicable knowledge and I enjoy practicing more than reading so it's perfect.