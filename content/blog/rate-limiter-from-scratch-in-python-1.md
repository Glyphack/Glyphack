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

    def to_seconds(self) -> int:
        if self == Unit.SECOND:
            return 1
        elif self == Unit.MINUTE:
            return 60
        elif self == Unit.HOUR:
            return 3600
        else:
            raise ValueError(f"Unknown unit: {self}")


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
        self.capacity = self.rule_descriptor.requests_per_unit
        self.refill_every_x_seconds = unit.to_seconds()

```

How does token bucket works?

[Wikipedia definition](https://en.wikipedia.org/wiki/Token_bucket) is pretty straightforward:

> - A token is added to the bucket every R seconds.
> - The bucket can hold at the most B tokens. If a token arrives when the bucket is full, it is discarded.

To translate it into code, for each request we create a key, this key consists of the request path and it's value for the specified key.
When a request comes in:

- We allow it if it's not in the storage which means it's the first time.
- If key exists we try to consume one token from it and if it fails we deny

When do we do the refill?
This part is handled by setting the ttl, after the ttl the bucket is gone and we recreate it and fill it with `capacity`.

```python
def do_limit(self, request: Request):
 self.request = request
 counter_key = self._get_counter_key()
 if counter_key is None:
  return False
 if self._consume(counter_key):
  return False

 return True

def _get_counter_key(self):
 descriptor = self.rule_descriptor
 path = self.request.path
 key = descriptor.key
 value = self.request.data[key]
 if descriptor.value is not None and value != descriptor.value:
  return None
 else:
  return path + "_" + key + "_" + value

def _consume(self, counter_key):
 counter = self.storage_backend.get(counter_key)
 if counter is None:
  counter = self.capacity
 elif counter <= 0:
  return False

 counter -= 1
 self.storage_backend.set(counter_key, counter, self.refill_every_x_seconds)

 return True

```

### Implementing Local Cache

With local cache we need to keep track of the data and ttl(time to live) values.

```python
from datetime import datetime, timedelta
from typing import Dict

from hera_limit.storage.storage import AbstractStorage


class Memory(AbstractStorage):
    def __init__(self):
        self.data = {}
        self.ttl: Dict[str, datetime] = {}
```

The set operation takes in a a string key and a string value. We don't need to support more complex data structures(sets, maps) with this function as it's not needed.

```python
def set(self, key: str, value: str, ttl_seconds: int):
 self.data[key] = value
 self.ttl[key] = datetime.now() + timedelta(seconds=ttl_seconds)
```

We add the key to both `data` and `ttl` to be able to determine if a key is expired or not.
Now when getting a key we need to check the `ttl` has not passed yet.

```python
def get(self, key):
 if key in self.ttl:
  if self.ttl[key] < datetime.now():
   del self.ttl[key]
   del self.data[key]
   return None
 return self.data.get(key)
```

{{< callout emoji="💯" text="An improvement idea is to create a process to remove keys with passed `ttl`. Currently if we add many keys but don't retrieve them for a long time it can take space." >}}

### Rate Limiter Service

The service is just the orchestrator of our components. we haven't defined an interface for it now because nothing depends on it.

When the service is started it takes in the rules and since each rule might have multiple descriptors we need to make sure to check all of those if a request path matches it.

The `Config` class holds data such as which limiting strategy to use.

```python
@dataclass
class Config:
    limit_strategy: LimitStrategies


class RateLimitService:
    def __init__(
        self, config: Config, storage_engine: AbstractStorage, rules: List[Rule]
    ) -> None:
        self.rule_to_limits: Dict[Rule, List[AbstractStrategy]] = {}
        self.storage_engine = storage_engine

        for rule in rules:
            self.rule_to_limits[rule] = []
            for descriptor in rule.descriptors:
                if config.limit_strategy == LimitStrategies.TOKEN_BUCKET:
                    self.rule_to_limits[rule].append(
                        TokenBucket(
                            storage_backend=self.storage_engine,
                            rule_descriptor=descriptor,
                        )
                    )
                else:
                    raise NotImplementedError
```

The limit function is going to find which rules apply for each request and apply all of its descriptors.

```python
def do_limit(self, request):
 applied_rules = []
 for rule, limits in self.rule_to_limits.items():
  if rule.match(request.path):
   applied_rules.append(limits)
 for rule_limits in applied_rules:
  if rule_limits.do_limit(request):
   return True
 return False
```

### Testing

We did a lot of work before writing tests and it's so unfortunate. I though having tests after setting up the interfaces would be better for this post. But never do this in real life!

We're going to use `pytest` to write tests and we can define the storage as a fixture to inject it in the test cases:

```python
@pytest.fixture
def local_storage():
    yield memory.Memory()
```

Also in order to test that the algorithm respects the time period of a limit,
we need to mock the `datetime.now()` in our tests.
Install `freezegun` to do this.

```bash
pip install freezegun
```

#### Test Token Bucket Algorithm

There are three cases we can test for the implementation:

- When a bucket gets empty it should allow the request anymore
- Algorithm respects key values, for example if user 1 requests too much only user 1 is limited.
- If a value for a key is provided then we only limit requests with that value.

An important question that pops up is that how can we test the bucket refills? we need to wait for the `ttl` to pass. We're going to use python [mock](https://docs.python.org/3/library/unittest.mock.html) package and mock the time function that is available on the Memory to fast forward the time.

```python
def test_token_bucket_apply_limit_per_unit(local_storage):
    rule_descriptor = Descriptor(
        key="user_id",
        requests_per_unit=1,
        unit=Unit.SECOND,
    )
    token_bucket = TokenBucket(
        storage_backend=local_storage,
        rule_descriptor=rule_descriptor,
    )
    request = Request(path="dd", data={"user_id": "1"})
    assert token_bucket.do_limit(request) is False
    assert token_bucket.do_limit(request) is True

    time_now = datetime.datetime.now() + datetime.timedelta(seconds=3)
    with freezegun.freeze_time(time_now):
        assert token_bucket.do_limit(request) is False


def test_token_bucket_apply_limit_for_values(local_storage):
    rule_descriptor = Descriptor(
        key="user_id",
        requests_per_unit=1,
        unit=Unit.SECOND,
    )
    token_bucket = TokenBucket(
        storage_backend=local_storage,
        rule_descriptor=rule_descriptor,
    )
    user_1_request = Request(path="dd", data={"user_id": "1"})
    user_2_request = Request(path="dd", data={"user_id": "2"})

    assert token_bucket.do_limit(user_1_request) is False
    assert token_bucket.do_limit(user_2_request) is False
    assert token_bucket.do_limit(user_1_request) is True
    assert token_bucket.do_limit(user_2_request) is True


def test_token_bucket_apply_limit_specific_values(local_storage):
    rule_descriptor = Descriptor(
        key="user_id",
        value="1",
        requests_per_unit=1,
        unit=Unit.MINUTE,
    )
    token_bucket = TokenBucket(
        storage_backend=local_storage,
        rule_descriptor=rule_descriptor,
    )
    user_1_req = Request(path="dd", data={"user_id": "1"})
    user_2_req = Request(path="dd", data={"user_id": "2"})

    assert token_bucket.do_limit(user_1_req) is False

 assert token_bucket.do_limit(user_2_req) is False
    assert token_bucket.do_limit(user_1_req) is True
```

#### Test Rate Limiter Service

For rate limiter service we need to create two fixtures, config and local storage:

```python
@pytest.fixture
def local_storage():
    yield memory.Memory()


@pytest.fixture
def config():
    return Config(
        limit_strategy=LimitStrategies.TOKEN_BUCKET,
    )
```

Now what can be tested in the service?
With the limit strategy we were testing if the rule descriptor is applied correctly.

Here we should check if the rule is applied correctly,
this means we can still test the rule descriptor part,
but it's not necessary since if a rule descriptor is not applied correctly
then the limit strategy test must throw an error(otherwise we end up with an
untested strategy which is a nightmare).

```python

def test_rate_limit_service_applies_the_rule(local_storage: memory.Memory, config: Config):
    rule_descriptor = Descriptor(
        key="user_id",
        requests_per_unit=1,
        unit=Unit.SECOND,
    )
    rule = Rule(path="/limited-path", descriptors=[rule_descriptor])
    rate_limit_service = RateLimitService(
        config=config, storage_engine=local_storage, rules=[rule]
    )
    request = Request(path="/limited-path", data={"user_id": "1"})
    assert rate_limit_service.do_limit(request) is False
    assert rate_limit_service.do_limit(request) is True

    time_now = datetime.datetime.now() + datetime.timedelta(seconds=3)
    with freezegun.freeze_time(time_now):
        assert rate_limit_service.do_limit(request) is False
```

## Conclusion

So far we have a working rate limiter with one implemented rule.
I think this would be enough for one read,
In the next post we will add more rate limiting algorithms and see
how the current structure of the program can be extended.

You can find the [full source code](https://github.com/Glyphack/hera-limit) on my Github.
