---
created: 2025-04-27
category:
  - "[[Books|Books]]"
title: Coders at Work
author: Peter Seibel
isbn13: 978-1430219484
link:
rating: "4"
tags:
layout: book
share: "true"
---
I met many interesting people through this book that I did not know about. People like: 

- Jamie Zawinski (he also appears in this documentary https://www.youtube.com/watch?v=4Q7FTjhvZ7Y)
- Guy Steele
- Peter Norvig

Reading it felt like listening to early Lex Fridman. Back when he was interviewing cool programmers.

The book was very long, and to be honest I almost forgot all the details when I reached the end of the book.
But there were repeating patterns I've read that stuck with me.

---

In debugging, print statements are useful. I used them since I learned programming. But also seeing others say this. Makes me feel better.
I always thought print statements for debugging is my problem. But I think at some point when the code is complex it's easier to use print statements to gather more information about the program than to stop and continue manually.
I use a mix of both print statements and debuggers but seeing many of the interviews mention print statements are the way to debug was something I did not expect.

My personal experience is mostly from working on Ty. Since it's Rust with giant data structures (printing the whole value would be hard to interpret.) it's easier to have if statements to see if my condition is met and then a print statement. Sometimes I place the breakpoint in the if body so I can check some stuff but printing is faster somehow.
Another method is using traces + the printing.
But I rarely use rust debugger and it might be because enums are so hard to view in it.

---

They were all eager to read code. These programmers were working in an older era.
Without the tools we have now to write and execute so much code this fast. It makes sense that they had to give the code more thought before trying it.

I don't read that much code and certainly with the explosion of code that we have now I'm not gonna try to do it on non trusted codes.
I have a network of people I trust with good code that I can learn from(or good products that I can learn form) and I check those.
Reading everything is definitely not a viable strategy now.

---

Not liking the blackbox was also common in the book. The last chapter with Knuth had a lot of good advice on this one.
It's easier to understand what you want and write that part yourself rather than understanding a big system to solve your tiny usecase.
It's also more fun and important for learning.

---

Knuth had a similar idea to patches called change files. Interesting how he didn't pursue that to create a git like system for sending patches to each other.

Some of the chapters sounded less like programming and more about management and how teams should work. I think it was the person from IBM that I didn't really understand what are the talking points. I didn't like these.