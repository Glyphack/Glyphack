---
title: "Rate Limiter From Scratch in Python Part 2"
date: 2023-02-21T21:34:49+01:00
draft: false
tags: [coding]
---

<!--toc:start-->

- [Introduction](#introduction)
- [New Rate Limiting Algorithms](#new-rate-limiting-algorithms)
  - [Fixed Window](#fixed-window)
    - [Test](#test)
  - [Sliding Window Log](#sliding-window-log)
    - [Testing](#testing)
  - [Sliding Window Count](#sliding-window-count)
    - [Tests](#tests)
- [Conclusion](#conclusion)
<!--toc:end-->

## Introduction

In the last [post](./rate-limiter-from-scratch-in-python-1)
I started writing a rate limiter.
The project right now supports only 1 rate limiting algorithm(Token Bucket).

In this part we're going to implement the following algorithms:

- Fixed window
- Sliding window log
- Sliding window count

We'll see how each algorithm compares to another, and the trade offs.
Also after implementing each one we'll see how to abstractions we created
previously helped minimizing the implementation for new algorithms.

At the end of this post we'll add Redis as storage backend to our application.

## New Rate Limiting Algorithms

Before implementing the algorithm we can start by adding them to our rate limiter
service.

First we need to update the LimiterStrategy enum:

```python
class LimitStrategies(str, Enum):
    TOKEN_BUCKET = "token_bucket"
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW_LOG = "sliding_window_log"
    SLIDING_WINDOW_COUNTER = "sliding_window_counter"
```

The code that initialized the limiter strategy objects is in rate limiter service.
You can use a empty class(with no implementation) and implement it as we go
through them one by one.

```python
            for descriptor in rule.descriptors:
                if config.limit_strategy == LimitStrategies.TOKEN_BUCKET:
                    limits.append(
                        TokenBucket(
                            storage_backend=self.storage_engine,
                            rule_descriptor=descriptor,
                        )
                    )
                elif config.limit_strategy == LimitStrategies.FIXED_WINDOW:
                    limits.append(
                        TokenBucket(
                            storage_backend=self.storage_engine,
                            rule_descriptor=descriptor,
                        )
                    )
                elif config.limit_strategy == LimitStrategies.SLIDING_WINDOW_LOG: limits.append(
                        TokenBucket(
                            storage_backend=self.storage_engine,
                            rule_descriptor=descriptor,
                        )
                    )
                elif config.limit_strategy == LimitStrategies.SLIDING_WINDOW_COUNTER:
                    limits.append(
                        TokenBucket(
                            storage_backend=self.storage_engine,
                            rule_descriptor=descriptor,
                        )
                    )
                else:
                    raise ValueError(
                        f"Limit strategy {config.limit_strategy} not supported"
                    )

```

### Fixed Window

In the fixed window algorithm, we split the time into unit-size buckets.
Each bucket has a specified capacity and can limit the requests once it's reached.

For example, if our unit is 1 minute, our buckets would be 10:00, 10:01, and 10:02.

Now how can we choose the hash key?
A hash key like `path_1000_<key>_<value>` is good because
it puts all requests from a specific entity to a path into the correct bucket.
So we can query this key and check the count to determine the request.

But choosing the hour & minute combination to add time to the key is not going to work,
because there might be collisions when the day passes and we reach that time again.

To overcome this problem, we can use [timestmap](https://www.unixtimestamp.com/),
since each time second has a unique timestamp, we resolve the collision.

Since the timestamp represents the seconds,
we can't create a bucket for minute intervals if we use this value directly in the cache.
When the limiting unit is a minute, we need to find the value which
is the same for every moment in a given minute.

We can do this by dividing the timestamp by our unit:

```python
current_interval = str(int(datetime.now().timestamp() / self.interval_len_sec))
```

this value will be the same for all moments in the interval.

We can see that based on how this interval is calculated,
our limiter limits the requests for the window 10:00:00 and 10:01:00.
But it does not check the window 10:00:30 and 10:01:30.
This is the problem that sliding window algorithm solves,
by not making the window fixed.

Now that we figured out the hard part let's look at the code:

```python
class FixedWindow(AbstractStrategy):
    def __init__(
        self,
        storage_backend: AbstractStorage,
        rule_descriptor: Descriptor,
    ):
        super(FixedWindow, self).__init__(storage_backend, rule_descriptor)
        self.interval_len_sec = self.rule_descriptor.unit.to_seconds()
        self.interval_max = self.rule_descriptor.requests_per_unit

    def do_limit(self, request: Request):
        self.request = request
        counter_key = self._get_counter_key()
        if counter_key is None:
            return False
        if self._window_max_reached(counter_key):
            return True

        return False

    def _get_counter_key(self):
        current_interval = str(int(datetime.now().timestamp() / self.interval_len_sec))
        descriptor = self.rule_descriptor
        path = self.request.path
        key = descriptor.key
        value = self.request.data[key]
        if descriptor.value is not None and value != descriptor.value:
            return None
        else:
            return path + current_interval + "_" + key + "_" + value

    def _window_max_reached(self, counter_key):
        counter = self.storage_backend.get(counter_key)
        if counter is None:
            self.storage_backend.set(counter_key, 1, self.interval_len_sec)
            return False
        elif counter >= self.interval_max:
            return True

        counter += 1
        self.storage_backend.incr(counter_key)

        return False
```

Notice that here we are using the `incr` method from the storage.
We haven't implemented this functionality yet, but this is a good interface to add.

Since other storages such as redis has support for increment it's better to use it,
rather than get, increment and set the value approach.

So we add new method to `AbstractStorage`:

```python
@abstractmethod
def incr(self, key):
    raise NotImplementedError
```

And implement it in the memory:

```python
  def incr(self, key: str):
      if key in self.data:
          self.data[key] += 1
      else:
          self.data[key] = 1
```

#### Test

Testing this new strategy is so easy,
since all of our strategies have the same interface(input/output) we can
use pytest to [parameterize](https://docs.pytest.org/en/6.2.x/parametrize.html)
the strategy that is being tested.

Let's go back to the test we wrote for token bucket and rewrite it in this way:

```python
@pytest.mark.parametrize(
    "limit_strategy",
    [
        TokenBucket,
        FixedWindow,
    ],
I)
def test_apply_limit_per_unit(local_storage, limit_strategy):
    rule_descriptor = Descriptor(
        key="user_id",
        requests_per_unit=1,
        unit=Unit.SECOND,
    )
    token_bucket = limit_strategy(
        storage_backend=local_storage,
        rule_descriptor=rule_descriptor,
    )
    request = Request(path="dd", data={"user_id": "1"})
    assert token_bucket.do_limit(request) is False
    assert token_bucket.do_limit(request) is True

    test_now = datetime.datetime.now() + datetime.timedelta(seconds=3)
    with freezegun.freeze_time(test_now):
        assert token_bucket.do_limit(request) is False
```

the testing strategy is now passed to this test and it only tests the behavior.

Now we can rewrite the remaining tests as well:

```python
@pytest.mark.parametrize(
    "limit_strategy",
    [
        TokenBucket,
        FixedWindow,
    ],
I)
def test_apply_limit_per_value(local_storage, limit_strategy):
    rule_descriptor = Descriptor(
        key="user_id",
        requests_per_unit=1,
        unit=Unit.SECOND,
    )
    token_bucket = limit_strategy(
        storage_backend=local_storage,
        rule_descriptor=rule_descriptor,
    )
    user_1_request = Request(path="dd", data={"user_id": "1"})
    user_2_request = Request(path="dd", data={"user_id": "2"})

    assert token_bucket.do_limit(user_1_request) is False
    assert token_bucket.do_limit(user_2_request) is False
    assert token_bucket.do_limit(user_1_request) is True
    assert token_bucket.do_limit(user_2_request) is True


@pytest.mark.parametrize(
    "limit_strategy",
    [
        TokenBucket,
        FixedWindow,
    ],
I)
def test_apply_limit_specific_value(local_storage, limit_strategy):
    rule_descriptor = Descriptor(
        key="user_id",
        value="1",
        requests_per_unit=1,
        unit=Unit.MINUTE,
    )
    token_bucket = limit_strategy(
        storage_backend=local_storage,
        rule_descriptor=rule_descriptor,
    )
    user_1_req = Request(path="dd", data={"user_id": "1"})
    user_2_req = Request(path="dd", data={"user_id": "2"})

    assert token_bucket.do_limit(user_1_req) is False
    assert token_bucket.do_limit(user_2_req) is False
    assert token_bucket.do_limit(user_1_req) is True
```

### Sliding Window Log

As discussed earlier, the sliding window log does not take the time window fixed.
Imagine a request comes in at 10:00:30, instead of looking at request count in
the window 10:00 to 10:01
we check the number of requests in the window of 09:59:30 till that request.

So the steps are:

1. When a new request comes in save the timestamp into a list
2. Count all the requests within the time unit of the arrived request
3. If count more than allowed requests limit the request

How this can be done?

We need to save the timestamp when each requests comes in.
Then when the next request comes we need to query all requests in the previous minute.

Now the question is what data structure should be used here.
We need a data structure which can search and return all the values within a range.

Redis provides [sorted sets](https://redis.io/docs/data-types/sorted-sets/)
which can provide an efficient way for finding a range of values in a list.

Although sorted sets are
[implemented](https://github.com/redis/redis/blob/unstable/src/t_zset.c)
with hash map and [skip list](https://brilliant.org/wiki/skip-lists),
we are going to use a naive approach for implementing them in local memory storage.
This can be a good topic for another post.

Let's start implementing the algorithm.

```python
class SlidingWindowLog(AbstractStrategy):
    def __init__(
        self,
        storage_backend: AbstractStorage,
        rule_descriptor: Descriptor,
    ):
        super(SlidingWindowLog, self).__init__(storage_backend, rule_descriptor)
        self.interval_len_sec = self.rule_descriptor.unit.to_seconds()
        self.interval_max = self.rule_descriptor.requests_per_unit

    def do_limit(self, request: Request):
        self.request = request
        request_logs_key = self._get_request_logs_key()
        if request_logs_key is None:
            return False
        if self._window_max_reached(request_logs_key):
            return True

        return False

    def _get_request_logs_key(self):
        descriptor = self.rule_descriptor
        path = self.request.path
        key = descriptor.key
        value = self.request.data[key]
        if descriptor.value is not None and value != descriptor.value:
            return None
        else:
            return path + "_" + key + "_" + value
```

First we get key of the list holding request logs.
Then we check if current windows max request count is reached or not.

```python
def _window_max_reached(self, window_key):
    self.storage_backend.sorted_set_remove(
        window_key,
        0,
        datetime.now().timestamp() - self.interval_len_sec,
    )
    current_window_req_count = self.storage_backend.sorted_set_count(
        window_key,
        datetime.now().timestamp() - self.interval_len_sec,
        datetime.now().timestamp(),
    )
    if current_window_req_count is None:
        self.storage_backend.sorted_set_add(window_key, datetime.now().timestamp())
        return False
    elif current_window_req_count >= self.interval_max:
        return True

    self.storage_backend.sorted_set_add(window_key, datetime.now().timestamp())

    return False
```

Before checking the request count,
we need to remove all the request that are not in the current window.

Then we count the requests within the time unit and check if
it's more than the allowed count for the interval.

#### Testing

Same as how we tested the previous strategy we
can add this new strategy to test parameters:

```python
@pytest.mark.parametrize(
    "limit_strategy",
    [
        TokenBucket,
        FixedWindow,
        SlidingWindowLog,
    ],
)
```

we can add this strategy to previous tests,
but there's also a new behavior we can test for this strategy.
Since the sliding window algorithm does not allow over-limit requests
at the edge of the time unit (like between 01:50 and 02:10) we can add test it.

So create a new test:

```python
@pytest.mark.parametrize(
    "limit_strategy",
    [
        SlidingWindowLog,
    ],
)
def test_sliding_window_does_not_allow_requests_in_unit_edges(
    local_storage, limit_strategy
):
    rule_descriptor = Descriptor(
        key="user_id",
        requests_per_unit=2,
        unit=Unit.MINUTE,
    )
    sliding_window = limit_strategy(
        storage_backend=local_storage,
        rule_descriptor=rule_descriptor,
    )
    user_1_req = Request(path="dd", data={"user_id": "1"})

    current_time = datetime.datetime.now().replace(
        hour=0, minute=0, second=50, microsecond=0
    )
    with freezegun.freeze_time(current_time):
        assert sliding_window.do_limit(user_1_req) is False

    test_now = current_time + datetime.timedelta(seconds=15)
    with freezegun.freeze_time(test_now):
        assert sliding_window.do_limit(user_1_req) is False
        assert sliding_window.do_limit(user_1_req) is True
```

Notice in our test we set the initial time to a time near ending of a minute,
then move the time forward to be in the next minute, previous algorithms wouldn't
block this.
But since the window is not fixed in this limiter it will block the third request,
even if it's sent in the in the next minute. Nice improvement.

### Sliding Window Count

The sliding window log solves the problem of allowing over-limit
requests at unit edges.

But this algorithm uses more storage since it's storing full timestmap.

To solve this problem, there is another approach to count requests in each window.
When a request comes in calculate the current 1 minute window.
This window spans the current minute and probably the previous minute.
We can calculate what percentage of the rolling window is in previous window.
Then we can use that percentage to assign a weight to previous window request count.

so it would be
`total_requests = previous_window_weight * previous_window_count + current_window_count`.

For the implementation we use the previous way to create keys for each interval.

```python
class SlidingWindowCount(AbstractStrategy):
    def __init__(
        self,
        storage_backend: AbstractStorage,
        rule_descriptor: Descriptor,
    ):
        super(SlidingWindowCount, self).__init__(storage_backend, rule_descriptor)
        self.interval_len_sec = self.rule_descriptor.unit.to_seconds()
        self.interval_max = self.rule_descriptor.requests_per_unit

    def do_limit(self, request: Request):
        current_interval = str(int(datetime.now().timestamp() / self.interval_len_sec))
        prev_interval = str(int(datetime.now().timestamp() / self.interval_len_sec) - 1)
        key = self.rule_descriptor.key
        path = request.path
        value = request.data[key]

        previous_interval_key = self._get_counter_key(prev_interval, path, key, value)
        current_interval_key = self._get_counter_key(current_interval, path, key, value)

        if previous_interval_key is None or current_interval_key is None:
            return False

        self.storage_backend.incr(current_interval_key)

        current_interval_counter = self.storage_backend.get(current_interval_key) or 0
        previous_interval_counter = self.storage_backend.get(previous_interval_key) or 0

        percent_of_previous_interval_overlap_current_window = (
            1
            - (
                self.interval_len_sec
                - datetime.now().timestamp() % self.interval_len_sec
            )
            / self.interval_len_sec
        )

        total_requests = math.ceil(
            previous_interval_counter
            * percent_of_previous_interval_overlap_current_window
            + current_interval_counter
        )

        if total_requests > self.interval_max:
            return True

        return False

    def _get_counter_key(self, interval, path, key, value):
        descriptor = self.rule_descriptor
        key = descriptor.key
        if descriptor.value is not None and value != descriptor.value:
            return None
        else:
            return path + interval + "_" + key + "_" + value

```

Most of the code is similar to the sliding window log, except that we use
both previous and current interval keys to count the requests.
The mysterious formula `datetime.now().timestamp() % self.interval_len_sec`
always outputs
the number of seconds remaining until the end of interval and diving this by
the interval
length will give us the percentage of the current window passed. Subtracting
this from 1
will give how much of the sliding window is in the past interval to calculate
the weight.

Also since our calculation can result in a floating point number we can round it
up or down. Rounding up is chosen in this case.

#### Tests

Since this is another implementation for the sliding window, we can add it as a parameter
to all previous tests and the sliding window test.

```python
@pytest.mark.parametrize(
    "limit_strategy",
    [
        SlidingWindowLog,
        SlidingWindowCount,
    ],
)
def test_sliding_window_does_not_allow_requests_in_unit_edges
```

And finally running all the tests, results in 18 tests for all of our strategies
with very minimal test code.
It's always good to write less code cause less code is better.

```python
tests/limit_strategy/test_limit_strategy.py ..............                                                                         [ 77%]
tests/service/test_limiter.py ....                                                                                                 [100%]

=========================================================== 18 passed in 0.20s ===========================================================
```

## Conclusion

We now have implemented all different algorithms for our rate limiter.
The true power of our abstractions are shown in the less code we have to
write for each limiter, we can test them all with universal test cases,
the rate limiter service can use them without knowing what the underlying strategy
is.

In the next part we can see how to implement another storage backend such as redis,
without having to change any code in rate limiting algorithms.
