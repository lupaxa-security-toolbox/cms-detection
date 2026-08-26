<!-- markdownlint-disable -->
<p align="center">
  <a href="https://github.com/lupaxa-security-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/security-toolbox/readme-logo.png" alt="Project Logo" width="256"/><br/>
  </a>
</p>
<h3 align="center">
  The Lupaxa Security Toolbox<br />
  Part of The Lupaxa Project
</h3>

<br />

# lupaxa-cms-detection

Identify which CMS a website is using from public signals — name, evidence,
version when it is exposed, and a confidence rating.

Built for authorised security-assessment recon used by The Lupaxa Project.

> [!WARNING]
> **Authorised use only.** Use this tool for authorised security-assessment
> recon only. You must have permission to test the target.

## Features

- Detect a CMS from public signals: generator tags, headers, cookies, and scripts
- Report **name**, **evidence**, **version** when it is exposed, and **confidence**
- Quiet default: homepage plus confirm files for CMS that already scored
- Optional **`--active`** broader path probes, including a catalogue confirm sweep when the homepage is quiet (a path is never a hit from HTTP 200 alone)
- Library API (`detect` / `detect_many`) and CLI (`cms-detection`)
- Text, JSON, and CSV output
- Fully typed, linted, formatted, and tested

## Installation

### From PyPI

```bash
pip install lupaxa-cms-detection
```

### From source (development mode)

```bash
pip install -e ".[dev]"
```

Requires Python 3.10+. Runtime dependencies: `requests`, `beautifulsoup4`.

## Library quick start

```python
from lupaxa.cms_detection import detect

result = detect("https://example.com", active=False)
print(result.cms, result.version, result.confidence)
```

## CLI quick start

```bash
cms-detection --help
cms-detection https://example.com
cms-detection https://example.com --active
cms-detection urls.txt --format json --output results.json
```

You can also run the CLI as a module:

```bash
python -m lupaxa.cms_detection --help
python -m lupaxa.cms_detection --version
```

## Documentation

Online documentation:

[Documentation](https://cms-detection.thelupaxaproject.org/)

Source repository:

[GitHub](https://github.com/lupaxa-security-toolbox/cms-detection)

### Serve docs locally

From a clone of the repository:

```bash
make mkdocs-serve
```

Then open the local URL printed by MkDocs in your browser.

## Development

Clone the repository and install with Make:

```bash
make init                # first-time makefile-skills checkout
make python-install-dev  # editable install with [dev]
make python-check        # lint, type-check, and test
```

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
