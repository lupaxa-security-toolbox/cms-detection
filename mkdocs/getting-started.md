# Getting started

## Requirements

- Python 3.10 or newer
- `requests` and `beautifulsoup4` (installed with the package)

## Install

```bash
pip install lupaxa-cms-detection
cms-detection --help
```

Library import:

```python
from lupaxa.cms_detection import detect

result = detect("https://example.com", active=False)
print(result.cms, result.version, result.confidence)
```

Module entry point:

```bash
python -m lupaxa.cms_detection --version
```

### From source (development)

```bash
make init
make python-install-dev
cms-detection --version
```

## First run

Default mode fetches the homepage, then confirm files for CMS that already
scored:

```bash
cms-detection https://example.com
```

`--active` adds broader path probes, and when the homepage has no signal it
also walks the catalogue's confirm files. A path is never a hit from HTTP
200 alone:

```bash
cms-detection https://example.com --active
```

If the URL has no scheme, the tool tries `https://` first and falls back to
`http://` only if TLS or connect fails.

## Makefile helpers

```bash
make init                 # clone makefile-skills into .makefiles/
make python-install-dev   # editable install with [dev]
make python-check         # lint + type + test
make mkdocs-serve         # local docs site
```
