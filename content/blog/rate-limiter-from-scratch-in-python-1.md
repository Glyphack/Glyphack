---
title: "Rate Limiter From Scratch in Python Part 1"
date: 2023-02-14T23:19:18+01:00
draft: false
tags: [coding]
---

## Introduction

After reading [ByteByteGo course](https://bytebytego.com/) motivated me to write a rate limiter. So I decided to do it in [500lines](https://aosabook.org/en/500L/introduction.html) theme.
We are going to focus on how to create the interfaces and components, to allow extensibility in the predicted ways.

You can find the full source code [here](https://github.com/Glyphack/hera-limit).

## What is a Rate Limiter?

Well there are a lot of [great explanations](https://www.cloudflare.com/en-gb/learning/bots/what-is-rate-limiting/) on what is a rate limier but I'll give a very small introduction to it for this post.

Rate limiter is a software that limits how many times someone can repeat an action in your software. Take twitter as an example, they need to limit how many times someone can send a tweet per minute otherwise 1 person can create 1 million tweets in a second and fill up all of their server resources.

## High Level Design

First off what should our rate limiter do? Rate limiter should be a function that takes in a request, decides if the request can go through or not based on the current statistics.

We are going to implement the following features:

1. Rule based rate limiting: let user define rules with a simpler version(without nested rules) of [envoy rate limit config](https://github.com/envoyproxy/ratelimit#configuration).
2. Support both local memory and Redis as storage backend
3. Support the following rate-limit algorithms:
4. Token bucket
5. Fixed window
6. Sliding window log
7. Sliding window counter
8. Distributed deployment model: deploying multiple instances with both consistent and eventual consistent models.

What are the components in our system?

![System Components](/rate-limiter-components.png)

Breaking down the components:

Rules storage
it is responsible for loading rules and providing them to rate limiter. Separating this component allows the service to not depend on how the rules should be loaded into the service. We want to start the application with a set of rules saved on disk, but it's useful to be able to add/remove rules from an API endpoint while the application is running.
Although we are not going to implement that part in this guide. It's good to separate this for easier testing and future extensibility.

Storage

This component is responsible for holding data used by rate limiting algorithms. Creating an interface for storage is useful because we can ignore the underlying storage implementation in rate limit algorithms. This allows us to easily use multiple storage backends such as Redis or local memory without having to touch the rate limit algorithm code.
For the above algorithms we can implement operations `exists`, `get_value`, `set`, `incr`.

Note that we have this assumption that our datastore for this software is a key/value store, we are not creating a generic store that can be used for other use cases. This helps with writing a simpler interface and implementation for storage. For example we don't require to support a where/filtering clause.

[This video](https://www.youtube.com/watch?v=tKbV6BpH-C8)
gives a nice explanation on why sometimes we must do this.

{{< callout emoji="✅" text="In the above abstraction we are not creating a generic storage but only a key value store. This limits the extensibility of the code but makes the work easier. This is a good choice for rate limiter problem scope. Always be careful when creating a very generic abstraction." >}}

Limit Strategy: This component implements the rate limit algorithms without knowing about the underlying storage or API implementation. It should take in a storage and a request and provide a result whether it's limited or not.
The request details are important to decide whether to limit or not, but we only the request data, IP, and path. So it's better to only take in these values and not depend on a particular request type, then in the future we can write adapters to convert a gRPC request to this functions input format.

Service: takes care of orchestrating all the components.
Upon startup it loads all the rules into memory and creates a list of limit strategies to check.
Flow of handling requests:

1. Run all the rules that apply to the request path
2. rules provide an answer whether to allow or deny the request.

API: This layer is an interface for other programs to call the rate limiter, for example this part can be exposed to the API gateway. We are not going to implement the API but we implement the logic to rate limit requests. Separating the API and rate limit service is helpful as we can expose different interfaces to integrate with different tools, for example:

- Importing the rate limiter directly into the app
- Making it available as a [Kong plugin](https://docs.konghq.com/gateway/latest/plugin-development/)

The rule structure is part of application interface. Users can define them to rate limit the services, and just like an API we don't change them much. On the other hand the LimitStrategy and Storage can be swapped and replaced with different implementations. So a rule can stay the same while the limiter enforcing the rule can be changed to relax the rule or make it more strict.

## Implementation

### Defining Interfaces

Based on the above rule structure we can use the following structure:

```python
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class Unit(str, Enum):
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"


@dataclass
class Descriptor:
    key: str
    unit: Unit
    requests_per_unit: int
    value: Optional[str] = None


@dataclass
class Rule:
    path: str
    descriptors: List[Descriptor]

    def match(self, path: str) -> bool:
        return self.path == path
```

`dataclass` is used here for easier initialization.

Now let's define the storage interface

```python
from abc import ABC, abstractmethod
from enum import Enum


class StorageEngines(str, Enum):
    REDIS = "redis"
    MEMORY = "memory"


class AbstractStorage(ABC):
    @abstractmethod
    def get(self, key):
        raise NotImplementedError

    @abstractmethod
    def set(self, key, value, ttl_seconds: int):
        raise NotImplementedError

```

`get` and `set` are the required methods for implementing the above algorithms. other operations such as [decr](https://redis.io/commands/decr/) are also available which can increase the performance of our code.

Limit strategies only depend on the storage & rule components.
It should also have a request type for itself which can be used by other components calling it to pass in a request with a generic form. So it does not depend on a specific type of request, but only it's data and path.
The only public function is `do_limit` which takes in a request and determines if it's limited or not.

```python
class LimitStrategies(str, Enum):
    TOKEN_BUCKET = "token_bucket"


@dataclass
class Request:
    path: str
    data: dict


class AbstractStrategy(abc.ABC, metaclass=abc.ABCMeta):
    def __init__(
        self,
        storage_backend: AbstractStorage,
        rule_descriptor: Descriptor,
    ) -> None:

        self.storage_backend = storage_backend
        self.rule_descriptor = rule_descriptor

    @abc.abstractmethod
    def do_limit(
        self,
        request: Request,
    ):
        raise NotImplementedError
```

### Token Bucket

Now that the interfaces are clear we can start implementing the algorithm.

From the rule strucutre, we can use the `unit` to to refresh tokens in the bucket. and the `request_per_unit` to determine bucket capacity.

```python
class TokenBucket(AbstractStrategy):
    def __init__(
        self,
        storage_backend: AbstractStorage,
        rule_descriptor: Descriptor,
    ):
        super(TokenBucket, self).__init__(storage_backend, rule_descriptor)
        unit = self.rule_descriptor.unit
        if unit == Unit.SECOND:
            refill_period = 1
        elif unit == Unit.MINUTE:
            refill_period = 60
        elif unit == Unit.HOUR:
            refi
```
