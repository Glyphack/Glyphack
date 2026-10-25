---
date: 2026-10-25
category:
  - "Blog"
tags:
  - devlog
title: "Log 9: LLM thoughts, readings, and trips"
---
I stay away from the people who are shouting stuff like "YOU'RE GONNA LEFT BEHIND JUST BUILD THINGS".
While I like to use AI to do get more things done these claims don't provide anything of value.
I need concrete examples and things to show for something. I like people who build something and show it's possible and you can try. Or people who write about their experience with LLMs.

So here's an example problem I have when coding with an LLM.

1. I ask it to do something that I'm familiar with. I even write the plan of I want this new data structure and here's how I want the full code to work out.
2. It generates some code and I am good with the code mostly I might tweak it, and continue
3. I realize I lost the mental model of what the hell is going on I go back to prompts like "This does not work fix".

At this point I have two options:

1. Stop and read the code figure out what's going on then continue again.
2. Ask the LLM for more information on what's going on then I know what to prompt next.

I tried first option when working on [Clay](https://github.com/Glyphack/clay) I asked for a CLI tool with the stuff I want it to do then I took the control of the code and mostly did edits.
This is a very small project but I know everything that happens during the installation and it actually worked when my friends tested it.
The importance of things being correct here was that I wanted to share this with few friends and wanted to make sure it does what's needed and works.
Getting to something that works with an LLM requires a lot of testing and most of the time I make something vibe coded it just works on that specific case that it's prompted and something small can make it fail.

The only part that I outsourced to LLM for implementation was the UI.
My idea was that I use [charm](https://github.com/charmbracelet) tools and the LLM would just put different components near each other so the actual logic is done by someone else who is an expert in this topic.
This is basically like don't vibe code your game engine when you want to make a game. Just use an engine and vibe code the game.

This was good but I don't think it can be done on bigger projects. I want to get back to working on [Simu](https://glyphack.github.io/simu/) and that code is bigger so I cannot read everything from the main again at some point.
It will take couple of hours.
So I feel this is a good approach for small projects maybe less than few thousand lines of code.

I tried the second approach in [Running Python tests in Ty](/blog/ty-pytest/) I did write the first draft of the code myself. In some edge cases I didn't know what's the best solution is so I asked the LLM to implement it and after it passes the tests I take a look at it.
Then after checking the code it changed it took me a longer time to understand the change.
Primarily because the LLM reused some code that I didn't know about.
The code change was small (~200 lines) but then it imported and use X where I have no idea about it.
Then I ask about why X is used here and I have to investigate where are other uses of X and if this is the right code to reuse.

It could be that a person who incrementally learned all the codebase is more comfortable in this situation because they remember when X was introduced but for me it's more work to figure out.

What I tried was:

- Ask LLM for more explanation of why something is imported and used and if it follows the other patterns of using that in the code.
- Ask the LLM to revert its changes and then I go ahead and implement myself and when I'm stuck I ask for help and since it did research it suggests solutions. So I first ask it to try something and make sure it works, so it's not giving me bullshit solutions. Then I try to do it myself and use it as a guide. My hope is that when I do this myself I give it a better prompt when asking a question.

The first approach works. It's nicer to just do this in the chat and ask the LLM for excerpts of the code along with explanation.
Unfortunately I have to be careful and spam questions like "Does this need to be this complicated?" or "Is this the correct solution or just a hack". So I have to go back and forth.
Sometimes I don't like the UI for this kind of review. Because the text I have to read is scattered in the chat.
I like to try at some point to make it a prompt that fills in some UI with the code to review along with annotations for me. Some idea I took from [here](https://www.geoffreylitt.com/2026/07/02/understanding-is-the-new-bottleneck).

The second approach is slower especially if I'm a noob in the domain.
It's more work but I have a guide at points where I'm stuck.
This is similar to how I studied. Get some problems and work on them and then check the solution when I'm stuck.

***

I'm searching for advice in this regard but most of the things I see on the internet is like astrology.
"Oh you're a Gemini? You're a better match with Codex than Opus. Don't forget to talk to it condescendingly. Trust me, it's a kinky model."

Seriously, are you a witch doctor turned into a programmer?

Mostly the useful stuff seem to be about software itself that I can use for prompting and reviewing.
If you have some posts please send it over to me.

***

I'm not looking for The Way to use LLMs for programming.
Some people complain about the code but quality of the code is subjective.
The way of solving each problem is different.
Sometimes you know the problem is really simple you know the way to do it and can verify the code so you take a different approach.
Or maybe you don't have time for something, it's nice if LLM can do it. It does not matter that in general the code is not correct but if it solves that specific case it saves you time.

(I'm still suspicious when someone says a model made this thing completely and they tried it for few minutes and it works.
My own experience is that I created some utility scripts this way that occasionally break, and vibe coded stuff I receive from others has bugs.
I'm not saying this leads to good stuff, sometimes you don't have enough time to care about something.)

There are other cases.
I program because it's fun then the whole fun would be gone if I have no idea what's going on.
There are some stuff I wrote about this in [Persian](/persian/) mostly because I saw suggestions about what's the correct way to program now.

***

I've been writing more on this blog after I started [sharing my notes](/blog/oblog/) but I don't publish all of them as a blog. It would be too noisy.
So here's a summary of them.

Travels

- [Lago di Garda Trip](/synced/lago-di-garda/)
- [Iceland Trip](/synced/iceland-2026/)
- [Antalya Trip](/synced/antalya-2026/)
- [Istanbul Trip](/synced/istanbul-aug-2026/)

Books

I'm still reading biographies mostly and some stuff in between.

- [Manna - Two Visions of Humanity's Future](/synced/manna-two-visions-of-humanitys-future/)
- [The Autobiography of Benjamin Franklin](/synced/the-autobiography-of-benjamin-franklin/)
- [My Inventions The Autobiography of Nikola Tesla](/synced/my-inventions-the-autobiography-of-nikola-tesla/)
- [How to Fail at Almost Everything and Still Win Big](/synced/how-to-failed-at-almost-everything-and-still-win-big/)
- [Do the Work](/synced/do-the-work/)

***

Links

- [Mel Blanc](https://nl.wikipedia.org/wiki/Mel_Blanc) - I love vocal impressions & just making random noises. I did not know that he's the voice behind most of Looney Tunes characters. I enjoyed watching his interviews of him doing impressions.
- I don't do android development actively but every time I have to do it's such a pain to set up. This blog tries to show how can you build android apps. https://www.hanshq.net/command-line-android.html
- I was out of stuff to watch on YouTube. I love [OverSimplified](https://www.youtube.com/OverSimplified) but I finished it so I found some good channels from https://thume.ca/2020/07/19/my-youtube-tier-list/ I enjoyed [Stuff Made Here](https://www.youtube.com/channel/UCj1VqrHhDte54oLgPG4xpuQ).