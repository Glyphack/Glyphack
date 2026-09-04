---
date: 2026-09-04
category:
  - "Blog"
tags:
  - Active
title: Share Obsidian Notes To A Blog
---
A while back I started [sharing](/blog/ob/) my working notes on my blog.
This increased the amount of time I spend on writing.
As a result, developed a habit of [journaling](https://jon.bo/posts/on-journaling/) and keeping log of things I'm doing to the point that I spend about 1 hour writing these days.
I always liked reading [people's](https://jon.bo/posts/on-journaling/) [notes](https://jon.bo/posts/on-journaling/).
These notes while are not as polished as a blogpost they give you a different view into the person's mind.

Since last week I moved everything into Obsidian and just keep my blog for building the Markdown files and putting them on the internet.
This makes it so much easier for me because now I can reference all my notes and all of my writing happens in one place.

My goal is to share more stuff on my website by exporting them from Obsidian.
Using Obsidian never became a habit for me until I moved all my notes there.
I don't have a sophisticated workflow I write things down in files and link them together.
I don't need to sync my blog and notes manually anymore.
This is how I was able to share my [trips](/synced/trips/) and my [garden](/synced/garden/) online.

Currently the pages I share from my vault don't show up in the RSS feed.
But if A blogpost refers to a page from my vault that I shared it will have a link to that page.

I love this new setup I feel it made writing much more enjoyable and easier for me.
I'm going to share it with you.
You can copy it and use it.
Don't be tied to the specific tools here. Any editor or blog engine works. I happen to use Hugo but the technique I explain is transferable to any system.

## Why Move to Obsidian?

The main reasons I'm not in a Neovim buffer right now is mainly two things

- Syncing: I can jot something quickly on my phone before I forget and I have it on the computer to continue.
- Attachments: Adding and managing files and pictures to blogposts is always hard. With Obsidian I can even take a photo with my phone and attach it to a note.

I love Neovim as an editor. But not every note needs to be there. I enjoy the look and feel of Obsidian.
Sometimes I miss vim commands that are not available. But it's a compromise that I'm fine to make.

The reason I waited this long before doing this was the extensibility.
You can install plugins in Obsidian.
But I needed the ability to customize its behavior for myself, just like in Neovim.
Then I made a [personal plugin](https://github.com/Glyphack/dotfiles/tree/master/obsidian) and I started customizing anything I wanted.
You can have any custom command you like in it.
One of my favorite things is a command that I made to log what I'm doing to my current weekly notes.

This plugin can contain all the various customizations I like all in one and I don't even need to publish it anywhere.
I can install it locally in my vault directory and use it.
This was the step that made me use Obsidian more.


## Setup

My Obsidian and vault are separate. My blog is on GitHub.
I write notes in Obsidian and I sync it to GitHub.

I have created a custom command for myself that copies the notes that I want to publish to my blog folder on the same computer.

I create a note in Obsidian. It can be a blogpost or just a page.
I trigger the action "Insert Template" in Obsidian and insert my "Share Template".
This is the template:

```
---
share: true
title: ""
dest: ""
---
```

I can fill in `dest: blog/hello-world` and `title: Hello World`.
Now automatically this note is copied into the [content directory](https://gohugo.io/getting-started/directory-structure/) of my blog.

So then I have a new entry in my blog like this:

```
blog/
	content/
		Hello World/
			index.md
```

I chose the [page bundles](https://gohugo.io/content-management/page-bundles/) because it makes attachment management much easier. I'll talk about it in a section below.

That's it! I commit and push then my blog is updated. I can edit it with Obsidian and repeat.

There are some caveats to this.
How do you handle links to other pages?

## Standalone Pages

I make standalone pages similar to blogposts. I set the `dest` to `synced/hello-world`.
In Hugo only the `content/blog` directory is special and the rest of the pages can be anywhere in the `content` folder.
I save them to `content/synced/` to keep stuff organized.
Then it's easy to distinguish between the blogs and other notes.

If I want the page to have a different URL I can customize it by adding `url` to the front matter.
Hugo uses the front matter as well.

## Styled Pages

For some pages, like my [Bookshelf](/synced/reading-list/), I want custom styling.
This page is mostly HTML that is stored in the blog with a bit of Markdown that is in my notes.

The way this works is that I set a layout in the front matter of this note `layout: reading-list`.
In Hugo I can create a [layout](https://gohugo.io/methods/page/layout/) for it in `layouts/reading-list.html`:

```html
{{ define "main" }}
<article class="post">
  <header>
    <h1 class="post-title">{{ .Title }}</h1>
  </header>
  <div class="post-content">
    {{ .Content }}

    <h2>Books</h2>
    {{ $syncPages := where .Site.RegularPages "Section" "synced" }} {{ if
    $syncPages }}
    <ul>
      {{ range $syncPages }}
      <li>
        <a href="{{ .RelPermalink }}">{{ .File.BaseFileName }}</a>
      </li>
      {{ end }}
    </ul>
    {{ else }}
    <p>No sync pages found matching the criteria.</p>
    {{ end }}
  </div>
</article>
{{ end }}
```

Then Hugo uses this HTML to render that page.
The Markdown content will be shown at the top and the HTML follows.
The template can be more fancy like my [reading list](/synced/reading-list/) page.

This is a good separation.
I don't need the HTML templates in my Obsidian vault.
So they stay inside the blog and the note be in Obsidian.

## Links

This is the part that I spent most time getting it right.
I want my note links to work on my blog as well.

Obsidian uses wiki style links.
For example, `[[Some Note]]` in Obsidian needs to be converted to `[Some Note](Some link)`.

These are the rules I'm applying right now for this:

For `[[Some Note]]` first find the note.

If the note has `share: true` it means that it's published on the blog so it can be linked to blog itself.
Lookup the `dest` value to determine where the note is published at and convert the link to: `[Some Note]($dest_value)`.
If the note has an alias like `[[Some Note|this note]]` then use the alias for title: `[this note]($dest_value)`.

The notes can also carry a `source` front matter that is a URL.
If a Note 1 is published and has a links to Note 2 but Note 2 is not published then the link to Note 2 points to the `source` URL instead.
This way if I have a note about a concept I can point note's `source` to its Wikipedia and when I mention it in my blogs it would become a link to Wikipedia.

Other links stay as is, so any `[title](link)` stay as is.

Links like `[[other-note#heading]]` will end up as `[other-note](/path/to/note)`.
The heading information is dropped because I never link my posts in that way.

## Attachments

Attachments are exported along with the note that is published.
If a note mentions a file the file will be copied to the bundle directory.
Bundle is just a directory containing the post and it's attachment.

So if a note contains `![[my-image.png]]` it will be copied along with the note next to the `index.md` of that note.

For pictures I needed to strip data like location of the picture before publishing to blog.
Before copying pictures I use [EXIF tool](https://exiftool.org/) to remove that then copy the pictures.

Since a note and its attachments are inside a directory if anything changes about the note or attachments they are both updated and there will be no stale files.

## Unpublishing Notes

If I want to take something off my blog that was previously published I can toggle the `share` to `false` in the front matter.
This works because during the publish the program creates a file named `.dots-synced` that contains all the folders that were synced from Obsidian.
Also if something is renamed a new file will be created and the old one will be deleted.

## Missing Parts

There are some things that I haven't figured out yet.

What to do with [Dataview](https://blacksmithgu.github.io/obsidian-dataview/) queries? These queries are converted to lists in my Obsidian vault. But on the blog I generate lists with layouts. I currently don't publish this.

How to handle short codes?
This is a Hugo feature where you can put some JavaScript in the middle of a blog. I used it in [this post](/blog/huec/) to visualize the Hue payload format.
Currently I keep the short code in my blog and in the note I just refer to it.
It works and I'm not sure if I want to overengineer it to show in Obsidian as well.
Maybe using an iframe it can work inside Obsidian.

---

That's all I do for now to write on my blog.
I'm still not going to publish this as a plugin on Obsidian because it's very tailored to my own setup and I'm still experimenting with it.
There are some extra tips for customizing your vault with your own plugin, but those will wait for a dedicated post.
Meanwhile, you can read through my [dotfiles](https://github.com/Glyphack/dotfiles).