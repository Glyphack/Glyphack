---
title: "Devlog 5: Simu, Ty, Book Reader"
date: 2025-09-28T10:52:46+02:00
draft: false
tags: [log] 
---

## Chat with New People

Met [Amir](https://amirhn.com/). Turns out it was a good decision to live stream writing Redis in C from scratch. You find new friends by doing it.
Met Matt from [Blinkinlabs](https://blinkinlabs.com/about).

## Simu

About a month ago I started building a logic gate simulator software. My goal is to run it in web browser and have enough features to make a CPU with it.
I think this will be useful for teaching people about CPUs.

Worked on:

- Polishing the UI, You can click drag a pin to connect it to another pin.
- Various dragging actions for dragging and keeping the connection, drag both ends of the wire and drag only one end of the wire.
- Draft for connecting a wire to middle of another wire, live coding [here](https://youtu.be/ROll1Qz64OQ)(Alert: it's in persian.)

You can watch me [here](https://youtu.be/ROll1Qz64OQ?t=295) using it to build a multiplexer. The UI is finally easy and fast to use.

## Ty

Ty worked on the [self feature]({{< relref "blog/ty-self.md" >}}) a bit and then I'm taking a break. I'll get back this week.
Most of the blocking issues are resolved by others. They did the super hard part.
We are close to have Self type in Ty!

## Book Reader

I had this project from a long time ago and I stopped using it. It's a book reader with builtin translation.
I made it when I was reading a [Max Havelaar](https://nl.wikipedia.org/wiki/Max_Havelaar_(boek)) But I lost my interest.
Now my girlfriend is using it so I spend more time working on it. The good part is that it still compiles after few months of not touching it. I will write more about it.

## Books

I started reading [Data Oriented Design]({{< relref "synced/Data Oriented Design.md" >}}) when I worked on Simu.
It's a good book, I never had correct training on data normalization and this book had new stuff for me right away.

As I read more of the book it got more abstract and it was talking about topics that are hard to apply. For example "Avoid enums" But the author does not talk about the huge amount of code you need to write when you avoid enums. I think overall there are useful ideas in the book but on the other hand it's not as practical as I expected it to be.

While reading it my friend Kevin sent me [this blog post](https://kyju.org/blog/rustconf-2018-keynote/) which had more examples of writing code in DoD way.

[Creativity, Inc.]({{< relref "synced/Creativity, Inc..md" >}}) was in my reading list for a long time.
I heard good things about it from a lot of blogs and people.

First chapters are cool. It talks about the history of Pixar, how Ed got interested in making animations with computers and how long it took for him to get funded and pursue this dream.

Everything else is generic management advice. Things like people should review each others work and be able to give honest opinion, you can't control everything so leave room for randomness in your calculations.

So not so exciting of non-fiction choices.

## Various Links

- <https://geohot.github.io//blog/jekyll/update/2025/09/12/ai-coding.html>
- <https://borretti.me/article/lessons-writing-compiler>
- <https://en.wikipedia.org/wiki/Chris_McCandless>
- <https://www.recurse.com/self-directives>
- <https://bernsteinbear.com/blog/walking-around>
- <https://commandcenter.blogspot.com/2023/12/simplicity.html>
- <https://www.youtube.com/watch?v=JRTLSxGf_6w>
