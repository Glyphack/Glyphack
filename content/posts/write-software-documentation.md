---
title: "How Write and Organize Software Documentation"
date: 2022-01-23T17:30:40+03:30
draft: false
tags: ['software-documentation', 'documentation-writing', 'writing-documentation', 'document software']

---
Software documents play an important role in software development, everyone pays attention to writing documentation but just like writing code, writing the text is not enough but it has to be readable and understandable for other people, after all the purpose of documenting is to communicate. Recently I was reading documentation of a system and noticed that there's something  strange about it. although all the components are documented, but still it's not easy to find information on something.

Let's review the documentation role in these two situations, onboarding a new person with the system and improving collaboration between a team. This comes down to these two questions:
1. Can I hand over my technical docs to someone and expect them to have all information they need to make their first commit?
2. If situation X happens, do my teammates have to call someone to know what is happening?
So every day, when one of these happens, think about the answers and see how well your documentation is. For example, when you get similar questions from teammates about a system, think of it as a failure in the documentation system, not all questions can be answered inside docs, but the frequent ones must be answered.

## Avoid Common Problems of Technical Software Documentation
So what are the problems that can be in your technical notes?
### Non existent documents
#### No Entry Point Link Around a Topic
There is no primary documentation around a topic; you have to pass multiple links when someone is on boarded or read a single document after cloning the repo.
#### Cover all information needed for a project
If someone joins your team, they need information on how a system works. They also have to know how to set up their local and sandbox environment and use it.

### Hidden Documents
####  Nesting Overuse
Having sub-pages inside sub-pages makes the text to be scattered in different documents. Suppose someone reads a note on compiling a project. They also have to find the testing guide and deployment guide next to that text. It can be another section within that doc or a document next to it. Just make sure you don't need to browse again to find those.
This pattern is similar to coupling the code that is related to each other like putting it inside a single module.
#### Multiple channels
Some materials might be found on the slack channel, others on your documentation tool.

### Inaccurate Documents
If the documents are not updated along with the code, they become inaccurate as you change the software.

### Obsolete Documents
If a design is changed and older design decisions don't apply anymore, archive them.

### Afterthought Documents
This is a problem because if you write your docs after delivering a project, you will end up:
1. Forgetting to include important notes on the topic because you are in the [curse of knowledge](https://en.wikipedia.org/wiki/Curse_of_knowledge).
2. Explain the project to someone personally if you need to hand it over in the middle.

## How to Make Technical Documentations Better
It's essential to organize documents so that it's visible to everyone.

**Be Careful with Nesting**
When newcomers open the documentation, they should locate all the required information they need to work on the project. This means in your top-level page you should have all the topics you want to explain visible there as links or sub-pages.
As an example of a good technical documentation checkout [CockroachDB documents](https://wiki.crdb.io/wiki/spaces/CRDB/overview), There are all the things from introduction to deploying the project listed on the first page with only 1 level nesting.

**Make it like a story**
It should make sense to read and continue to the next topics. Make sure the topics are in the right order. Keep similar topics in different contexts separate, e.g. keep end-user documents separate from system specification documents but link them because the developer needs to know about the user when writing docs.
This means all the journey from finding the repo to clone to deploying a feature can be found inside technical docs.

**Make Documentation Writing an Ongoing process**
It's hard to keep documents that no one reads updated, make sure your documents have users by sending people document links instead of answering questions in Slack.

**Writing Software Documentation is a Collaborative Process**
Write documents with the mindset of other people are going to use them. so you should considering:
- Ask your team to review the docs you write
- Put new pages you create on draft

## Other resources

- [Documenting code repositories](https://microsoft.github.io/code-with-engineering-playbook/documentation/guidance/project-and-repositories/)

- [Type of documentations](https://blog.prototypr.io/software-documentation-types-and-best-practices-1726ca595c7f)
