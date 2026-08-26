# Reference

## Result fields

`DetectResult` is a frozen dataclass. Unknown CMS is success: `cms` is
`None` and `error` is empty.

| Field        | Type                   | Meaning                                                    |
| :----------- | :--------------------- | :--------------------------------------------------------- |
| `url`        | `str`                  | Final URL after redirects, or the input if fetch failed    |
| `cms`        | `str \| None`          | Best match name, or `None` if unknown                      |
| `version`    | `str \| None`          | Public version string, or `None`                           |
| `confidence` | `str \| None`          | `high`, `medium`, or `low` when `cms` is set               |
| `evidence`   | `tuple[Evidence, ...]` | Hits from the run, including candidate hits                |
| `candidates` | `tuple[str, ...]`      | Other CMS that scored, excluding `cms`                     |
| `error`      | `str`                  | Fetch or parse failure, or `""`                            |

`Evidence` fields: `kind` (`meta_generator`, `header`, `cookie`, `script`,
`path`), `value` (what was seen), and `cms` (which signature it supported).

## Confidence rules

Each matching signal adds points used only to pick the winner. Points are
not shown in the CLI.

| Signal                                           | Points | Strength |
| :----------------------------------------------- | :----- | :------- |
| `meta_generator` substring match                 | 3      | strong   |
| Listed response header name present              | 3      | strong   |
| Matching `confirm_paths` or `active_paths` probe | 2      | path     |
| Cookie name prefix in `Set-Cookie`               | 1      | weak     |
| Script `src` host or path substring              | 1      | weak     |

| Confidence | Rule                                                                              |
| :--------- | :-------------------------------------------------------------------------------- |
| `high`     | Two or more independent passive kinds, or one strong passive plus a matching path |
| `medium`   | One strong passive, or two weak passives                                          |
| `low`      | Path evidence only, or a single weak passive                                      |

`cms` is the highest total. Other names with a score greater than zero go
in `candidates`. Ties: more distinct evidence kinds, then presence of a
version, then alphabetical name.

A path probe counts only when the status is allowed **and** a required
snippet appears in the body or headers. HTTP 200 alone is not a hit.

## Errors

| Case                              | Behaviour                                              |
| :-------------------------------- | :----------------------------------------------------- |
| Network, timeout, TLS, HTTP error | `error` set, `cms=None`; the batch continues           |
| Invalid URL or empty input        | CLI exits non-zero; library raises `CmsDetectionError` |
| One probe fails                   | That probe is skipped; the detect continues            |
| Unknown CMS                       | Success: `cms=None`, `error=""`                        |
| Output file write failure         | CLI reports it and exits non-zero after the scan       |
