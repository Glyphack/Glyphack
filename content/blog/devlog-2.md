---
title: "Devlog 2"
date: 2024-11-02T11:11:05+01:00
draft: false
tags: [devlog]
---
Random notes from past month.

**New Projects**

I spent about a year building [my own tool-chain](https://github.com/Glyphack/enderpy) for building a python type checker. It inspired by what ruff was doing for Python linting and wanted to do the same for type checker.
A few months ago I found out that astral team are building a type checker. So I decided to redirect my energy toward that.
Building a type checker for a language that is not designed for typing is hard.
Sometimes you need to know what will be the exact behaviour of a type, and you see Pyright and Mypy have differences.
So naturally this requires you to do more research and figure out the specs yourself.

I was getting a lot of my guidance from the astral team. Because I'm not a python typing expert.
So I think this would be a better approach to contribute to that project and achieve my goal.
Also, Rust is a hard language and a lot of the time I felt like the language was stopping me from doing what I want.
So I had to read a lot on how to use it.
When contributing to another project, you have other people who will help with this kind of stuff.
So this is even better I don't need to fight the language any more, I can read their code and learn and help with typing.

Aside from that,
I'm building a C compiler from scratch with my friend. The goal is for it to compile itself.
https://github.com/keyvank/30cc

For some time I'm going to write my own projects in something other than Rust.
It was hard for me to work with it and focus on the project.
For learning projects I want to do it myself with minimal dependencies.
Rust can be tricky, and you need a dependency to save yourself from writing unsafe code.
Or the code becomes verbose and requires a lot of typing and organizing it.

**Terminal Workflow Improvements**

On of the things I've been wanting for a long time was the ability to jump to start of a command output in terminal. Imagine when you run something, and it outputs a lot of things.
When you want to see the beginning of the output or just read the logs from the beginning you need to scroll up.
This turns out to be easy to do but requires configuration for the terminal and shell you are using.
For Wezterm and Fish I did the following:

Set key bindings for [ScrollToPrompt](https://wezfurlong.org/wezterm/config/lua/keyassignment/ScrollToPrompt.html) action.
Create a fish function to emit the characters that marks the output of the command before executing a command.
```sh
function pre_command --on-event fish_preexec
    printf '\033]133;A\033\\'
end
```

This feature to run specific functions on an event in fish is really powerful. You can build custom workflows around your work. For example, you can do some project specific setup when entering a folder with this snippet:
```sh
function some_setup --on-variable PWD
    if test "$PWD" = "$PROGRAMMING_DIR/"
		# do some stuff
    end
end
```

**Neovim**

If you know how to fold all the functions by default please let me know.
<https://old.reddit.com/r/neovim/comments/1g41rjy/can_neovim_do_this_already_with_treesitter/>

I'm proud of myself for writing these two simple commands:
1. Key binding to insert a hyperlink in markdown file on visual selection
2. Command to go to the test file of the current go file I have open. Very useful at my job

```
vim.api.nvim_create_user_command("Link", function(opts)
	local start_pos = vim.fn.getpos("'<")
	local end_pos = vim.fn.getpos("'>")

	local selected_text = vim.fn.getline(start_pos[2]):sub(start_pos[3], end_pos[3])

	vim.api.nvim_command("normal! gv")
	if selected_text:match("^http") then
		vim.fn.setreg('"', "[](" .. selected_text .. ")")
		vim.api.nvim_command("normal! P")
		local new_pos = { start_pos[2], start_pos[3] - 1 }
		vim.api.nvim_win_set_cursor(0, new_pos)
	else
		vim.fn.setreg('"', "[" .. selected_text .. "]()")
		vim.api.nvim_command("normal! P")
		local new_pos = { start_pos[2], start_pos[3] + #selected_text + 2 }
		vim.api.nvim_win_set_cursor(0, new_pos)
	end
end, { range = true })

vim.keymap.set("v", "<leader>k", ":Link<CR>", { noremap = true, silent = true })

vim.api.nvim_create_user_command("GotoTest", function()
	local current_file = vim.fn.expand("%:p")
	local file_type = vim.bo.filetype
	local test_file

	if file_type == "go" then
		test_file = vim.fn.fnamemodify(current_file, ":r") .. "_test.go"
	else
		vim.api.nvim_err_writeln("Test file location not defined for filetype: " .. file_type)
		return
	end

	if vim.fn.filereadable(test_file) == 1 then
		vim.cmd("edit " .. test_file)
	else
		vim.api.nvim_err_writeln("Test file not found: " .. test_file)
	end
end, {})

```

I had a problem that when I connected my laptop to a new screen Flameshot would not capture the whole screen from the new screen in the screenshots.
I could not find a way to resolve this so I wrote this hammerspoon script to restart the app when I connect it to a new monitor:

```lua
local function screenCallback(layout)
	if layout == true then
		print("Screen did not change")
		return
	end
	setPrimary()

	local flameshot_bundle = "/Applications/flameshot.app"
	local flameshot = hs.application.find(flameshot_bundle, false, false)
	if flameshot then
		flameshot:kill()
	end
	hs.application.open(flameshot_bundle)
end

hs.screen.watcher.newWithActiveScreen(screenCallback):start()
```

---

* I knew about PyPy, but I didn't know they have a full tool chain for creating interpreters. Until I watched this [Tsoding video](https://www.youtube.com/watch?v=p8fCq16XTH4)
* Kay Lack's YouTube channel is one of the best things I found last month. High quality videos about computers and programming.
    This one is about [regex](https://youtube.com/watch?v=DiXMoBMWMmA&si=yqldVom-i92x7iSA) and [this one](https://www.youtube.com/watch?v=GU8MnZI0snA) assembly.
