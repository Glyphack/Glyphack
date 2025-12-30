---
title: "Blogging with Obsidian"
date: 2025-04-09T21:25:18+02:00
draft: false
tags: [] 
---
My blog is a bunch of files that are given to a program that converts them to HTML and CSS files, which is what you see here.

Also, Obsidian uses files to store my notes. This means it gives the most freedom than any other tool out there.

Since I've been writing both on my blog and in Obsidian there were times that I wanted to share stuff outside my Obsidian and link it in my website.
One way to do this is using Obsidian Publish, but after reading the [creator of Obsidian himself suggesting alternatives to it](https://www.reddit.com/r/ObsidianMD/comments/16e5jek/comment/jzv38ja/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button) I searched for ways to publish my notes on my blog.

There are great plugins that make this thing called digital garden (basically a website that you can browse) from Obsidian vault:

- <http://github.com/oleeskild/obsidian-digital-garden>
- <https://github.com/jackyzha0/quartz>

While they are good I was looking for something that I can use to generate the site myself.
So I can have my notes in the same theme as my blog, so it looks like the same page.

That's how I found [Obsidian Enveloppe](https://github.com/Enveloppe/obsidian-enveloppe), a plugin that helps you push files from Obsidian to Github.
I'm satisfied with the tool, it does the job with little complexity and composes well with user workflow.

So as a first step I decided to give it a shot, moving my reading list off Notion to my Blog.

This will allow me to use Obsidian as my editing tool and my Blog as the publishing tool.

## My setup

I create notes for books I read with my notes for the book.
These notes have special [front matter](https://gohugo.io/content-management/front-matter/) `category: [Books]` to specify it's a book.

Then I publish these notes to my blog repository in a special folder that I use to sync my notes. This sync is a one way sync. I'm not going to update these notes on Blog anymore.

The published notes will appear in my blog by default. Since Hugo just picks up all the markdown files and turns them into a page.

But these pages are not linked by default since they are not blog entries.
So I created this HTML page, that lists all the notes with "Books" category:

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

And I used it as the layout for a markdown page:

```markdown
---
title: "My Reading List"
layout: reading-list
draft: false
---

Here are some of the books I've read and plan to read.
```

Now I have a `/reading-list` page on my website, that filters all the notes related to books. And show them.

This shows how simple and without any magic you can publish Obsidian notes.
There are unlimited customizations that can be done. Like showing the books in a specific order or format. I left that out since it's lengthy and does not fit in the scope of this post.
Since I'm not using some dependency I am free to touch the HTML and change how my published notes look.

I like to see more people sharing their internal notes. If you do, share it with me. I like to read it.

Next I like to get create email subscriptions and comments for my blog.
