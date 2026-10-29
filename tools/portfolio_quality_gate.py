"""Raw data 없이 실행하는 포트폴리오 저장소 품질 게이트."""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def check_python_syntax(errors: list[str]) -> int:
    files = sorted((ROOT / "src").glob("*.py"))
    for path in files:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeDecodeError) as exc:
            fail(f"Python parse failure: {path.relative_to(ROOT)}: {exc}", errors)
    return len(files)


def check_guardrails(errors: list[str]) -> None:
    required_snippets = {
        "src/04_naive_check.py": [
            "((null >= obs).sum() + 1) / (len(null) + 1)",
        ],
        "src/25_manifest.py": [
            'isin(["STALE", "MISSING", "UNKNOWN"])',
            "if start is None:",
            "return 1",
        ],
        "src/common.py": [
            '"t63_run_manifest.csv"',
            "EXTERNAL_FILES = {",
            "Warning: failed to write Markdown table",
        ],
        "src/13_inference.py": [
            "명목 88.9% Jackknife+ 구간",
            "일반 유한표본 보장 하한 77.8%",
        ],
        "src/14_final_model.py": [
            "p<0.01은 명목 임계다",
            "p<0.0038",
        ],
    }
    for relative, snippets in required_snippets.items():
        path = ROOT / relative
        if not path.exists():
            fail(f"Missing guardrail source: {relative}", errors)
            continue
        text = path.read_text(encoding="utf-8")
        for snippet in snippets:
            if snippet not in text:
                fail(f"Missing guardrail in {relative}: {snippet}", errors)


def check_local_markdown_links(errors: list[str]) -> int:
    link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    checked = 0
    for path in [ROOT / "README.md", ROOT / "PROJECT_CARD.md", ROOT / "docs" / "MY_CONTRIBUTION.md"]:
        if not path.exists():
            fail(f"Missing portfolio document: {path.relative_to(ROOT)}", errors)
            continue
        for target in link_pattern.findall(path.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            target_path = target.split("#", 1)[0]
            if not target_path:
                continue
            checked += 1
            resolved = (path.parent / target_path).resolve()
            if not resolved.exists():
                fail(f"Broken link: {path.relative_to(ROOT)} -> {target}", errors)
    return checked


def check_raw_data_scope(errors: list[str]) -> None:
    raw = ROOT / "data" / "raw"
    if not raw.exists():
        fail("Missing data/raw data-access guide", errors)
        return
    unexpected = [p for p in raw.rglob("*") if p.is_file() and p.name.lower() != "readme.md"]
    for path in unexpected:
        fail(f"Raw data must not be tracked: {path.relative_to(ROOT)}", errors)


def main() -> int:
    errors: list[str] = []
    python_files = check_python_syntax(errors)
    check_guardrails(errors)
    links = check_local_markdown_links(errors)
    check_raw_data_scope(errors)

    if errors:
        print("PORTFOLIO_QUALITY_GATE=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PORTFOLIO_QUALITY_GATE=PASS")
    print(f"python_files={python_files}")
    print(f"local_links={links}")
    print("raw_data_tracked=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
