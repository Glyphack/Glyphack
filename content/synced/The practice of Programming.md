---
created: 2025-04-27
category:
  - "[[Books|Books]]"
tags:
title: The practice of Programming
author:
  - Brian Kernighan
  - Rob Pike
isbn13: 978-0201615869
link:
rating: "3"
layout: book
share: "true"
---
I started reading the book because of the authors.
Although it's old it has good lessons about programming that are not outdated.
And it's a book from Rob pike so you would hear about simplicity over and over again.

The book takes these general ideas and goes over multiple chapters that explain things like designing, testing, debugging in programming and explains multiple approaches in each scenario.
Along the book you write some programs.
The way these programs are written is a lesson in itself.

Make a simple version.
Think about data structures and interfaces to make a general version.
Iterate and improve into the program after it's used and you have user feedback.

Which is related to the [Gall's law](https://en.wikipedia.org/wiki/John_Gall_(author)#Gall's_law).

Chapter 3 was the start of interesting topics for me.
I like the idea of approaching design with C.
It's about data structures and performance.

But this book approaches the problem simply and from first principles.
What are the important resources we have when programming? How can we design based on the resources?
And doing this in C is good because there's no abstractions that simplifies part of the challenge.

> Less clear, however, is how to assess the loss of control and insight when the pile of system-supplied code gets so big that one no longer knows what's going on under- neath. This is the case with the STL version; its performance is unpredictable and there is no easy way to address that. One immature implementation we used needed to be repaired before it would run our program. Few of us have the resources or the energy to track down such problems and fix them.

Also useful questions to ask in the interfaces chapter:

> Information hiding. The library will impose no limits on input line length or number of fields. To achieve this, either the caller must provide the memory or the callee (the library) must allocate it. The caller of the library function fgets passes in an array and a maximum size. If the line is longer than the buffer, it is broken into pieces. This behavior is unsatisfactory for the CSV interface, so our library will allocate memory as it discovers that more is needed.

 > Resource management. We must decide who is responsible for shared information. Does csvgetline return the original data or make a copy? We decided that the return value of csvgetline is a pointer to the original input, which will be overwritten when the next line is read. Fields will be built in a copy of the input line, and csvfield will return a pointer to the field within the copy. With this arrangement, the user must make another copy if a particular line or field is to be saved or changed, and it is the user's responsibility to release that storage when it is no longer needed.
 
 > Error handling. Because csvgetline returns NULL, there is no good way to distinguish end of file from an error like running out of memory; similarly, access to a non-existent field causes no error. By analogy with ferror, we could add another function csvgeterror to the interface to report the most recent error, but for simplicity we will leave it out of this version.

---

The testing chapters are things that I mostly knew.
I think people started doing more testing since 1998 and what this book is trying to explain are things you probably already do.
The book emphasizes automation a lot. Which people do a lot more now days.
Maybe there are places where automation is not used and should be but I don't see it.

---
The performance chapter is a nice introduction for learning how to optimize performance.
I think I had my first step with a video from [Jon Gjengset](https://thesquareplanet.com/).

---
I skimmed over the portability chapter. I knew already knew part of it.
But I didn't find it useful right now. If I was writing more programs in C it would have been useful.
It was mind blowing that some computers read numbers in little-endian and others in big-endian and this is not something you can assume when developing a protocol.
It's incredible how much abstractions we have on top of things like this that are not trivial.

---

The Notation chapter is full of fun programs to implement.
It's about making small focused syntax for doing stuff in programs.
Techniques like macros, interpreters.
I wish these were things I made when I was in university.
