---
date: 2026-10-14
category:
  - "Blog"
tags:
title: I made a macOS Setup
---
Unlike Linux users, Mac users don't rice their systems and share these customizations.
Recently I've seen posts where people wanted to [try Linux on a Mac](https://www.reddit.com/r/omarchy/comments/1ogw249/how_feasible_is_omarchy_on_a_mac/) just for trying out a customized setup.
I think this is because of the lack of configured setups on macOS.
I like to be a power user of the tools I use, so I spent a fair amount of time learning tricks for [customizing macOS](/blog/macos-productivity/).

If you think it's impossible to customize macOS, you're wrong.
MacOS has user interface APIs that can be used to do almost anything you like.

So after completely disregarding [xkcd: Is It Worth the Time?](https://xkcd.com/1205/), I created [Clay](https://github.com/Glyphack/clay). It sets up your macOS with useful hotkeys and tools.
You can go ahead and [install it](https://github.com/Glyphack/clay#clay) or watch this video of me using it on a new Mac mini:
![](https://www.youtube.com/watch?v=MByiA57ExN8)

In short, this gives you minimal application switching and window management hotkeys plus some building blocks to make your setup.
The information about what's inside and what happens when you install it on your system is in the project.
The rest of this post will be about why I made it.

---

There are [some](https://github.com/geerlingguy/mac-dev-playbook) [scripts](https://github.com/MikeMcQuaid/strap/tree/main) that install apps and configure macOS settings.
But these setups leave the configuration up to you and don't come with hotkeys and ideas for improving the user experience.
Configuring the tools is done with dotfiles in these systems. This means that you need to do the configuration part for yourself.
This is fine for programmers, but I can't run it on my girlfriend's laptop.

I want the installer to be one command that does the whole setup, same as how popular Vim and Emacs distributions work.
You can customize the setup later.

Besides that, the idea of sharing a whole set of dotfiles is not practical.
I have my dotfiles and you can take some goodies for yourself.
But installing all of it on your computer means that you live with my personal preferences and I have a lot of them.
Also, some tools just have a single configuration file. If you have your own configuration, you cannot install someone else's configuration because it will replace it.

[Raycast](https://raycast.com/) is also an alternative way to customize macOS.
The problem with Raycast is that you cannot configure it through code.
This basically means sharing configurations is impossible.
That's why you have countless how-to videos for it, but there's no packaged configuration.

(Okay, not completely true. You can install it, then configure it and export the configuration, but updating that configuration is impossible since the configuration is binary.)

Another requirement was for it to be automated as much as possible.
There are [setup](https://github.com/nicolashery/mac-dev-setup) guides that require you to go through each step one by one.
A lot of these setups require you to navigate through settings pages after the installation to give permissions to each app.
Everything can be automated except for granting permissions.
The trick I found for that is to run `open "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"`.
This will open the accessibility window, so the only thing left is to toggle the access.

For the language, I wanted something other than bash so the program can actually handle errors, have nice data structures, and be able to surgically update some configuration so I don't just replace files if you already have them.
Doing this in bash is not impossible, but you end up with thousands of lines of fragile bash scripts.
That's why I chose Go.

The next question was what I put into the setup.
My dotfiles were a good place to start with this one because I had collected a lot of customizations over the years.
And the next step was to figure out which ones are generic enough that others will use them.

Hotkeys for navigation and window management are generally useful.
Based on posts like [this](https://x.com/tobi/status/2005106172316319758), I think people also like automations.

So after the installation, you:
- Can navigate between apps and browser tabs with the keyboard.
- Can code automations to control the speaker/mic or [run and hide apps on startup](https://www.reddit.com/r/macOS/comments/11sn0ih/run_and_hide_apps_at_startup_on_ventura/) if you like. But the code is minimal because there are functions available for each one.
- Don't have to go to the Settings app for better defaults, like a fast key press repeat rate.

Tiling window managers are getting a lot of attention. I tried them a few years ago and didn't like them.
The reason is that I usually use one application and that's full-screen. I don't like apps to open in small windows near each other.
So this is not included. But there are also a [lot](https://github.com/ianyh/Amethyst) of [options](https://github.com/asmvik/yabai) for this.

---

How do you access the user interface API of macOS for customization?
One way is to write apps that customize the behavior, like [this setup](https://github.com/paulsp94/omacosy/).
The other way is to use apps that let you customize macOS and write your configuration, like [this](https://www.youtube.com/watch?v=8pqFtkQip4I).
Although the first approach gives more freedom, it seems like too much work and maintenance for me.
So I chose the latter option, to configure pre-existing apps.
It will require less bug fixing, especially since these tools have existed for years and are stable.

---

Let me know what you think about it.
