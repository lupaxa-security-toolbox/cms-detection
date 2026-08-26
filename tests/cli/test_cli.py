"""CLI entrypoint."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from lupaxa.cms_detection.cli import main
from lupaxa.cms_detection.models import DetectResult, Evidence
from lupaxa.cms_detection.version import get_version


def _wp() -> DetectResult:
    return DetectResult(
        url="https://blog.example/",
        cms="WordPress",
        version="6.4.2",
        confidence="medium",
        evidence=(Evidence("meta_generator", "WordPress 6.4.2", "WordPress"),),
        candidates=(),
        error="",
    )


def test_help_exits_zero(capsys: object) -> None:
    assert main(["--help"]) == 0


def test_version_flag(capsys) -> None:  # type: ignore[no-untyped-def]
    assert main(["--version"]) == 0
    assert get_version() in capsys.readouterr().out


def test_text_output(capsys) -> None:  # type: ignore[no-untyped-def]
    with patch("lupaxa.cms_detection.cli.detect_many", return_value=[_wp()]):
        code = main(["https://blog.example"])
    assert code == 0
    out = capsys.readouterr().out
    assert "https://blog.example/ => WordPress 6.4.2 (medium)" in out


def test_json_format(capsys) -> None:  # type: ignore[no-untyped-def]
    with patch("lupaxa.cms_detection.cli.detect_many", return_value=[_wp()]):
        code = main(["https://blog.example", "--format", "json"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload[0]["cms"] == "WordPress"


def test_active_flag_passed() -> None:
    with patch("lupaxa.cms_detection.cli.detect_many", return_value=[_wp()]) as mocked:
        main(["https://blog.example", "--active"])
    assert mocked.call_args.kwargs["active"] is True


def test_file_input(tmp_path: Path) -> None:
    listing = tmp_path / "urls.txt"
    listing.write_text("https://a.example\nhttps://b.example\n", encoding="utf-8")
    with patch("lupaxa.cms_detection.cli.detect_many", return_value=[_wp(), _wp()]) as mocked:
        main([str(listing)])
    assert mocked.call_args.args[0] == ["https://a.example", "https://b.example"]


def test_csv_format(capsys) -> None:  # type: ignore[no-untyped-def]
    with patch("lupaxa.cms_detection.cli.detect_many", return_value=[_wp()]):
        code = main(["https://blog.example", "--format", "csv"])
    assert code == 0
    out = capsys.readouterr().out
    assert "url,cms,version,confidence,evidence,candidates,error" in out
    assert "WordPress" in out


def test_verbose_appends_evidence(capsys) -> None:  # type: ignore[no-untyped-def]
    with patch("lupaxa.cms_detection.cli.detect_many", return_value=[_wp()]):
        code = main(["https://blog.example", "--verbose"])
    assert code == 0
    assert "evidence: meta_generator=WordPress 6.4.2" in capsys.readouterr().out


def test_output_json_writes_file_not_stdout(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    dest = tmp_path / "results.json"
    with patch("lupaxa.cms_detection.cli.detect_many", return_value=[_wp()]):
        code = main(["https://blog.example", "--format", "json", "--output", str(dest)])
    assert code == 0
    assert capsys.readouterr().out == ""
    payload = json.loads(dest.read_text(encoding="utf-8"))
    assert payload[0]["cms"] == "WordPress"


def test_output_write_failure_exits_nonzero(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    dest = tmp_path / "missing" / "results.json"
    with patch("lupaxa.cms_detection.cli.detect_many", return_value=[_wp()]):
        code = main(["https://blog.example", "--output", str(dest)])
    assert code == 2
    assert "Failed to write output file" in capsys.readouterr().err


def test_empty_url_file_exits_nonzero(tmp_path: Path) -> None:
    listing = tmp_path / "empty.txt"
    listing.write_text("\n\n", encoding="utf-8")
    with patch("lupaxa.cms_detection.cli.detect_many") as mocked:
        code = main([str(listing)])
    assert code == 2
    mocked.assert_not_called()
