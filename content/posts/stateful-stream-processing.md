---
title: "Stateful Stream Processing"
date: 2022-08-15T08:53:57+04:30
draft: true
tags: [] 
---

A pattern that I have recently seen in a project is data replication through
real-time stream processing. This pattern happens when a company has all of
it's data stored on centralized databases and applications access this data,
this means that two example services like "search" and "product catalog" are
depending on the same data.
In this situation some services cannot function by only request the data
through API, they need a snapshot of the data.
Do address this requirement the real-time data replication solutions come
handy.
With this approach we need a event driven architecture to handle incoming data
and apply required transformations.
All stream processing frameworks such as Kafka Streams support doing stream
joins to denormalize the data and while they offer very straightforward
performant solutions the join support is limited in some cases.

## Streaming Changes from Database
We can start by implementing a change data capture system with a tool like
Debizium and Apache Kafka. An example architecture is the following picture:
![streaming-database-changes](/streaming-database-changes.excalidraw.png)

Now the downstream services can use the data product topic coming out of Kafka.
Let's focus on how to implement the stream processing component.

As discussed earlier this use case is very suitable for a tool like Kafka
Streams but if we have requirements to join data like:

- Join on primary and non primary keys
- Having no time window on when the join can occur
- Support denormalizing database relations

Then you cannot utilize full power of Kafka streams.
Because Kafka streams joins the data on record key then all records that are
going to be joined need to be published with the same key.
Now if a stream needs to be joined with multiple streams then it has to be
published in multiple topics with different keys.
This approach will result in the following diagram

![reparition-data-join](/repartion-data-to-join.excalidraw.png)

This can lead to a very expensive solution both in terms of cost and
development.

## Stating the Problem and Possible Solutions
Now that we know the pattern and the limit let's try to solve it with for an
example business.
Imagine you are doing this for Github, they want to extract all user data and
it's interactions with the platform into an easy to use data structure named
`UserProfile`

Let's start by giving a very simple example data model:
![github-example-data-model](/github-example-data-model.excalidraw.png)

With following definitions:

**User**
- id
- email
- username
- registered_at

Pk: email

**Repo**
- name
- owner
- description
- star_count
- fork_count
- created_at
- updated_at

Pk: (owner,name)

**Pull Request**
- repo
- repo_owner
- index
- author
- status
- created_at

Pk: (repo,repo_owner,index)

**Star**
- username
- repo_name
- repo_owner
- created_at

Pk: (username, repo_name, repo_owner)

**Payment Info**
- id
- verified

Now let's say the `UserProfile` is going to have the structure:

**User Profile**
- email
- username
- starred_repos (many to many rel)
    - repo 
    - description
- pull_requests (one to many rel)
    - repo
    - index
    - title
    - created_at
    - status
- payment_verified

In this case when we are consuming events form User, Pull Request and Star
table then we need to do join these streams and embed the pull request and
star information inside the `UserProfile` output stream.
If we start by using message keys as join keys here to join User and Pull
Request streams then the Pull Request has to be published with `author` field
as a key.
In case we need to create another data product for pull requests
data depends on the repo and index we need to create another stream.

Before that let's see what query join do we need to perform on these streams
to get the result.
```SQL
select ...
from users
left outer join star
    on star.username = username
left outer join pull_request
    on pull_request.author = username
left outer join payment_info
    on payment_info.id = id
```
Note that in this query we only want to get a single record with `UserProfile`
structure.
This means to embed all pull requests into record as a list, and add
payment_verified value as a single value.

## Solutions
To give a solution I'm focusing on providing something that can work at huge
scale, imagine we are going to create a hundred data products so system should
make it very easy to onboard a new table.

### Solution 1: Using RDBMS
I started with the idea of why not just moving all the computation on the database?
After all the SQL language has nice features to do these transformations.

![rdbms-solution](/running-transformations-on-db.excalidraw.png)

With this method we can have a generic application that reads streams and place
them in database under a table with the topic name.
So to onboard a new topic we have to feed this service two values:
- table name to insert data into
- table schema and mapping of event fields into table fields

After we insert the data in the database we
[trigger](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraMySQL.Integrating.Lambda.html) a lambda function to run the SQL query, get the data and embed the joins into a single document and produce message to Kafka.

This lambda function requires these inputs:
- a mapping from table names to SQL queries

After lambda is triggered it will lookup the mapping and run the SQL query. In our case it will get the user back with all matched pull request.
Now we need a custom logic in lambda to embed all the matched Pull Request
entities into `UserInfo` message.

### Benefits
- Implementation is very generic
- We have all the capabilities of SQL to do the processing
- Each topic can be joined with any other topic with any valid SQL condition

### Drawbacks
- The fact that we put all the computation on the database and specially join
    queries will result in a huge amount of costs
- The architecture is not truly real-time, we should utilize indexes on
    database to make sure query returns with low latency


