---
title: "Simple Expertise"
date: 2025-10-25T11:09:19+02:00
draft: false
tags: [] 
---


If you think about how we judge skills you'd see we do it by questioning the advanced stuff.

Some think this is right. If a person has experience in something they must know the advanced topics that beginners haven’t heard of.
This is what schools do: after every level, the questions get harder.
I’ve sat through more physics than Galileo and Newton combined.
Am I a good physicist?

That's how my mindset changed.

I was sitting at a talk by [Kelsey Hightower](https://github.com/kelseyhightower)[^1].
He said in every interview he wants to learn something new about the person.
And he asks the candidate to write a simple program and watches everything he does.
So he did this live in the talk.

He opened the terminal, then Vim, and wrote a Go hello world.

```go
package main

import "fmt"

func main() {
 fmt.Println("hello world")
}
```

He Compiled it and asked how big is the binary? No one knew.
He ran `ls -lh` and it was 2Mb.

He asked was what is making this file 2 megabytes?
People suggested complex reasons: debug symbols, Go runtime, system libraries.

He asked How can we apply these suggestions to make the binary smaller?
Again silence in the room.
Ideas were easy to remember and say, but no one thought about applying them.

He proceeded to change it to:

```go
package main

func main() {
 println("hello world")
}
```

These questions can continue,
how many instructions do you think the two programs have?

Expertise shows up in simple problems, because simple problems expose fundamentals.
In programming we are working on top of [layers of abstraction](https://iuliangulea.com/pyramid-of-mastery).
Abstractions can be good when you know how they work and you use them but otherwise they are some artificial limit.
An abstraction is designed for a use case in mind.
When it does not work the truth is not that it cannot be done, but it's to break through the layer.
Discover how to achieve the goal from basic principles.
It's like saying a program cannot be smaller because of the compiler.
The compiler is just a word. The truth is what did the compiler put into the program.

This happens in other topics.
If someone asks why leaves are green and I say it's because they contain chlorophyll do I really know what I'm talking about?
That's the answer everyone gets in school.

How does it pay off to see what's under the hood?

Kelsey told a story that his colleague found a bug in go compiler because he looked at the instructions when noticed the program is not fast.
It's easier to shrug it off and say the compiler did some magic work and this is the result.
That never leads to interesting findings.

This was also my own experience.
I thought contributing to [Python](https://glyphack.com/contributing-to-python-docs/) required some magical preparation.
The reality is, just read what's in the manual then check what's going on.
If they don't match you are onto something.

If you want to feel confident about your knowledge, start with the simplest task and keep asking fundamental questions.
Don't take magical words as answers. The answers are simple.

[^1]: He didn't prepare any slides. It was more a discussion. Presentation was three slides with one big word "AI" and it got bigger in each slide. He asked everyone to invest in themselves. Our work is the AI training data so there's still value in thinking. Don't delegate your thinking to AI.
![Kelsey](/Kelsey.jpeg)
