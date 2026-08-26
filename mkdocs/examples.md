# Examples

## Text (default)

```bash
cms-detection https://example.com
```

Typical line:

```text
https://example.com => WordPress 6.4.2 (high)
```

Add `--verbose` to append evidence notes:

```bash
cms-detection https://example.com --verbose
```

## JSON

```bash
cms-detection https://example.com --format json
cms-detection https://example.com --format json --output results.json
```

JSON is a list of result objects (evidence as dicts).

## File of URLs

Write one URL per line, then pass the file:

```bash
cms-detection urls.txt
cms-detection urls.txt --format json --output results.json
cms-detection urls.txt --format csv --output results.csv
cms-detection urls.txt --workers 4 --delay 0.2
```

Each URL is independent. `detect_many` and the CLI return results in input
order.

## Active probes

Default mode stops after homepage scoring plus confirm files for CMS that
already scored. `--active` adds broader path probes, and when the homepage
has no signal it also walks the catalogue's confirm files:

```bash
cms-detection https://example.com --active
```

A path is never a hit from HTTP 200 alone.

## Library

```python
from lupaxa.cms_detection import detect, detect_many

result = detect("https://example.com")
print(result.cms, result.version, result.confidence)

for item in detect_many(["https://example.com", "https://example.org"]):
    print(item.url, item.cms or "unknown", item.confidence or "")
```
