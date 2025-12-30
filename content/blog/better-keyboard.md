---
title: "A Better Keyboard"
date: 2023-12-30T10:54:35+01:00
draft: false
tags: [tools]
---

Imagine you want to make a better keyboard.
Seems like a hard challenge for every company.
What if 'better' meant compressing multiple key presses into one? Or have shortcut for your frequent actions.
If you minimize the effort to use it then you are making it better for yourself.

Challenge lies in the keyboard's limited keys, and hard to press combinations like `ctrl + alt + any key`.

Most of us learn to use tools as they are.
But most of the time the product is not tailored to your needs out of the box.

None of the products produced are going to be designed based on your specific needs.
One of the advantages of trying to use keyboard to make repetitive tasks easier is to reduce the attention needed for them.
When these tasks will be easy enough that doing them [won't require attention](https://www.scattered-thoughts.net/writing/moving-faster/).
Just like how when you learn touch typing, and suddenly you are just writing instead of looking at the keyboard, or frequently press the wrong key.
You get faster.

Before going into details, keep in mind that the goal is to make your workflow easier.
Some of these suggestions might be useful and others might be not.
Take away the ideas with yourself and adjust it accordingly.

I implemented the improvements using the following tools:

- [Hammerspoon](https://www.hammerspoon.org/)
- [Karabiner](https://karabiner-elements.pqrs.org/)

These tools are exclusively for Mac. There are other alternatives for other platforms.

## Remapping Keys

Our keyboards are not designed for heavy usage of shortcuts.
So you can start making shortcuts for stuff by setting them to `ctrl + T`,

This method presents two significant challenges:

- The easily accessible keys are already assigned, such as `CMD + T`.
- Complex combinations become cumbersome: try pressing `CMD + ALT + ctrl + T`.

The idea is that some keys can be used to do more than one thing.
What keys can be used like this? Let's take a look at different keys.

- Keys you hold down to change how _other_ keys behave, but that (usually) don't do anything if you use them on their own (like Shift and Control).
  - `Shift`
  - `Control`
  - `Alt`
  - `Command`
  - `Fn`
- Keys that you press and release but don't want to "repeat" as you hold them (like Escape or Insert).
  - `Escape`
  - `Caps lock`

You can use the keys that are designed to only be held to do a new thing if they are pressed. Or use the keys that are designed to be pressed to do another thing if they are held.

For example, I have set the following setting for Caps lock keys:

- On hold: hyper key `ctrl + SHIFT + ALT`
- On press: escape

Why hyper?
Because this new key press cannot conflict with any other shortcuts
This allows you to create shortcuts like: hyper + H/J/K/L which is pretty comfortable to press.

I used to have CAPS lock set to `CMD + ctrl + SHIFT + ALT`.
But I noticed that there is a MacOS specific key binding for taking a system snapshot with `CMD + ctrl + shift + alt + ,` which cannot be disabled and my system froze when I accidentally pressed this key.
So I stopped using it and switched to the above combination instead.

You can do this using a [complex modification](https://karabiner-elements.pqrs.org/docs/manual/configuration/configure-complex-modifications/#create-your-own-rules) in Karabiner:

```
{
    "description": "Capslock to Hyper",
    "manipulators": [
        {
            "description": "Click to Capslock, Hold to Hyper",
            "from": {
                "key_code": "caps_lock",
                "modifiers": {
                    "optional": [
                        "any"
                    ]
                }
            },
            "to": [
                {
                    "key_code": "right_shift",
                    "modifiers": [
                        "right_control",
                        "right_option"
                    ]
                }
            ],
            "to_if_alone": [
                {
                    "key_code": "escape"
                }
            ],
            "type": "basic"
        }
    ]
}
```

This key now can be used as your new shortcut key.
`hyper + t` can be mapped to an action globally and does not conflict with anything.
So any key on the keyboard can now be used for shortcuts, allowing numerous customization.

If there are keys on your keyboard that you don't use you can map them to frequently used keys.
For example for vim users, the right command key on macs can be remapped to control.
This makes pressing vim shortcuts like `ctrl + A` easier.

I have a split keyboard, so keys under my thumbs are easy to press, and I remapped them to do more stuff than usual.

![](/split-keyboard-remapping.excalidraw.svg)

I changed a lot of keys since then but the ideas are useful. Just find the keys that works best for you.

## Window Switching

There are some default hotkeys on every system like `alt+tab`.
This gives you a bit more advantage over switching windows with a mouse, [but there is room for improvements](https://www.youtube.com/watch?app=desktop&v=Px0_8J0Wb-s).
These shortcuts are designed for general problems.
You can improve it for your own workflow.

First example is alt tabbing to switch windows.
This simple thing that you probably do 100 times a day requires to:

- Take hand off home row
- Press them multiple times to find the window you want
- And if you have multiple windows then press `ctrl+tab` or `command+~` to get there
  Wouldn't it be good if you could do 80% of these window switches with a single shortcut that is more ergonomic?
  It depends, I switch between Browser, terminal and note app multiple times most of the time.
  You can assign a hotkey for these and only use alt tab for when you need to switch infrequently used windows.

Here's the solution I use based on [this post](https://rakhesh.com/coding/using-hammerspoon-to-switch-apps/)

```lua
WINDOW_MANAGEMENT_KEY = { "alt", "command", "ctrl" }
WINDOWS_SHORTCUTS = {
 { "J", "Brave Browser" },
 { "K", "WezTerm" },
}

local function launchOrFocusOrRotate(app)
 local focusedWindow = hs.window.focusedWindow()
 if focusedWindow == nil then
  hs.application.launchOrFocus(app)
  return
 end

 local focusedWindowApp = focusedWindow:application()
 local focusedWindowAppName = focusedWindowApp:name()
 local focusedWindowPath = focusedWindowApp:path()
 local appNameOnDisk = string.gsub(focusedWindowPath, "/Applications/", "")
 local appNameOnDisk = string.gsub(appNameOnDisk, ".app", "")
 local appNameOnDisk = string.gsub(appNameOnDisk, "/System/Library/CoreServices/", "")
 if focusedWindow and appNameOnDisk == app then
  local currentApp = hs.application.get(focusedWindowAppName)
  local appWindows = currentApp:allWindows()
  -- https://www.hammerspoon.org/docs/hs.application.html#allWindows
  -- A table of zero or more hs.window objects owned by the application. From the current space.
  if #appWindows == 1 then
   currentApp:hide()
   return
  end

  if #appWindows > 0 then
   -- It seems that this list order changes after one window get focused,
   -- Let's directly bring the last one to focus every time
   -- https://www.hammerspoon.org/docs/hs.window.html#focus
   if app == "Finder" then
    -- If the app is Finder the window count returned is one more than the actual count, so I subtract
    appWindows[#appWindows - 1]:focus()
   else
    appWindows[#appWindows]:focus()
   end
  else
   hs.application.launchOrFocus(app)
  end
 else
  hs.application.launchOrFocus(app)
 end
end

for _, shortcut in ipairs(WINDOWS_SHORTCUTS) do
 hs.hotkey.bind(WINDOW_MANAGEMENT_KEY, shortcut[1], function()
  launchOrFocusOrRotate(shortcut[2])
 end)
end
```

The lua table can be easily expanded to open more applications.

## Shortcut for frequent actions

Other than switching apps there are some useful tools that is nice to have at hand.

Some suggestions are:

- [Viewing calendar and reminders](https://www.raycast.com/extensions/calendar)
- [Clipboard history](https://www.raycast.com/extensions/clipboard-history)
- [Fuzzy find and open browser bookmarks](https://www.raycast.com/raycast/browser-bookmarks)
- [Splitting, resizing & moving windows](https://www.hammerspoon.org/docs/hs.grid.html#:~:text=To%20resize%2Fmove%20the%20window,upper%2Dleft%20of%20the%20window.)
- [Fuzzy find open windows](https://www.raycast.com/changelog/1-19-0)

Raycast is easier to use for things you need to browse and search.
For actions that don't include search and selection Hammerspoon is good.

These mappings can look like this:

```
hyper + A move window to left half of the screen
hyper + S move window to bottom half of the screen
hyper + D move window to right half of the screen
hyper + W move window to top half of the screen
hyper + L clipboard history
hyper + ; browser bookmarks
hyper + M search open windows
```

The following Hammerspoon config allows moving windows with shortcuts:

```lua
-- left
hs.hotkey.bind(WINDOW_MANAGEMENT_KEY, "a", function()
 hs.window.focusedWindow():moveToUnit({ 0, 0, 0.5, 1 })
end)
-- right
hs.hotkey.bind(WINDOW_MANAGEMENT_KEY, "d", function()
 hs.window.focusedWindow():moveToUnit({ 0.5, 0, 0.5, 1 })
end)
-- up
hs.hotkey.bind(WINDOW_MANAGEMENT_KEY, "w", function()
 hs.window.focusedWindow():moveToUnit({ 0, 0, 1, 0.5 })
end)
-- down
hs.hotkey.bind(WINDOW_MANAGEMENT_KEY, "s", function()
 hs.window.focusedWindow():moveToUnit({ 0, 0.5, 1, 0.5 })
end)
-- center
hs.hotkey.bind(WINDOW_MANAGEMENT_KEY, "c", function()
 hs.window.focusedWindow():centerOnScreen()
end)
-- full screen
hs.hotkey.bind(WINDOW_MANAGEMENT_KEY, "i", function()
 hs.window.focusedWindow():moveToUnit({ 0, 0, 1, 1 })
end)
```

You can also use a layout mode for moving windows:
<https://github.com/jasonrudolph/keyboard#window-layout-mode>

## Symbol Layers

If you code a lot this will be your favorite section.
Have you noticed how hard it is to type `_`?
You need to take fingers off the home row, hold shift and press a key.
Both keys are pressed with pinky fingers.

I find the idea [here](https://gist.github.com/gsinclair/f4ab34da53034374eb6164698a0a8ace),
it suggests to map `(holding s)+k` to a symbol like `-`.

The idea is very similar to how we define different toggle and press behavior to keys.
With Karabiner, you can modify s key to act like normal s but when pressed simultaneously with k become `-`.

Concerned about accidentally typing `sk` or `-`? You can adjust the speed at which the shortcut triggers with the
[hold down option](https://karabiner-elements.pqrs.org/docs/json/complex-modifications-manipulator-definition/to/hold-down-milliseconds/).

So imagine the following layout:

```
    y u i o
a   h j k l
    n m , .
```

When you hold a with left hand and any of the right keys it can be mapped to a symbol.

Here's my layout. I mention the key you need to hold on the left and what new keys are mapped to on the right.

`s` for symbols:

```
    y ` u # i $ o %
s   h ~ j - k - l !
    n   m + , + . @
```

`f` for delimiters:

```
    y   u { i } o ^
f   h < j ( k ) l &
    n > m [ , ] . *
```

So just set these stuff for different combinations that are hard to press.
I even have `a+u` for `tab` and `a+i` for `ctrl+tab`.

For implementing this in Karabiner follow the guide above.
Since Karabiner uses json files for configuration writing all of this by hand is time consuming. You can use a tool like Goku (brew install yqrashawn/goku/goku) instead.
Here is my [giant json](https://github.com/Glyphack/dotfiles/blob/20b97e675532db0bf8d73068fec1dd3050ad2fc5/karabiner/karabiner.json#L1) Karabiner configuration.

For doing normal JSON you need the following Karabiner rules for :

```
{
                "from": {
                  "key_code": "u",
                  "modifiers": {
                    "optional": [
                      "any"
                    ]
                  }
                },
                "to": [
                  {
                    "key_code": "open_bracket",
                    "modifiers": [
                      "left_shift"
                    ]
                  }
                ],
                "conditions": [
                  {
                    "name": "f-mode",
                    "value": 1,
                    "type": "variable_if"
                  }
                ],
                "type": "basic"
              },
              {
                "type": "basic",
                "parameters": {
                  "basic.simultaneous_threshold_milliseconds": 250
                },
                "to": [
                  {
                    "set_variable": {
                      "name": "f-mode",
                      "value": 1
                    }
                  },
                  {
                    "key_code": "open_bracket",
                    "modifiers": [
                      "left_shift"
                    ]
                  }
                ],
                "from": {
                  "simultaneous": [
                    {
                      "key_code": "f"
                    },
                    {
                      "key_code": "u"
                    }
                  ],
                  "simultaneous_options": {
                    "detect_key_down_uninterruptedly": true,
                    "key_down_order": "strict",
                    "key_up_order": "strict_inverse",
                    "key_up_when": "any",
                    "to_after_key_up": [
                      {
                        "set_variable": {
                          "name": "f-mode",
                          "value": 0
                        }
                      }
                    ]
                  }
                }
              }
```

## Not Only Speed but ergonomics

These customization help with removing uncomfortable keys you need to press.
The benefits are immediate - less strain on your fingers and wrists due to reduced movement, and a mind unburdened from managing mundane tasks like locating the Terminal window.
