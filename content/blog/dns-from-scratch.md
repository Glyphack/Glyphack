---
title: "Writing a DNS server From Scratch"
date: 2024-10-12T13:09:53+02:00
draft: false
tags: [programming]
---

I decided to build another system from scratch just to explore a new topic and learn things.
This time I chose the [Code Crafters's DNS challenge](https://app.codecrafters.io/courses/DNS-server)

This is not a tutorial on how to do it but some notes to motivate you to do it.
There's already [excellent material](https://app.codecrafters.io/courses/DNS-server) on how to do it with code examples here.
If you are already curious, then start building your own.

I really enjoyed the way challenge is organized.
It's very small steps in which you implement something from the spec.
You don't build fake things that later become real at a certain stage.
It's all working software from the beginning.
For example, in the DNS challenge you can use what you build with the `dig` command from the first step.
It does not actually work, but it's the first thing you need when building a DNS server.
Something that just spits out correct bytes.

This encourages you to not plan for what components your app should have or how to represent the request and response.
You build the thing that shows you a result as soon as possible.
I was writing my code in the main function with no structs or anything. Because you really don't need it.

This helps a lot to make progress and stay motivated.
A lot of the time when you are learning something new you try to see what is the whole subject and how much you have to learn and what are the topics.
But this also slows you down and makes it uninteresting.
Primarily, because the joy of learning is destroyed.
Also, because any complex topic is big enough to show you how much time you need to spend to become good that can push you away from learning it.
This helps you to just focus on the given problem at the time.
You can apply this in your own projects as well.
Instead of listing every single thing you need to do to succeed focus on the next result you can see and learn to get there.

**Things I learned**

This was my first time working with the bits and bytes in golang.
I had only done it in assembly before and almost forgot how it's done.
And golang has a useful set of packages to do help with this.

Also, the [compression method](https://datatracker.ietf.org/doc/html/rfc1035#autoid-44) is interesting, you don't need a general algorithm that compresses the data when you know patterns in your data.
The compression does not work like normal compressions, and instead it relies on the fact that the DNS query has a lot of domain names with similar labels (each word between the `.` in domain is a label) so it says a label once and refer to it later.

Start with the smallest thing that gives result.

**Improvements**

In the last stage of the challenge you implement a DNS server that takes in the requests and resolves them using another DNS resolver. The other resolver is provided by codecrafters.
I tried to use my resolver with `8.8.8.8:53` and it was not working.
I found the reason is that my DNS parser does not still support all the information that `dig` command sends by default. And also I haven't implemented compression for encoding DNS request to bytes.
I haven't checked how the codecrafters software works but maybe I would try to contribute this later.
