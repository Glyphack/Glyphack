---
title: "Personalize Macos Environment for Your Productivity"
date: 2023-02-19T20:58:33+01:00
draft: false
tags: [tools]
---

MacOS is already a polished environment,

Investing the time to personalize your tools and environment is a smart move,
especially if you plan to do your current profession for years to come.
With a set of personalized methods and tools,
you can make your routine tasks easier and more efficient.

In this guide, we'll explore methods and tools that can help you personalize
your environment to suit your needs as a developer.
While not everything may be applicable to you,
you're sure to find some good ideas to steal or improve upon.
We'll go through a list of regular tasks that developers face and
show you how customized tools can make your work easier and more enjoyable.

## Why?

If you're already sold to this idea go ahead and start,
otherwise keep reading so I can convince you why you might want to start
configuring your tools.

I first heard the term
[Personalized Development Environment](https://www.youtube.com/watch?v=QMVIJhC9Veg)
in the video he talks about why configuring Neovim editor for yourself is
useful and good investment.

I think this approach works well with other tools too.
If you are going to spend 20 years in this profession,
you need your customized tools and environment to work with.
That's exactly why you learn touch typing.
Being able to use keyboard with the least amount of effort is important.

You can go ahead with default configurations that come out of the box but those
are not built for you, they are for everyone.
Apple does not know you are going to a lot of meetings everyday and need ready
tools to attend them.
They don't know your job involves constantly switching between two windows.

All of these actions have cognitive overhead to do with default settings.
This automations are not primarily here to save your time,
they are here so you can complete your stuff more easily.
If you need to constantly search some documentation while coding,
it's a lot if you have to altTab to your browser find the browser tab and
write in the search box, what if you could get a floating window that give you
what you need inside the text editor so you don't loose the focus?
or even worse opening the browser and end up scrolling reddit.

## How to Start

Since this is all about your own workflow,
I can't give you instructions on what to configure.

But I give you ideas about what can be done,
and next time you wish something was easier to do take a look and see
which tool can help you with it.

### Keyboard

Keyboard is the main input to do your work,
there's not much to customize about the mouse but keyboard has a lot of possibilities.

note that using the following tools without knowing touch typing is not possible.

### Remapping

Try remapping the keys that you don't use often to things that you miss on the
keyboard, some examples are:

- Caps lock: key can be remapped to Esc, especially if you use vim
- Fn keys: I added media control to stop/play and move between songs
- `§`: which I don't know why is it here in the first place can be mapped to "`"

[Karabiner](https://karabiner-elements.pqrs.org/) can be used for this purpose.

it supports more [complex modifications](https://ke-complex-modifications.pqrs.org/)
which include things like adding a shortcut for sleep.

### Expanding

Text expanding is writing a small text and then it expands to a bigger text.

For example instead of typing your work mail every time you,
can only wirte `,wm` and it expands to your work mail.

[TexExpander](https://textexpander.com/) is the tool I use for this.

Some examples I have are:

- `,date` to current date like 19/02/2023
- multiple shortcuts to write my email addresses

You can also have macros for run javascript code to format something,
for example this snippet and format json in my clipboard for when I need
to share something with others:

```js
JSON﻿.﻿stringify﻿(﻿%clipboard, null﻿, 2﻿)﻿;
```

This is so powerful for me,
I deal with a lot of json outputs everyday and being able to format it without
opening a website and paste the json in and format it to look at what it I can
continue my work in my environment.

### Raycast

While other suggestions have multiple implementations that you can use,
I don't think there's a better launcher than [Raycast](https://www.raycast.com).

What does it do?

It gives a launch bar(like Spotlight) that can open applications,
find files and perform actions. I suggest reading through their
[manual](https://manual.raycast.com/) to understand all it can do.
With Raycast you can integrate the stuff you need while reading/coding to quickly
pull them off without leaving your current work.

#### Extensions

Raycast is easy to extend yourself, every time you find yourself doing something
over an over or need to open something regularly, take a look at it's
[store](https://www.raycast.com/store)
to check if there's a solution.

After installing the extensions you can configure them or set shortcuts by
searching "extensions" in Raycast search bar.

For example these are some of the things I'm using
![My Raycast](/my-raycast.png)

Notice that you can [set hotkeys](https://raycastapp.notion.site/Command-Aliases-and-Hotkeys-43cba38c19dd4000bc75404c11eb0f80)
for most used commands to activate them immediately.

[Search bookmarks](https://www.raycast.com/raycast/browser-bookmarks)
Start bookmarking any page you need to visit frequently, for example your
team Jira board, AWS account, Homepages for your projects, or university portal.
Then use this extension to search the page you want to open from bookmarks and
open it with.

The reason this is handy is that, first you don't need to open browser to search
and through the history to open frequently visited pages also you don't have to
navigate through the pages to get to where you want.
Imagine navigating through Confluence to update some page you have to do everyday.

Clipboard history & edit for traveling trough clipboard and change the content.

[Calendar](https://raycastapp.notion.site/Calendar-b4bdcf402a024c37940e46e8dcf2da91)
to check the events and join them.

[AWS](https://github.com/raycast/extensions/blob/4d68ff23122d5505ab1be6dc595427f8f95fa7ea/extensions/amazon-aws/README.md)
extension to browse resources, everyone knows AWS console sucks and is slow.
Fun note: I previously tried to implement the same for
[slapdash](https://github.com/Glyphack/aws-slapdash/)
after writing a plugin for them realized their APIs are not developer friendly.
And this is a risk because the usefulness of these products are tied to developers.

[Github](https://www.raycast.com/raycast/github)
Can be useful if you happen to do open source, it can search repos,
and PRs:
![Raycast Github](/raycast-github-pr.png)

#### Apps

Another feature is to manage some application windows with hotkeys.
This is useful 1,2 applications where you switch them all the time.
For example for me it's terminal and browser:
![Raycas Apps](/raycast-apps.png)

With this setting not only you can launch the app but you can focus the window
anywhere with hotkey.

#### Quicklinks

Last feature to setup is Quicklinks,
with this you can predefine sites to open with some parameters,
this can be used to search google, or translate a world.
![Raycas Quicklinks](/raycast-quicklinks.png)

## Automation tools

### Hammerspoon

This one's the most powerful tool, it's a bridge between MacOS and Lua. You can
[customize anything](https://www.hammerspoon.org/docs/index.html)
with it's builtin libraries called spoons.

You can take a look at
[my config](https://github.com/Glyphack/dotfiles/blob/master/hammerspoon/init.lua)
for inspirations. The rest are explanations of my config.

One useful feature if you do multiple meetings per day(which you probably do)
is it have a global shortcut to mute/unmute your mic to don't annoy others with
noise in the meeting and quickly unmute. I'm doing this with [global mute spoon](https://github.com/cmaahs/global-mute-spoon).

Here's how the configuration looks like

```lua
local GlobalMute = hs.loadSpoon("GlobalMute")
GlobalMute:bindHotkeys({
    unmute = { lesshyper, "u" },
    mute   = { lesshyper, "m" },
    toggle = { hyper, "t" }
})
```

I also use Hammerspoon to set my audio devices when different devices are connected.
this one sets my output to speakers when my external mic & speaker is connected:

```lua
local function switchOutputAfterExternalMicConnected()
    current = hs.audiodevice.defaultInputDevice():name()
    print("Current device: " .. current)
    if current == "External Microphone" then
      print("Forcing default output to Internal Speakers")
      hs.audiodevice.findOutputByName("MacBook Pro Speakers"):setDefaultOutputDevice()
    end
end
```

### Crontab

If you need to execute something regularly, create a crontab for it.
MacOS has [crontab](https://alvinalexander.com/mac-os-x/mac-osx-startup-crontab-launchd-jobs/)
which you can use for this.

Also can create push notifications using hammerspoon and
calling an API to check for new notifications(for example Github).

## Terminal

I assume you do use terminal a lot,
otherwise you would not read this far cause developers who don't use terminal
effectively don't care much about the previous stuff either.

Terminal is designed to be configured with functions for frequent commands.

I'm not gonna talk much about terminal but just make sure to:

- Use a [fuzzy finder](https://github.com/junegunn/fzf)
  for searching directories and history
- Create a lot of functions for frequent used commands

### Create Functions

For example I used to record a lot videos for my team and share them,
but had to compress them before so I created this function:

```fish
function compress_vid
    ffmpeg -i $argv -vcodec h264 -acodec aac -strict -2 output.mp4
end
```

Or you might be doing a lot of
[dynamoDB](https://github.com/Glyphack/dotfiles/blob/master/fish/functions/start-dynamodb.fish)
and
[Kafka](https://github.com/Glyphack/dotfiles/blob/master/fish/functions/start-kafka.fish)
development so have commands to ready your environment for test.

I'm using fish but this can be applied to other shells as well.
In case you regularly run particular commands like activating the python virtualenv,
use a hook to auto activate it for you.
I'm using [virtualFish](https://github.com/justinmayer/virtualfish) for this.

### Fuzzy Finder

After you installed fzf make sure to configure it for these shortcuts:

- [Alt+C](https://github.com/Glyphack/dotfiles/blob/master/fish/config.fish#L12)
  for searching and navigating to a directory
- [Ctrl+T](https://github.com/Glyphack/dotfiles/blob/master/fish/config.fish#L11)
  to search the current dir and use the path
- Ctrl+R to search the history

This Alt+C command is really handy for me to navigate and open projects,
you can see that I set it to only search my development directory.

Also learn to configure the tools you use often,
read their manuals to find out what features they have that might be useful for you.

### Configure Git

A good one to start can be git,
you can setup [global ignore file](https://github.com/Glyphack/dotfiles/blob/master/gitconf/.gitignore_global),
[aliases](https://github.com/Glyphack/dotfiles/blob/master/gitconf/.gitconfig#L8)
and optional configurations for some projects.
For example I override some configs when I'm in my company projects folder.

Take advantage of TUI apps like [lazy-git](https://github.com/jesseduffield/lazygit),
to make your work easier.

IMO the only way to work with git should not be the git client in your text editor.
Having to open the text editor for only git operations might take your focus.

### Starship

Use [Starship](https://starship.rs/),
it can give you information about the directory your in,
like what git branch are you on or what AWS account is current being used.

I use [this setting to](https://github.com/Glyphack/dotfiles/blob/cc7bd423da69321036d1eba8ece9316801f6bd85/starship/starship.toml#L3)
have the AWS account name and region

### AWS

Since I mentioned AWS, make sure to use one of [aws-vault](https://github.com/99designs/aws-vault) or [aws-sso-util](https://github.com/benkehoe/aws-sso-util) to switch AWS accounts. You should be able to switch quickly for your testing and development, and this does not have to involve going to console and copying credentials every time.

### Neovim

There are a lot of guides to configure and work with Neovim,
I suggest [this](https://www.youtube.com/watch?v=w7i4amO_zaE)
and
[this](https://www.youtube.com/watch?v=stqUbv-5u2s).
You can also find the plugins/tools I use or think is interesting to check in my
[stars list](https://github.com/stars/Glyphack/lists/tools).

### Learn Your Code Editor

Even if you don't use something like Neovim,
your editor supports a lot of customizations, and should be customized.
When you find some action requires a lot of effort, try to customize it in your Editor.

For example, most of the time I stage part of the file I'm editing for commits.
In VSCode you need to open the version control panel,
scroll through the file and right click to select stage selected.
This is super hard if you have to do it 20 times in a productive day.
I have a config in my vim to directly stage hunks in my editor to commit,
but I'm sure you can find a VSCode equivalent.

The moral of this part is,
no matter what editor you use after you realized some set of
actions are the ones you do more than others try to customize your editor to
allow those actions to be done more easily,
without taking you out of the zone.

## Conclusion

This was a long post, I wanted to go through my own configuration and
update some stuff so decided to share it here as well.

Hope it's useful for you and don't forget the main point,
customize your tools for your job to be able to get things done with less thinking.

If you use other tools customizations I'll be happy to hear them.
