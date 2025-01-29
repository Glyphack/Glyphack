---
title: "Can Data Fool You?"
date: 2025-01-29T22:32:33+01:00
draft: false
tags: []
---

I was taking some time off the blogging and doing more programming lately.
But suddenly a shocking experience made me write this story.

Maybe before we go into the story I should give you a little bit of background.
If you haven't been living in a cave you know how hot being data driven is.

Now what does it mean to use data to make decisions?
If you cannot make a decision just run both under some experiment and decide based on the result.
If you have a problem with too many factors, and it's hard to decide and reason about every aspect of it this approach sounds more reasonable.
But here's why I think this misses a point.

Few days ago I was working on some piece of code.
After running it a few times turned out the calculations were wrong.
And I knew before me someone worked on this feature and released it. They even collected the data and showed that it was working positively.
So turns out, this piece of code was running in an A/B test for weeks. And after the analysis it seemed to be working good, so the code was left there and nobody looked at it again.

Running an A/B test to verify a calculation is correct, or a fix is working is one of the worst solutions.
The moment you see the charts go up you attribute that to the code you changed.
Would you possibly think with yourself that, the code might be wrong?
Could it be that the code is wrong, but the result is better due to some other thing that we don't know?

Imagine you want to sell a book but don't know what price would yield the most profit.
You can sell it more expensive and expect less sales while having more profit on each book or the other way around.
Now your data boss comes up with this neat idea.
Let's sell the book with two different prices in two markets and see how much profit do we make.
Now imagine maybe one market was Inevitably going to like the book less. You can imagine a million reasons that this might happen. You know how suddenly something can go viral.
This definitely affects the data.
Once you see this you try to explain your decision with the data.
Oh, maybe it's expensive and people didn't buy it.
Unless something is terribly wrong(10x books sold in one area) you don't suspect the result.
Also, how are you going to decide on how long should we continue it? When do you know you are done? It's all approximations.

While this was a hypothetical examples there are more [resources](https://www.goodreads.com/book/show/13530973-antifragile) on why you might misunderstand a phenomenon and come up with wrong answers and [how data can fool you](https://www.youtube.com/watch?v=QBe8lJdpvDU)

What is better than approximation? Logic.
Don't you remember how did you learn the multiplication table in school?
You didn't randomly say numbers and find which numbers are getting you a better grade. That's what LLMs do and that's why their numerical calculations suck.
You did trial and error for some time and then started to have some understanding and made decisions afterwards.

One thing I should be very careful with is to not fool myself with data. Having data about something is good. But why not combine it with some logic?
Correctness of a code is determinable by running it and checking the result.
But if you say we write the code and let the data decide if it was better or not, you end up in a mess.
Everything might be wrong, it might have performed better in the charts.
But it's wrong, at that point either you are wrong, or you messed something up, and you are in the mercy of the world that boosted your results with something you don't know about.

It's easy to see something happening and thinking you exactly know why.
But if the same thing stopped happening you couldn't make it happen.
If you exactly knew why you could have made it happen again.
When you can't, it means that you didn't really in the first time.
If you ever did an A/B test and found out why something is better try to use that idea again. It should be consistent, if it's not then something's wrong.
