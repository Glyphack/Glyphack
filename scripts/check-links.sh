#!/usr/bin/env bash
set -euo pipefail

uvx linkchecker https://glyphack.com/ \
  --timeout=30 \
  --user-agent 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36' \
  --check-extern \
  --no-warnings \
  --ignore-url 'linkedin\.com' \
  --ignore-url 'facebook\.com' \
  --ignore-url 'twitter\.com' \
  --ignore-url 'x\.com' \
  --ignore-url 'openstreetmap\.org' \
  --ignore-url 'http://www.catb.org/~esr/' \
  --ignore-url 'https://datagenetics.com' \
  --ignore-url 'https://cacm.acm.org/blogs/blog-cacm/153780-data-mining-the-web-via-crawling/fulltext' \
  --ignore-url 'https://www.washingtonpost.com/wp-srv/national/longterm/' \
  --ignore-url 'https://www.cloudflare.com/en-gb/learning/bots/what-is-rate-limiting/' \
  --ignore-url 'ttps://www.science.org/content/article/people-would-rather-be-electrically-shocked-left-alone-their-thoughts' \
  --ignore-url 'https://docs.confluent.io/platform/current/installation/configuration/consumer-configs.html#consumerconfigs_max.poll.interval.ms'
