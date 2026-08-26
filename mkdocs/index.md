# CMS Detection

`lupaxa-cms-detection` identifies which CMS a website is using from public
signals. It reports the CMS name, the evidence that led to the call, a version
when one is exposed, and a confidence rating.

!!! warning "Authorised use only"
    Use this tool for authorised security-assessment recon only. You must have
    permission to test the target.

Install the package for the library API and the `cms-detection` console
command:

```bash
pip install lupaxa-cms-detection
cms-detection https://example.com
```

You can also run `python -m lupaxa.cms_detection`.

## What it does

- Scores homepage signals (generator meta, headers, cookies, script hosts)
- Fetches a few well-known public files when identity or version is still missing
- Optionally runs broader path probes with `--active`
- Never treats a bare HTTP 200 as a path hit — the response must contain a matching snippet
- Returns one best `cms`, other `candidates`, evidence, and confidence

## Next steps

- [Getting started](getting-started.md) — install and first run
- [Usage](usage.md) — CLI flags and the library API
- [Reference](reference.md) — result fields and confidence rules
- [Examples](examples.md) — text, JSON, and file-of-URLs recipes
