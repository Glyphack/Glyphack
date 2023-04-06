---
title: "Building a Web Crawler in Golang"
date: 2023-03-20T18:17:24+01:00
draft: false
tags: ["coding"]
---

<!-- vim-markdown-toc GFM -->

- [Introduction](#introduction)
- [But Why Building Another Crawler?](#but-why-building-another-crawler)
- [High Level Design](#high-level-design)
  - [URL Frontier](#url-frontier)
  - [Selector](#selector)
  - [Workers](#workers)
  - [Fetcher](#fetcher)
  - [Content Processor](#content-processor)
  - [Link Extractor](#link-extractor)
- [Implementation](#implementation)
  - [Let's talk about channels](#lets-talk-about-channels)
  - [Storage](#storage)
  - [Parser](#parser)
  - [Processor](#processor)
  - [Distribute and Collect Result from Workers](#distribute-and-collect-result-from-workers)
  - [Worker](#worker)
  - [Extracting Links](#extracting-links)
  - [Saving Content](#saving-content)
  - [Running Processors](#running-processors)
  - [Failed URLs](#failed-urls)
  - [HTML parser](#html-parser)
  - [Putting it All Together](#putting-it-all-together)
- [Conclusion](#conclusion)

<!-- vim-markdown-toc -->

## Introduction

Web crawler is a program that explores the Internet,
by going to different websites and following any link it finds.

Crawlers are interesting because they provide a way to gather data
from the internet.
This is especially useful for data mining purposes.

You can find the full implementation in the [GitHub repository](https://github.com/Glyphack/crawler).

[This post](https://cacm.acm.org/blogs/blog-cacm/153780-data-mining-the-web-via-crawling/fulltext)
provides a good introduction to building a crawler.

## But Why Building Another Crawler?

I wrote down my reasons in the [previous post](/rate-limiter-from-scratch-in-python-2)
on why I'm building this stuff from sctrach.
The short answer is that it seems simple until you try it.

After reading through this project and implementing yourself,
you will have a good understanding of how to write concurrent
applications in Go.

## High Level Design

Let's look into what components a cralwer is made of, this helps
to structure our code.

The following diagram shows the execution flow of our program and
responsibilities of components:

![crawler-diagram](/crawler-diagram.excalidraw.svg)

Let's break it down:

### URL Frontier

URL Frontier is a collection of URLs that are going to be crawled.
It supports adding & consuming new URLs as we discover links in fetched pages.

### Selector

To consume the URLs from frontier we can get them one by one.
But this can cause problem if we want to distribute the URLs between multiple workers.

The technique used here is called fan-out.

For example if some URLs are more important to crawl first, and each worker gets
the next URL to crawl then those special URLs can't be crawled first.
Another usefulness of this component is distributing URLs from one host to one worker.
So each worker can make sure to not send too many requests to a single Host.
The best practice is to wait 2 seconds between requests for the same Host.

### Workers

Each worker consumes from queues that selector fills and fetches the URL.

The worker must handle failures and retry when it fails to fetch a URL.
Each worker also keeps track of URLs fetched to be polite.

### Fetcher

This components is the reverse of selector component, it gathers
results from different workers to a single collection.

This operation is called fan-in which is useful here because we
can simplify the processor operations because it only needs to
consume from a single result channel.

### Content Processor

After we get the result from each worker we ran different
content processors on the result, this can be tasks like extracting
new URLs or saving pages to the disk.

Also note that this component does not apply a single
logic on all results. We can register different processors,
like a plugin system to expand this component.

Later we discuss how we can use strategy design pattern to
implement this in code.

### Link Extractor

The link extractor is a special processor we create
that uses a parser to parse the page content and insert URLs
back to frontier.

## Implementation

### Let's talk about channels

channels are going to be used heavily in the implementation.
I suggest you to make sure you understand [fundamentals](https://go.dev/tour/concurrency/1)
of channels.
before reading the rest of this post.

We can start with frontier since it's not dependent on any other component.

I'll create a new package frontier:

```go
type Frontier struct {
    urls        chan *url.URL
    history     map[url.URL]time.Time
    exclude     []string
}

func NewFrontier(initialUrls []url.URL, exclude []string) *Frontier {
    history := make(map[url.URL]time.Time)
    f := &Frontier{
        urls:    make(chan *url.URL, len(initialUrls)),
        history: history,
        exclude: exclude,
    }

    for _, u := range initialUrls {
        f.Add(&u)
    }
    return f
}
```

The frontier uses a channel of urls to keep the added URLs.
Since the channel is consumed then we keep a `history` of visited URLs.
History can be later used to check whether we seen a URL or not.

The `terminating` attribute is used so we can have a graceful termination.
Since another goroutine is going to read from this channel, we might
want to wait until all the URLs are consumed and meanwhile don't add any new URLs.

Next we need a method to add a new url.

```go
func (f *Frontier) Add(url *url.URL) bool {
    if f.terminating {
        return false
    }
    if f.Seen(url) {
        log.WithFields(log.Fields{
            "url": url,
        }).Info("Already seen")
        return false
    }
    for _, pattern := range f.exclude {
        if pattern == url.Host {
            log.WithFields(log.Fields{
                "url": url,
            }).Info("Excluded")
            return false
        }
    }
    f.history[*url] = time.Now()
    f.urls <- url

    return true
}

func (f *Frontier) Seen(url *url.URL) bool {
    if lastFetch, ok := f.history[*url]; ok {
        return time.Since(lastFetch) < 2*time.Hour
    }
    return false
}

func (f *Frontier) Get() chan *url.URL {
    return f.urls
}
```

This method simply checks if the url is seen or not and if it's not
excluded adds it to the channel.

This function is blocking unless another gorutine is consuming from the urls channel.
Why is this important?
because if we run the Add in a blocking way without consuming the urls
we will block the goroutine & it's a deadlock.

The `Get` function does not provide any abstraction here, but I like the idea that
consumers don't have to know which channel they need to consume from.

In case you are wondering what log package I'm using, it's [logrus](https://github.com/sirupsen/logrus).

The next step is to create the component and orchestrates the crawl process.

Let's first define the configuration that user can pass to the crawler.

```go
type Config struct {
    MaxRedirects    int
    RevisitDelay    time.Duration
    WorkerCount     int
    ExcludePatterns []string
}
```

```go
package crawler

import (
    "net/url"

    log "github.com/sirupsen/logrus"

    "github.com/glyphack/crawler/internal/frontier"
    "github.com/glyphack/crawler/internal/parser"
    "github.com/glyphack/crawler/internal/storage"
)

type Crawler struct {
    config         *Config
    frontier       *frontier.Frontier
    storage        storage.Storage
    contentParsers []parser.Parser
    deadLetter     chan *url.URL
    processors     []Processor
}

func NewCrawler(initialUrls []url.URL, contentStorage storage.Storage, config *Config) *Crawler {
    deadLetter := make(chan *url.URL)
    contentParser := []parser.Parser{&parser.HtmlParser{}}
    return &Crawler{
        frontier:       frontier.NewFrontier(initialUrls, config.ExcludePatterns),
        storage:        contentStorage,
        contentParsers: contentParser,
        deadLetter:     deadLetter,
        config:         config,
    }
}

func (c *Crawler) AddContentParser(contentParser parser.Parser) {
    a.contentParsers = append(c.contentParsers, contentParser)
}

func (c *Crawler) AddExcludePattern(pattern string) {
    c.config.ExcludePatterns = append(c.config.ExcludePatterns, pattern)
}

func (c *Crawler) AddProcessor(processor Processor) {
    c.processors = append(c.processors, processor)
}
```

Config comes from the user and by making it a separate struct we can easily modify
it without changing the parameters we pass to create the crawler.
We keep a deadLetter channel for the failed URLs to have a retry mechanism.

The crawler takes in other components let's break them down:

### Storage

Storage is an interface that exposes method to save data.
This helps with extending the processor without changing it's code.

Whatever storage implementation we use we need to implement
the following methods:

```go
package storage

type Storage interface {
    Get(path string) (string, error)
    Set(path string, value string) error
    Delete(path string) error
}
```

### Parser

Instead of parsing the content in the crawler we can provide an implementation
for the filetypes we want to parse.
We can have a single parser that handles all the file types but
this way is much easier to extend.

But why do we need the parser?
After we fetch the page we need to parse it to get
the links from it and add it to our frontier.

```go
package parser

type Token struct {
    Name  string
    Value string
}

type Parser interface {
    IsSupportedExtension(extension string) bool
    Parse(content string) ([]Token, error)
}
```

Parser can check the file extension to see if it's supported,
And parse the file into tokens.

The token is parsed information from the content.
This is a nice way to extend the material we parse from the page later.
Currently we only care about `a` tags which are links.

### Processor

Following the same idea with parsers, we can provide the crawler
processes to apply on the web pages.

Some typical processes are:

- Saving the page
- Extracting links from the page

Let's define the interface based on the required actions.

```go
type Processor interface {
    Process(CrawlResult) error
}
```

The process function takes in the crawl result which we'll define later.
The function is only going to return an error.
Since a lot of operations can be done in this function we are not returning any value.

### Distribute and Collect Result from Workers

In the earlier section we discussed how can we parallelize the crawling
task by distrubting the urls into multiple queues and assign workers to each
queue.

Let's implement this functionality, We can create a new function called `Start`
for the crawler struct:

```go
func (c *Crawler) Start() {
    distributedInputs := make([]chan *url.URL, c.config.WorkerCount)
    workersResults := make([]chan CrawlResult, c.config.WorkerCount)
    done := make(chan struct{})

    for i := 0; i < c.config.WorkerCount; i++ {
        distributedInputs[i] = make(chan *url.URL)
        workersResults[i] = make(chan CrawlResult)
    }
    go distributeUrls(c.frontier, distributedInputs)
    for i := 0; i < c.config.WorkerCount; i++ {
        worker := NewWorker(distributedInputs[i], workersResults[i], done, i, c.deadLetter)
        go worker.Start()
    }

    mergedResults := make(chan CrawlResult)
    go mergeResults(workersResults, mergedResults)
```

Here we start by creating an input channel and an output channel for each worker.

There is a done channel here as well. It's a practice in go to use an empty
channel to notify the goroutines that the process is done or cancelled.

Then a function will start ditributing URLs from frontier to worker channels.

Finally we have a another function that merges results from worker outputs.

Note that these two functions and worker start are executed in a separate goroutine.
So they will continuously consume from frontier, add to worker input channel,
and put merge the result into a single output channel.

How can we implement the distribute and merge mechanisms?
[This post](https://go.dev/blog/pipelines) fully explains the fan-in and fan-out.

Let's create a separate file and implement these two functions.

```go
func distributeUrls(frontier *frontier.Frontier, distributedInputs []chan *url.URL) {
    HostToWorker := make(map[string]int)
    for url := range frontier.Get() {
        index := rand.Intn(len(distributedInputs))
        if prevIndex, ok := HostToWorker[url.Host]; ok {
            index = prevIndex
        } else {
            HostToWorker[url.Host] = index
        }
        distributedInputs[index] <- url
    }
}
```

Here we have a for loop over a channel.
This means that our function never exits until the frontier closes the channel.
For each url coming into the channel we take it and assign it to a worker input channel.

The assignment algorithm is very simple, we have a list of already assigned hosts.
If a host is new we assign it randomly, otherwise we send it to the assigned host.

Now let's implement the merger:

```go
func mergeResults(workersResults []chan CrawlResult, out chan CrawlResult) {
    collect := func(in chan CrawlResult) {
        for result := range in {
            out <- result
        }
        log.Println("Worker finished")
    }

    for i, result := range workersResults {
        log.Printf("Start collecting results from worker %d", i)
        go collect(result)
    }
}
```

This function might be a bit more complex.
First we created a function named collect that consumes from a single channel.
Then we loop over the workers and call this function on all the output channels.

So this starts a goroutine per worker that listens to output channel.
The result is put into the merged output channel.

Pretty simple yet powerful technique to parallelize a task.

### Worker

To implement the worker we first need to define the struct and crawl result.

```go
type CrawlResult struct {
    Url         *url.URL
    ContentType string
    Body        []byte
}

type Worker struct {
    input      chan *url.URL
    deadLetter chan *url.URL
    result     chan CrawlResult
    done       chan struct{}
    id         int
    logger     *log.Entry

    // Only contains the host part of the URL
    history map[string]time.Time
}
```

The crawl result represents a successsful page load with content and the type.

Let's breakdown what worker has:

- input: the channel that worker consumes from
- deadLetter: another channel that worker puts in the failed URLs into
- result: channel for sending successful crawls
- done: the channel that notifies the worker if it has to stop
- id: an id assigned to the worker this is useful for marking logs from each worker
- logger: a logger with worker context so log messages are distinguishable from others.
  `logger := log.WithField("worker", id)`

The Start method of the worker is a for-select statement to consume
any message that comes into the input channel, fetch and pass the result.

Before fetching the URL we check for politeness and sleep if needed.
There is a downside to this if we have consecutive URLs from one host.
Since we have to sleep and it slows down.

There are two improvements here I can think of:

1. Discarding that URL to deadletter and continue until we get another host
2. Distribute the URLs in worker input channel to reduce the chance of blocking

But here we just go with the simple approach

```go
func (w *Worker) Start() {
    w.logger.Debugf("Worker %d started", w.id)
    for {
        select {
        case url := <-w.input:
            for !w.CheckPoliteness(url) {
                time.Sleep(2 * time.Second)
            }
            content, err := w.fetch(url)
            if err != nil {
                log.Errorf("Worker %d error fetching content: %s", w.id, err)
                w.deadLetter <- url
                continue
            }
            w.history[url.Host] = time.Now()
            b. result <- content
        case <-w.done:
            return
        }
    }
}
```

The fetch function does a simple fetch and also determines the content type.

```go
func (w *Worker) fetch(url *url.URL) (CrawlResult, error) {
    w.logger.Debugf("Worker %d fetching %s", w.id, url)
    defer w.logger.Debugf("Worker %d done fetching %s", w.id, url)
    res, err := http.Get(url.String())
    if err != nil {
        return CrawlResult{}, err
    }
    defer res.Body.Close()

    if res.StatusCode != http.StatusOK {
        return CrawlResult{}, fmt.Errorf("status code error: %d %s", res.StatusCode, res.Status)
    }
    body, err := io.ReadAll(res.Body)
    if err != nil {
        return CrawlResult{}, err
    }

    var inferredContentType string
    contentType, ok := res.Header["Content-Type"]
    if ok && len(contentType) > 0 {
        inferredContentType = contentType[0]
    } else {
        inferredContentType = http.DetectContentType(body)
    }

    return CrawlResult{
        Url:         url,
        ContentType: inferredContentType,
        Body:        body,
    }, nil
}

func (w *Worker) CheckPoliteness(url *url.URL) bool {
    if lastFetch, ok := w.history[url.Host]; ok {
        return time.Since(lastFetch) > 2*time.Second
    }
    return true
}
```

### Extracting Links

To extract a link we implement the Processor interface we defined above.

This processor takes in parsers and crawl result then outputs links.

```go
type LinkExtractor struct {
    Parsers []parser.Parser
    NewUrls chan *url.URL
}

func (e *LinkExtractor) Process(result CrawlResult) error {
    foundUrls := make([]*url.URL, 0)
    for _, parser := range e.Parsers {
        if !parser.IsSupportedExtension(result.ContentType) {
            continue
        }
        parsedUrls, err := parser.Parse(string(result.Body))
        if err != nil {
            return fmt.Errorf("Error parsing content: %s", err)
        }
        log.Infof("Extracted %d urls", len(parsedUrls))
        for _, parsedUrl := range parsedUrls {
            newUrl, err := url.Parse(parsedUrl.Value)
            if err != nil {
                log.Debugf("Error parsing url: %s", err)
                continue
            }
            params := newUrl.Query()
            for param := range params {
                newUrl = stripQueryParam(newUrl, param)
            }
            if newUrl.Scheme == "http" || newUrl.Scheme == "https" {
                foundUrls = append(foundUrls, newUrl)
            }
        }
    }
    for _, foundUrl := range foundUrls {
        e.NewUrls <- foundUrl
    }
    return nil
}

func stripQueryParam(inputURL *url.URL, stripKey string) *url.URL {
    query := inputURL.Query()
    query.Del(stripKey)
    inputURL.RawQuery = query.Encode()
    return inputURL
}
```

The this struct keeps a list of parsers and has a channel to output links.

The process function takes in a crawl result and matches the type with it's parsers.
It's also important to make sure we strip the query params,
strings like `?sort=foo`.
There might be case that we care about them, but here to simply remove duplicates
we do this.

A better approach here is to use the `rel=canonical` HTML attribute to identify if
URL is identical to current page.

The result from this extractor are put in a new channel.

So in the crawler we can add this processor and get the URLs:

```go
    c.AddProcessor(&LinkExtractor{Parsers: c.contentParsers, NewUrls: newUrls})
    go func() {
        for newUrl := range newUrls {
            _ = c.frontier.Add(newUrl)
        }
    }()
```

### Saving Content

To save the content we use another processor.
This processor uses the storage backend provided to the crawler to store pages.

```go
type SaveToFile struct {
    storageBackend storage.Storage
}

func (s *SaveToFile) Process(result CrawlResult) error {
    savePath := getSavePath(result.Url)

    switch result.ContentType {
    default:
        savePath = savePath + ".html"
        err := s.storageBackend.Set(savePath, string(result.Body))
        if err != nil {
            return err
        }
    }

    return nil
}

func getSavePath(url *url.URL) string {
    fileName := url.Path + "-page"
    savePath := path.Join(url.Host, fileName)
    return savePath
}
```

And again we add it easily to the crawler:

```go
    c.AddProcessor(&SaveToFile{storageBackend: c.storage})
```

### Running Processors

The final step in our start method is to run processors on results.

Since the list of processors can be extended and we must not block the
goroutine, we execute each of them in a separate goroutine.

This is important because if we can't consume from the merged results fast enough
then each worker might wait until the processors are ran so they can send to channel.
Remember the send to channel blocks until the consumer is ready.

```go
    for result := range mergedResults {
        for _, processor := range c.processors {
            go func(processor Processor, result CrawlResult) {
                processErr := processor.Process(result)
                if processErr != nil {
                    log.Error(processErr)
                }
            }(processor, result)
        }
    }
```

### Failed URLs

This part is open ended and you can try it as an exercise.
We only consume the failed ones and log them to the console.

```go
    go func() {
        for deadUrl := range c.deadLetter {
            log.Debugf("Dismissed %s", deadUrl)
        }
    }()
```

### HTML parser

We need to implement at least 1 parser so our crawler can
parse HTML pages.

```go
package parser

import (
    "errors"
    "fmt"
    "io"
    "strings"

    "golang.org/x/net/html"
)

type HtmlParser struct {
}

func (p *HtmlParser) getSupportedExtensions() []string {
    return []string{".html", ".htm"}
}

func (p *HtmlParser) IsSupportedExtension(extension string) bool {
    for _, supportedExtension := range p.getSupportedExtensions() {
        if extension == supportedExtension {
            return true
        }
    }
    return true
}

func (p *HtmlParser) Parse(content string) ([]Token, error) {
    htmlParser := html.NewTokenizer(strings.NewReader(content))
    tokens := []Token{}
    for {
        tokenType := htmlParser.Next()
        if tokenType == html.ErrorToken {
            break
        }
        token := htmlParser.Token()
        if tokenType == html.StartTagToken {
            switch token.Data {
            case "a":
                for _, attr := range token.Attr {
                    if attr.Key == "href" {
                        tokens = append(tokens, Token{Name: "link", Value: attr.Val})
                    }
                }
            }
        }
    }

    if htmlParser.Err() != nil {
        if !errors.Is(htmlParser.Err(), io.EOF) {
            return tokens, fmt.Errorf("error scanning html: %s", htmlParser.Err())
        }
    }
    return tokens, nil
}
```

The parsing process is straight forward, we use a parser package and
walk over the elements and extract the ones with `a` tag and `href` attribute.

### Putting it All Together

We finally have everything needed to crawl some pages.

The parser we created is not a program, it's a library.
This can be imported and be started within another program.

You can create a CLI using this or use a main function.
We'll create a main function to test it out:

```go
func main() {
    log.SetFormatter(&log.TextFormatter{FullTimestamp: true})
    initialUrls := []url.URL{}

    myUrl, _ := url.Parse("https://glyphack.com")
    initialUrls = append(initialUrls, *myUrl)

    contentStorage, err := storage.NewFileStorage("./data")
    if err != nil {
        panic(err)
    }

    contentParsers := []parser.Parser{}
    contentParsers = append(contentParsers, &JsonParser{})

    crawler := crawler.NewCrawler(initialUrls, contentStorage, &crawler.Config{
        MaxRedirects:    5,
        RevisitDelay:    time.Hour * 2,
        WorkerCount:     100,
        ExcludePatterns: []string{},
    })

    crawler.Start()
}
```

## Conclusion

Going through building this crawler and facing many deadlocks taught me a lot
about goalng.
And writing about this was a good practice to question my design and
the way I wrote the code.

I could not explain the problems I faced in this post because I wrote it
long after I finished the code itself. But you know enough to not make
those mistakes as I did.
