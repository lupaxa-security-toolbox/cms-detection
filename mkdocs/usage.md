# Usage

Input is a single URL, or a file of URLs (one per line). If the argument
exists as a file, it is read as a list; otherwise it is treated as a URL.

## CLI flags

| Flag              | Default | Description                                         |
| :---------------- | :------ | :-------------------------------------------------- |
| `--active`        | off     | Run broader path probes after default confirm files |
| `--format`, `-f`  | `text`  | Output format: `text`, `json`, or `csv`             |
| `--output`, `-o`  | stdout  | Write results to this file                          |
| `--workers`, `-w` | `10`    | Thread-pool size for a file of URLs                 |
| `--delay`         | `0`     | Seconds to wait before each request                 |
| `--retries`       | `2`     | Retry count for failed fetches                      |
| `--verbose`       | off     | Append evidence notes to text lines                 |
| `--version`       | —       | Print the package version and exit                  |

```bash
cms-detection https://example.com
cms-detection https://example.com --active
cms-detection urls.txt --format json --output results.json
```

Default mode uses the homepage plus a few well-known public files for CMS
that already scored on that page. `--active` adds broader path probes, and
when the homepage has no signal it also walks the catalogue's confirm files.
A path is never a hit from HTTP 200 alone.

`--output` writes the chosen format to a file and does not also print
results on stdout.

Text line: `{url} => {cms} {version} ({confidence})`, plus a short evidence
note when `--verbose`. JSON is a list of result objects. CSV columns are
`url`, `cms`, `version`, `confidence`, `evidence`, `candidates`, and `error`.

Network and HTTP failures become `error` on that result and do not crash a
batch. Invalid URL or empty input exits non-zero.

## Library

```python
from lupaxa.cms_detection import detect, detect_many

result = detect("https://example.com", active=False)
print(result.cms, result.version, result.confidence)

results = detect_many(
    ["https://example.com", "https://example.org"],
    workers=10,
    active=False,
)
```

| Function       | Role                                                                 |
| :------------- | :------------------------------------------------------------------- |
| `detect`       | One target. Keyword-only: `active`, `delay`, `retries`, `timeout`    |
| `detect_many`  | Independent detects in input order. Same keywords plus `workers`     |

`detect()` does not raise on network or HTTP failure. Those become
`result.error` with `cms=None`. Invalid URL or empty input raises
`CmsDetectionError`.
