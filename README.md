<p align="center">
  <a href="https://github.com/lupaxa-security-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/security-toolbox/readme-logo.png" alt="Security Toolbox" />
  </a>
</p>

<h1 align="center">CMS Detection</h1>

Identify which CMS a website is using from public signals — name, evidence,
version when it is exposed, and a confidence rating.

> **Warning:** **Authorised use only.** Use this tool for authorised
> security-assessment recon only. You must have permission to test the target.

## Install

Python 3.10 or newer. `requests` and `beautifulsoup4` install with the package.

```bash
pip install lupaxa-cms-detection
cms-detection --help
```

## CLI

```bash
cms-detection https://example.com
cms-detection https://example.com --active
cms-detection urls.txt --format json --output results.json
python -m lupaxa.cms_detection --version
```

Default mode uses the homepage plus a few well-known public files for CMS
that already scored on that page. `--active` adds broader path probes, and
when the homepage has no signal it also walks the catalogue's confirm files.
A path is never a hit from HTTP 200 alone.

If the URL has no scheme, the tool tries `https://` first and falls back to
`http://` only when TLS or connect fails.

Pass one URL, or a file of URLs with one URL per line. When the argument is
an existing file, it is read as a list. Otherwise it is treated as a URL.

### CLI Flags

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

`--output` writes the chosen format to a file. Results stay off stdout.

A text line looks like `{url} => {cms} {version} ({confidence})`.
`--verbose` appends a short evidence note. JSON is a list of result objects.
CSV columns are `url`, `cms`, `version`, `confidence`, `evidence`,
`candidates`, and `error`.

Network and HTTP failures set `error` on that result and the batch
continues. An invalid URL or empty input exits non-zero. Unknown CMS is a
successful result: `cms` is empty and `error` is empty. A failed write of
the output file is reported after the scan, and the CLI exits non-zero.

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

`detect` takes one target. Keyword-only arguments are `active`, `delay`,
`retries`, and `timeout`. `detect_many` runs those detects independently,
keeps input order, and adds `workers`.

Network and HTTP failures do not raise. They become `result.error` with
`cms` set to `None`. An invalid URL or empty input raises `CmsDetectionError`.

## Results

`DetectResult` is a frozen dataclass.

| Field        | Type                   | Meaning                                                 |
| :----------- | :--------------------- | :------------------------------------------------------ |
| `url`        | `str`                  | Final URL after redirects, or the input if fetch failed |
| `cms`        | `str \| None`          | Best match name, or `None` if unknown                   |
| `version`    | `str \| None`          | Public version string, or `None`                        |
| `confidence` | `str \| None`          | `high`, `medium`, or `low` when `cms` is set            |
| `evidence`   | `tuple[Evidence, ...]` | Hits from the run, including candidate hits             |
| `candidates` | `tuple[str, ...]`      | Other CMS that scored, excluding `cms`                  |
| `error`      | `str`                  | Fetch or parse failure, or `""`                         |

`Evidence` fields are `kind` (`meta_generator`, `header`, `cookie`,
`script`, `path`), `value` (what was seen), and `cms` (which signature it
supported).

### Confidence Rules

Each matching signal adds points. Those points pick the winner and are not
shown in the CLI.

| Signal                                           | Points | Strength |
| :----------------------------------------------- | :----- | :------- |
| `meta_generator` substring match                 | 3      | strong   |
| Listed response header name present              | 3      | strong   |
| Matching `confirm_paths` or `active_paths` probe | 2      | path     |
| Cookie name prefix in `Set-Cookie`               | 1      | weak     |
| Script `src` host or path substring              | 1      | weak     |

| Confidence | Rule                                                                               |
| :--------- | :--------------------------------------------------------------------------------- |
| `high`     | Two or more independent passive kinds, or one strong passive plus a matching path  |
| `medium`   | One strong passive, or two weak passives                                           |
| `low`      | Path evidence only, or a single weak passive                                       |

`cms` is the highest total. Other names with a score greater than zero go
in `candidates`. Ties break on more distinct evidence kinds, then a version
being present, then alphabetical name.

A path probe counts when the status is allowed and a required snippet
appears in the body or headers.

## Development

```bash
make init
make python-install-dev
make python-check
```

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
