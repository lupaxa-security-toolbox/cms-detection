<p align="center">
  <a href="https://github.com/lupaxa-security-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/security-toolbox/readme-logo.png" alt="Security Toolbox" />
  </a>
</p>

<h1 align="center">cms-detection</h1>

Identify which CMS a website is using from public signals — name, evidence,
version when it is exposed, and a confidence rating.

> [!WARNING]
> **Authorised use only.** Use this tool for authorised security-assessment
> recon only. You must have permission to test the target.

<p align="center">
  <a href="https://cms-detection.thelupaxaproject.org/">Documentation</a>
  ·
  <a href="https://github.com/lupaxa-security-toolbox/cms-detection">GitHub</a>
</p>

## Install

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

## Library

```python
from lupaxa.cms_detection import detect

result = detect("https://example.com", active=False)
print(result.cms, result.version, result.confidence)
```

## Development

```bash
make init
make python-install-dev
make python-check
make mkdocs-serve
```

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
