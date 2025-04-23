---
title: "Devlog 3: Coding a redis clone in C and things I learned"
date: 2025-02-15T18:02:46+01:00
draft: false
tags: [coding, devlog]
---

About two months ago I started the build your own Redis challenge from [https://codecrafters.io](codecrafters.io).
I decided to do this in C. Initially I was just curious to do it in C. Doing it in C thought me a lot of stuff that otherwise I would have not learned. Another bonus point was that I could tweak the performance to be on par with Redis server.

C always seemed like an impossible language to me. Working so much in garbage collected languages with rich standard libraries made me think C is hard.
Now I think C is not hard. Whatever you write gets executed the way you wrote it. Little abstractions make it a great language to implement what you want and have control over your program.
Topics like Async programming, managing memory are broad topics. I agree that it's hard to achieve the same level of concurrency that you have in Python in C. But writing a small version that works for a specific use case is not impossible.
It's possible to implement hash map, Async, memory arena(for easier memory management), and your own string type with a few lines of C code, thanks to blogs like [null program](https://nullprogram.com)

I think I'll use the below techniques I learned for any C program I create. I wish it was easier to package them so I can reuse it in different projects.

The source code is at [glyphack/redis-clone](https://github.com/Glyphack/redis-clone).

The below are things I learned about C programming.

## Awesome Compiler Flags

I don't know why nobody told me this. C can have stacktraces. It can detect race conditions. It can detect use after free. It can do a lot of stuff by just adding more compiler flags.

You can compile your program with flags:

- `-fsanitize=undefined` to crash on undefined behavior scenarios
- `-fsanitize=thread` to crash when threads have race condition(this is actually what powers Golang race detector)

And if there is a race condition in your program you will see something like:

```
==================
WARNING: ThreadSanitizer: data race (pid=12345)
  Read of size 4 at 0x000000601040 by thread T2:
    #0 thread_func (source.c:7) in main
    #1 start_thread (pthread_create.c:XXX)

  Previous write of size 4 at 0x000000601040 by thread T1:
    #0 thread_func (source.c:7) in main
    #1 start_thread (pthread_create.c:XXX)

  Location is global 'shared_var' defined in source.c:5
==================
```

I built my program in debug mode with these flags and ran a tester that would insert and get values from the server. It detected a lot of bugs for me while pointing out the exact line the problem happened.

## Memory Arena

I used a [memory arena](https://nullprogram.com/blog/2023/09/27/) to minimize the number of `malloc` and `free` calls in the code.
It makes code faster but in the end I realized how much simplified the code gets.
It's basically like having a garbage collector and you know when it happens.

## Custom String Type

One of the problems I faced soon after working with C was that, sometimes I wanted to keep a reference to middle of a giant string. Imagine you get a request and extract a field name from it. Now you have two options, either `memcpy` that substring into a new string and add a `\0` or make a pointer to the starting offset of the substring.
When you keep the offset you cannot use it in most of other places because you don't know the end of this string, and C strings end with `\0`.
I followed the advice in [this post](https://nullprogram.com/blog/2023/10/08/) and it made code a lot smaller(no extra string creation and `malloc` calls) and simpler because working with a string when you know the length is just easier. Plus if you are worried you would lose the benefits of C string functions don't worry there is not much functionality there. You can implement it yourself.

## Hash Map

I followed [this post](https://nullprogram.com/blog/2023/09/30/) to implement a hash map. Initially my program was using a thread per connection so I tried to extend the lock free version to work with my program.
In the end I implemented Asynchronous code to handle multiple connections, removed the threads, and just used the hash map that is explain in the post.

## Redis Replication

The Redis replication is initially simple to implement I did not implement the full protocol.
The basic functionality is to handshake with the master node and master node has to keep a list of replicas to forward write messages to.
The way multiple nodes stay in sync is by using replication offset that master checks for periodically. I did not implement any recovery case for when a replica is out of sync.

## Asynchronous Programming

This is my favorite topic. I finally got a clue what actually happens in higher level languages. Before actually doing this I read and heard some words but it all felt like buzzwords to me.
What does it mean each coroutine has a stack? Why can't you run a blocking task inside an asynchronous function? I learned all after I implemented this.

The interesting part is, implementing basic asynchronous I/O is not hard, making it general and cross platform is. This is what other programming languages did.

To serve multiple clients concurrently we need a way to read from all of them without ever waiting for one client and **blocking** others.
So what we really need is, a way to tell which clients are ready to read, which are ready to write and instead of waiting for the ones that are not ready just skip and serve other clients.
I recommend following [this guide](https://build-your-own.org/redis/05_event_loop_intro). I ended up switching to `kqueue` from `poll` to achieve better performance on MacOS.

---

I think this database can be a good base program to expand to any kind of future databases I want to write.
I can reuse the existing protocol to exchange messages and add my custom logic or [implement Raft](https://eli.thegreenplace.net/2020/implementing-raft-part-0-introduction/).
