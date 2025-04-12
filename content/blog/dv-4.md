---
title: "Devlog 4: I made a chrome extension"
date: 2025-04-12T11:49:07+02:00
draft: false
tags: [devlog] 
---

I'm not sure if some time comes that I finally can say I know vim. But I don't think that would happen before I [read the whole manual](https://www.youtube.com/watch?v=rT-fbLFOCy0).

This week I learned these new commands:

I've always used `ctrl-o` to move to last place I was editing in vim. Turns out there's a keybinding to move to the previous file that was open it's  **`Ctrl-^` (or `Ctrl-6`)**.
This command switches to the last visited file.
It provides quick toggling between two files if you do it repeatedly.

[`:g`](https://vim.fandom.com/wiki/Power_of_g) is powerful. To move/delete things that have a pattern.
You are probably familiar with `gj` and `gk` but there's also `gq` (or `gw` if the other did not work.) `gw` helps to split a long line into smaller lines.

Other things:

- I made a chrome extension, [Readwise Reader Importer](https://chromewebstore.google.com/detail/readwise-reader-importer/biaidjfcmkeeiidenndhkdaldkljaipi?authuser=1&hl=en) to import links into Readwise. I wanted this tool myself for importing youtube playlists to Readwise. This time I decided to build it as an extension so I can share with others. It got 10 users! I did most of the work using Claude code. It costed around 10 euros, but I'm happy with the resulting look.
- I moved [my reading list](https://glyphack.com/reading-list/) off Notion and to my blog. I was tired of me entering books I read and notes about them in Obsidian and the Notion was rarely updated. So I found a [solution](https://glyphack.com/blog/ob/) to update my blog with Obsidian, and then show the book notes just as any other page on my blog. The bonus is that I can make it more beautiful in the future.
- I've heard about this language called ungrammar that is used in Rust to generate CSTs. I did not know anything about it. Thanks to this [issue in Ruff](https://github.com/astral-sh/ruff/issues/15655) , I did some work related to generating AST. There's [this nice](https://www.youtube.com/watch?v=EIXb9mX_o9s) video that explains how it's used in the Rust Analyzer code.
- I implemented [Redis streams](https://redis.io/docs/latest/develop/data-types/streams/) in toy [clone of Redis](https://github.com/Glyphack/redis-clone). I took some time doing this, I wanted to use an array instead of a linked list. This would make a good candidate for a blog post so I won't go into details. Redis uses [radix tree](https://en.wikipedia.org/wiki/Radix_tree#:~:text=In%20computer%20science%2C%20a%20radix,is%20merged%20with%20its%20parent.) to implement streams(according to AI)
- I read <https://sive.rs/su> and decided to keep my own URLs shorter too.

That's it for this week.
