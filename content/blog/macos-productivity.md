---
title: "Personalize Macos Environment for Your Productivity"
date: 2023-02-19T20:58:33+01:00
draft: false
tags: [tools]
---

MacOS is already a polished environment and unlike some other OSes it works out of the box.
Still, spending investing time to personalize your tools and environment is a smart move.

In the past years using MacOS I found simple tools that helps to make MacOS more ergonomic and fun.

Most of the content here is in [my dotfiles](https://github.com/Glyphack/dotfiles).

## Why?

If you're already sold to this idea go ahead and start,
otherwise keep reading so I can convince you why you might want to start
configuring your tools.

I first heard the term
[Personalized Development Environment](https://www.youtube.com/watch?v=QMVIJhC9Veg)
in this video about configuring text editors to your liking and the idea stuck with me since then.

I think this approach works well with other tools too.
That's exactly people learn touch typing.
Being able to use keyboard with the least amount of effort is important.

You can go ahead with default configurations that come out of the box but those
are not built for you, they are for everyone.

I don't think automation is not primarily here to save your time only.
Automation is here to make it easier. Let me give you an example.
Imagine you have to constantly switch between editor and web browser constantly for some task.
Doing this with the default tools is annoying, requires a lot of keys. But it can be simpler.
Default tool for this is to either use the mouse, or ALT+Tab every time to move between windows.
Specialized tools can make this simpler by setting a shortcut for each of the windows. Making the toggle just one keybinding.

## Remapping Keys

[Karabiner](https://karabiner-elements.pqrs.org/) can be used to remap keyboard.

Try remapping the keys that you don't use often to things that you miss on the
keyboard, some examples are:

- Caps lock: key can be remapped to `Esc` key when pressed and Hyper Key when held
- `§`: which I don't know why is it here in the first place can be mapped to "\`"

There are more advanced keybindings that can be done I have [created keybindings](https://glyphack.com/blog/a-better-keyboard/) to write symbols like `*`, `-`, etc. without reaching for shift key and a number.
This helped a lot with keeping my hands near the home row and reducing the work my pinky finger has to do.

## Text Expanding

Text expanding is writing a small text and then it expands to a bigger text.

For example instead of typing your mail every time you,
can only write `:em` and it expands to your email address.

[Espanso](https://espanso.org/) is the tool I use for this.

Some examples I have are:

- `:date` to current date like 19/02/2023

## Raycast

[Raycast](https://www.raycast.com) is the single best application I have in this list.

What does it do?

It gives a launch bar(like Spotlight) that can open applications,
find files and perform actions. I suggest reading through their
[manual](https://manual.raycast.com/) to understand all it can do.
With Raycast you can integrate the stuff you need while reading/coding to quickly
pull them off without leaving your current work.

Raycast is easy to extend yourself, every time you find yourself doing something
over an over or need to open something regularly, take a look at it's
[store](https://www.raycast.com/store)
to check if there's a solution.

For example these are some of the things I'm using:
![My Raycast](/my-raycast.png)

[Search bookmarks](https://www.raycast.com/raycast/browser-bookmarks)
Start bookmarking any page you need to visit frequently, for example
homepages for your projects.

The reason this is handy is that, first you don't need to open browser to search
and through the history to open frequently visited pages also you don't have to
navigate through the pages to get to where you want.
Imagine navigating through Confluence to update some page you have to do everyday.
These days I just bookmark things I want to visit again and don't bother with organizing them.

Clipboard history & edit for traveling trough clipboard and change the content.

[Github](https://www.raycast.com/raycast/github)
extension is also useful to check notifications.
![Raycast Github](/raycast-github-pr.png)

## Hammerspoon

This one's the most powerful tool, it's a bridge between MacOS and Lua. You can
[customize anything](https://www.hammerspoon.org/docs/index.html)
with it's builtin libraries called spoons.

You can take a look at
[my config](https://github.com/Glyphack/dotfiles/blob/master/hammerspoon/init.lua)
for inspirations.

One useful feature if you do multiple meetings per day(which you probably do)
is it have a global shortcut to mute/unmute your mic to don't annoy others with
noise in the meeting and quickly unmute. I'm doing this with [global mute spoon](https://github.com/cmaahs/global-mute-spoon).

Here's how the configuration looks like

```lua
local GlobalMute = hs.loadSpoon("GlobalMute")
GlobalMute:bindHotkeys({
    toggle = { hyper, "t" }
})
```

For example I have a microphone that is both input and output device.
When I connect this microphone I don't want to set it as my output device but that's what mac does by default.
In Hammerspoon I can setup a callback to set my input/output device when the microphone is connected.

```lua
local function audiodeviceCallback()
    current = hs.audiodevice.defaultInputDevice():name()
    print("Current device: " .. current)
    if current == "External Microphone" then
      print("Forcing default output to Internal Speakers")
      hs.audiodevice.findOutputByName("MacBook Pro Speakers"):setDefaultOutputDevice()
    end
end

hs.audiodevice.watcher.setCallback(audiodeviceCallback)
hs.audiodevice.watcher.start()

```

## Switching Windows

Another Raycast feature is setting keybinding to open application windows.
This is useful when you want to have one application on the screen.
For example for me it's terminal and browser.
![Raycast Apps](/raycast-apps.png)

These days I'm using [a new solution](https://glyphack.com/blog/a-better-keyboard/) based on Hammerspoon for this.

## Terminal

If you made it through here you might as well be a CLI user.
This post is not about terminal as it's not related to MacOS but here are a few tips.

Use a fuzzy finder like [fzf](https://github.com/junegunn/fzf) for searching directories and history.
I have the following Fish keybinding to do a fuzzy search in my home directory and select a folder I want to `cd` into.

```fish
set -x FZF_ALT_C_COMMAND "fd -t d . $PROGRAMMING_DIR -d 3"
```

### Configure Git

A good one to start can be git,
you can setup [global ignore file](https://github.com/Glyphack/dotfiles/blob/master/gitconf/.gitignore_global) to ignore files for your specific environment in every project. So you don't need to add your `.idea` folder to every project.
[Aliases](https://github.com/Glyphack/dotfiles/blob/master/gitconf/.gitconfig) are useful for making shorter commands.

Git work trees are a perfect solution if you want to have access to multiple branches at the same time.
For example having the master branch and a feature branch allows you to run benchmarks on both at the same time.

### Neovim

There are a lot of guides to configure and work with Neovim,
I suggest [this](https://www.youtube.com/watch?v=w7i4amO_zaE)
and
[this](https://www.youtube.com/watch?v=stqUbv-5u2s).
You can also find the plugins/tools I use or think is interesting to check in my
[stars list](https://github.com/stars/Glyphack/lists/tools).

### Learn Your Code Editor

Even if you don't use something like Neovim,
your editor supports a lot of customization, and should be customized.
When you find some action requires a lot of effort, try to customize it in your Editor.

For example, most of the time I stage part of the file I'm editing for commits.
In VSCode you need to open the version control panel,
scroll through the file and right click to select stage selected.
This is super hard if you have to do it 20 times in a productive day.
I have a config in my vim to directly stage hunks in my editor to commit,
but I'm sure you can find a VSCode equivalent.
