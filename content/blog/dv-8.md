---
title: "Devlog 8"
date: 2026-06-02T00:05:46+02:00
draft: false
tags: [log] 
---

It's been a while since I wrote a dev log.
I was working on some networking project and I didn't really think about other stuff for a few weeks.
Now I'm slowly getting back to writing more blogs.

My plan is to share more notes on my blog like my current [bookshelf](/reading-list).
I'll probably start with sharing my travels.

## Fuzzing Ty

Fuzzing is a cool technique. With fuzzing you can discover crashes in a codebase that you haven't worked in before.
You might not find the most interesting crashes.
But you find crashes.

So what's fuzzing?
You have a huge set of input data for your program.
This is called a corpus.
A fuzzer program can feed input to your program and detect if it crashes.
It can also modify the input to generate new input.
The loop is to generate input data, feed it into the program, check for a crash, mutate again.

The mutation can be based on code coverage.
The fuzzer can explore random changes to input and try to hit new paths in the program.

It all started after seeing [This PR](https://github.com/astral-sh/ruff/pull/23146).
I wondered if I could find a couple of these panics by fuzzing ty.
So I spent a day writing a fuzzer to see how it turns out.
I didn't have prior experience with fuzzing.

The most famous fuzzing tool is probably [AFL++](https://aflplus.plus/). But for ty there was already a fuzzer setup with Rust Fuzz so I used it.
I read through [Rust Fuzz Book](https://rust-fuzz.github.io/book/cargo-fuzz/tutorial.html) and wrote a fuzzer for autocompletion in ty, and I found three crashes!

- [Debug version panics on autocompletion when cursor is between two brackets](https://github.com/astral-sh/ty/issues/3087)
- [Excessive runtime for nested `OrderedDict` instances](https://github.com/astral-sh/ty/issues/3123)
- [Calling Enum with a single argument panics](https://github.com/astral-sh/ty/issues/3272)

I suspect ty's fuzzer has not been used for a long time. 
Following the [instructions](https://github.com/astral-sh/ruff/blob/61d78a19ece136d300290249beb2fac2cea5a266/fuzz/README.md#L32), I ran `cargo +nightly fuzz run` and I immediately got an error.

This build command was for M1 Macs. I'm on Apple silicon but I'm not on M1.
Anyway, I then tried the other command that was for non-M1 Macs.
Another error.

At this point I started reading the error message to figure out the problem:

```
  = note: Undefined symbols for architecture arm64:
            "___sanitizer_cov_8bit_counters_init", referenced from:
                _sancov.module_ctor_8bit_counters in pep440_rs-bed188ac979b131c.pep440_rs.4bdb810c36179955-cgu.0.rcgu.o
                _sancov.module_ctor_8bit_counters in libunicode_width-eea06fe4ff42950d.rlib[3](unicode_width-eea06fe4ff42950d.unicode_width.1584ecc128ad03be-cgu.0.rcgu.o)
...
ld: symbol(s) not found for architecture arm64
clang: error: linker command failed with exit code 1 (use -v to see invocation)
```

I was already running with `-s none`, which should disable all sanitizers.
If a codebase has a lot of `unsafe` code, sanitizers help to uncover more memory issues.
In the case of ty, I knew there could be crashes in non-unsafe code because of assertions.

So I searched around and another solution was to provide a stub for [Sanitizer Coverage](https://clang.llvm.org/docs/SanitizerCoverage.html).
In the error above the `___sanitizer_cov_8bit_counters_init` definition is missing.
I can define this symbol and provide it to the compiler.
Each definition has `__attribute__((weak))`. 
This would allow these definitions to be overridden.

```cpp
#include <stdint.h>

__attribute__((weak)) void __sanitizer_cov_8bit_counters_init(uint8_t *start,
                                                              uint8_t *stop) {}
__attribute__((weak)) void __sanitizer_cov_pcs_init(const uintptr_t *pcs_beg,
                                                    const uintptr_t *pcs_end) {}
__attribute__((weak)) void __sanitizer_cov_trace_const_cmp1(uint8_t a,
                                                            uint8_t b) {}
__attribute__((weak)) void __sanitizer_cov_trace_const_cmp2(uint16_t a,
                                                            uint16_t b) {}
__attribute__((weak)) void __sanitizer_cov_trace_const_cmp4(uint32_t a,
                                                            uint32_t b) {}
__attribute__((weak)) void __sanitizer_cov_trace_cmp1(uint8_t a, uint8_t b) {}
__attribute__((weak)) void __sanitizer_cov_trace_cmp2(uint16_t a, uint16_t b) {}
__attribute__((weak)) void __sanitizer_cov_trace_cmp4(uint32_t a, uint32_t b) {}
__attribute__((weak)) void __sanitizer_cov_trace_cmp8(uint64_t a, uint64_t b) {}
__attribute__((weak)) void __sanitizer_cov_trace_switch(uint64_t val,
                                                        uint64_t *cases) {}
__attribute__((weak)) void __sanitizer_cov_trace_div4(uint32_t val) {}
__attribute__((weak)) void __sanitizer_cov_trace_pc_indir(uintptr_t callee) {}
```

Finally compiled!
I'm not an expert in this topic and don't know what the correct solution is.
The reason I'm fine with this is that I have disabled sanitizers with `-s none`.
I assume this means sanitizers will not be used during fuzzing.
So an empty stub should be fine.

Now what are we testing in ty?

The fuzzer randomly generates Python code.
It then inserts the cursor at every line/column combination possible and calls the `completion` function.
This function will return autocomplete suggestions for that line and column.
If there's a crash, the fuzzer will report it.

```rust
fn do_fuzz(source: &[u8]) -> Corpus {
    let code = match std::str::from_utf8(source) {
        Ok(s) if !s.is_empty() => s,
        _ => return Corpus::Reject,
    };

    let parsed = parse_unchecked(code, ParseOptions::from(Mode::Module));
    if parsed.has_invalid_syntax() {
        return Corpus::Reject;
    }

    let (mut db, python_file) = setup_db();
    let settings = CompletionSettings { auto_import: false };
    db.write_file(PYTHON_PATH, code).unwrap();

    for offset in (0..=code.len()).filter(|&i| code.is_char_boundary(i)) {
        let text_offset = TextSize::from(offset as u32);
        let _ = completion(&db, &settings, python_file, text_offset);
    }

    Corpus::Keep
}

fuzz_target!(|data: &[u8]| {
    let _ = do_fuzz(data);
});
```

In fuzzing you usually leave the full argument generation to the fuzzer.
The code above doesn't do that.
I let the fuzzer generate the source.
I try all the positions in a file and there's a higher chance of finding a crash.

Out of curiosity, I also tried another approach called [Structure-Aware Fuzzing](https://rust-fuzz.github.io/book/cargo-fuzz/structure-aware-fuzzing.html).
The idea is that you define your input and the fuzzer generates it instead of a byte array.

```rust
#[derive(Debug)]
struct CompletionInput {
    source: String,
    cursor_offset: usize,
}

impl<'a> Arbitrary<'a> for CompletionInput {
    fn arbitrary(u: &mut Unstructured<'a>) -> arbitrary::Result<Self> {
        let source = String::arbitrary(u)?;
        if source.is_empty() {
            return Err(arbitrary::Error::IncorrectFormat);
        }
        let boundaries: Vec<usize> = (0..=source.len())
            .filter(|&i| source.is_char_boundary(i))
            .collect();
        let &offset = u.choose(&boundaries)?;
        Ok(Self {
            source,
            cursor_offset: offset,
        })
    }
}
```

And the logic for the fuzzer is to just find valid inputs and run the `completion` function.

```rust
fn do_fuzz(input: CompletionInput) -> Corpus {
    let code = &input.source;
    let offset = input.cursor_offset;

    let parsed = parse_unchecked(code, ParseOptions::from(Mode::Module));
    if parsed.has_invalid_syntax() {
        return Corpus::Reject;
    }

    let (mut db, python_file) = setup_db();

    let settings = CompletionSettings { auto_import: false };
    db.write_file(PYTHON_PATH, code).unwrap();

    let text_offset = TextSize::from(offset as u32);
    let _ = completion(&db, &settings, python_file, text_offset);

    Corpus::Keep
}
```

I found two crashes with the first approach and one with the second one.
I don't think there's a winner here.
Both methods can be useful.
Trying all positions is slower.
Also you lose the benefit of the fuzzer saving the exact input that causes the crash.

Found crashes, what now?

Leaving a fuzzer on a project that is not stable yet, like ty, is expected to generate lots of crashes.
It's good to report them.
But it's important to not flood the issues by copying and pasting what the fuzzer is giving us. (Sounds familiar, doesn't it?)

Make sure to not report one problem multiple times.
Multiple crashes might share the same root cause.
Reporting that once with all the examples is enough.

Use `creduce` to [minimize the input](https://bernsteinbear.com/blog/creduce/).
Usually fuzzer inputs are large, and the culprit is just in one or two lines.
Minimizing is taking a large input and reducing it to the absolute minimum that still causes the crash.
Debugging with a single line of Python code is a lot easier than debugging with a large program.

And finally, send patches too.
Charlie fixed [this](https://github.com/astral-sh/ty/issues/3272) 20 minutes after I opened it and didn't give me a chance.

This was a fun journey!
It took me two days and I learned a lot.

I liked cargo fuzz. Next time I'll try the [LibAFL](https://aflplus.plus/libafl-book/introduction.html) library to make a custom fuzzer.

## `,g` Command

I am a fan of customizing git configuration.
I started customizing my [`.gitconfig`](https://github.com/glyphack/dotfiles/blob/0bcb61f1e2812acf9807ecff527060817f8306c7/gitconf/.gitconfig#L1) a few years ago.

But I barely used git CLI wrappers, or GUI apps that aim to replace git.
The operations I do with git are simple and similar.
After you've undone a commit a few times you memorize it and don't need a GUI for it.
Another advantage of using the git CLI is that it works everywhere.
I do most of my git operations in fugitive in Vim with the same git commands.

But I finally made a git CLI wrapper!
It all started with a command I made some years ago. The command `myprs` used `gh` to list my pull requests using [gum](https://github.com/charmbracelet/gum) for selecting the branch to check out to.
My programming is mostly oriented around pull requests. 
Having something that lists all the stuff I have open was a huge win for me.
Or if you work in a large repo with lots of contributors it's easier to switch between your branches because you don't see others' branches.
Later I learned there are [ways](https://www.youtube.com/watch?v=GKBq5Xo_B6I) to do this with git itself too.

But there are other things that I do repetitively.

- Find name of the base branch (main/master)
- Deleting branches that are already merged
- Keeping the worktrees in a specific place so I can keep track of them.

The result is the `,g` command.
It uses [gum](https://github.com/charmbracelet/gum) to make it easy to list and choose stuff.

`,g new branch-name` makes a new branch.
With the `-w` flag it makes it a worktree. Worktrees are stored in `{worktree-path}/{project}-{branch}`. This makes it easier to search and manage.
New branches are created from the upstream base branch.
The main/master is resolved by the command.

`,g co` lets me switch between my branches or pull requests.
Before switching, anything in the current branch is stashed.
When I come back to it, saved changes are unstashed.
I used to do this with a subcommand `git wip` but I ditched that for an automated one.
Maybe I lose a change one day and go back to manual.

The command `,g done` checks out to base and deletes the branch and its worktree.
I also migrated my pull request scripts over so with `,g pr create` I can create them quickly.
`,g pr review` copies a message with pull request link to share with others for review.
I use `,g coauthored glyphack` to generate a co-authored-by message.
There are more commands I added based on the things I do frequently and need multiple command invocations.
You can check it out in my [dotfiles](https://github.com/Glyphack/dotfiles/blob/9f39ecf04c60900a94c8d1632a20b6432efe4b14/fish/functions/%2Cg.fish#L1).

It's written in fish. I ported it to fish with an LLM from bash scripts that I had over the years.
I'm comfortable with Python for these kinds of things but I don't know if it's important enough for me to rewrite it.

## vm2 command for running containers

It is scary to install anything on your computer these days.
Each app has [a shit ton of dependencies](https://pointersgonewild.com/2026-05-11-dependencies-are-a-liability).
Nearly every week a dependency is compromised.

But I like to install coding agents and try them.
At the same time I'm not confident in installing and running them on my system.

I used to use [vibe](https://github.com/lynaghk/vibe) for running agents.
I love how it's implemented and how customizable it is.
But two things made me reconsider:
- I know nothing about containers. Discovering networking [problems](https://github.com/lynaghk/vibe/issues/27) is not for me.
- Some features like `exec` are already provided in containers. But another tool means implementing them again.

So I tried a different approach with [Apple Container](https://github.com/apple/container).
I need a container with the tools I want to use.
Then run the container with directories mounted.
To simplify the workflow, I built a small CLI for it.
I can also customize the volumes and environment variables that are passed to the container.

Check it out [here](https://github.com/Glyphack/dotfiles/tree/be7d14e92480294cd59a83903dfaa7bb7be8f0f2/scripts/vm2).

Here's how it works:

Run `vm2 build` to build the image.
Running `vm2` in any directory creates a container and mounts:
- current working directory
- configurations like `.claude`
- the `.git` folder is included in the container. If it's a worktree, the `.git` is resolved and mounted.

Git provides useful tools like `git bisect` for the agent when debugging.
But git push is disabled by default with a `pre-push` git hook.
So the agent cannot accidentally push garbage.

This is partially extensible. You can write a Python script that runs and prints what customization to apply.
It can be setting environment variables, mounting a directory, or running a shell command after starting the container.

The format of output is:

```
VOLUME src:dest
SETUP command1;command2
ENV VAR1=VAL1
```

I use it mostly for running agents.
Sometimes I use it when I need to run a project and I don't trust the dependencies.

## Links

[Noise Protocol Framework](http://www.noiseprotocol.org)

I love the idea. Noise provides building blocks for creating secure communication channels.
This is useful for sending information back and forth over a public network.
Since it provides the tools, you can build the security protocol in your app.
You manage it however you like.
For someone like me without a background in cryptography and security, this is the closest I can get to doing my own security.

It's based on Diffie-Hellman.
You choose the algorithms to use and then use APIs to read and write messages.
[snow](https://docs.rs/snow/) crate implements the framework in Rust.
I used it and it was great.

The scenarios it protects against are:
1. Encrypt messages: An attacker who sees the messages cannot read the data.
2. Replay protection: An attacker cannot send the same bytes on behalf of the sender.
3. Man in the middle: An attacker cannot impersonate the receiver and fool the client to exchange keys.

If you like to learn more watch this [talk](https://www.youtube.com/watch?v=3gipxdJ22iM) from Trevor Perrin (author) and build something with it!

[Borrow-checking surprises](https://www.scattered-thoughts.net/writing/borrow-checking-surprises/)

It's like JavaScript puzzles of what will be printed, but for Rust borrow checker. I only hit 1 case of this.

[DigiNotar](https://en.wikipedia.org/wiki/DigiNotar)

I found this when I was learning more about security with the Noise framework.
Internet certificates that guarantee that the website you are seeing is the actual website are just an agreement.
The authorities can simply lie to you.
> The company was hacked in June 2011 and it issued hundreds of fraudulent certificates, some of which were used for man-in-the-middle attacks on Iranian Gmail users.

[Learning Software Architecture](https://matklad.github.io/2026/05/12/software-architecture)

Matklad was the one who saved me from the system design hell.
Things that I heard from people about software design when I started programming were garbage.
If of Kafka vs another queue means software architecture to you, read this.
It helps you to get out of the boxes and arrow mentality of software design.

[The illusion of moral decline](https://www.experimental-history.com/p/the-illusion-of-moral-decline)

This writing argues that morality is not declining.
The survey data from different countries, ages, etc. all agree that morality is declining.
Especially since the time they were born. Which if true is contradictory.
So something must make people feel that during their time something bad is happening.

In the end it argues that it's a bias that we think this is happening.
I am not convinced by the answer.
But I'm happy to know that having nostalgia is not just for me and everyone has it.
Now I can notice when it's affecting me.

[Richard Feynman on Hardware, Software, and Heuristics](https://youtube.com/watch?v=EKWGGDXe5MA)

Feynman explains to students how a computer works. How and where to use it.
I'm amazed by the level of detail he goes into in this introductory lecture.
This is the most accessible explanation of computer organization I've seen.

In the end he discusses the topic of "Can machines think?".
I was reading about the same topic in The Art of Doing Science and Engineering.
Both answers are very similar. This subject in the book has more depth. Read it if you liked the discussion in the lecture.

[The Lottery of Fascinations](https://slatestarcodex.com/2013/06/30/the-lottery-of-fascinations)

This helps you to not feel guilty next time when you feel you should like some subject.

[Every productivity thought I've ever had](https://guzey.com/productivity/)

I haven't read a piece on productivity for a while.
I liked it because it started out with a great tip and said that no productivity system works.
Which means this system probably won't work, so it's honest. Great!
