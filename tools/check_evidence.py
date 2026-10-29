"""README 대표 수치를 제출 산출물 CSV/JSON과 다시 대조한다."""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "outputs" / "tables"


def rows(name: str) -> list[dict[str, str]]:
    with (TABLES / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def close(actual: float, expected: float, tol: float = 5e-4) -> None:
    if not math.isclose(actual, expected, abs_tol=tol):
        raise AssertionError(f"expected {expected}, got {actual}")


def main() -> int:
    checks: list[str] = []

    leakage = rows("t13_naive_binary_contrast.csv")
    row_random = next(r for r in leakage if r["라벨 생성 방식"].startswith("방식 B") and r["분할 방식"].startswith("행 무작위"))
    day_group = next(r for r in leakage if r["라벨 생성 방식"].startswith("방식 B") and r["분할 방식"].startswith("작업일 그룹"))
    close(float(row_random["ROC-AUC"]), 0.586)
    close(float(day_group["ROC-AUC"]), 0.305)
    checks.append("leakage_split=0.586->0.305")

    integrity = {r["관측 사실"]: r["값"] for r in rows("t21_integrity_verdict.csv")}
    assert "800" in integrity["연속 일치 구간 길이"]
    assert "4 일" in integrity["반복된 작업일 수"]
    assert "26.8%" in integrity["전체 데이터 대비 비중"]
    checks.append("duplicated_block=800x4=26.8%")

    daily = rows("t22_taskA_model_comparison.csv")[0]
    close(float(daily["LOO-MAE"]), 1.536)
    checks.append("daily_loo_mae=1.536")

    normal = next(r for r in rows("t30_c1_normal_model.csv") if r["변수집합"] == "F1 가압력만" and r["모형"] == "HistGradientBoosting")
    close(float(normal["LODO R2"]), 0.5091)
    checks.append("normal_lodo_r2=0.5091")

    severity = [float(r["평균"]) for r in rows("t41_severity_sweep.csv")]
    close(sum(severity) / len(severity), 0.971, tol=6e-4)
    close(min(severity), 0.954)
    checks.append("synthetic_mean_worst_auc=0.971/0.954")

    nested = rows("t50_nested_k.csv")
    assert len(nested) == 5 and {r["선택된 k"] for r in nested} == {"3"}
    checks.append("nested_k=3_in_5/5")

    defect = [float(r["순열 p"]) for r in rows("t51_defect_link_main.csv") if r["순열 p"]]
    close(min(defect), 0.6511)
    checks.append("defect_link_min_p=0.6511")

    chart = rows("t55b_day_control_chart.csv")[0]
    assert chart["이상일 탐지"] == "3/3" and chart["안정일 오경보"] == "0/5"
    checks.append("day_shift=3/3_false_alarm=0/5")

    day_test = next(r for r in rows("t61_analysis_unit.csv") if r["분석단위"].startswith("작업일"))
    close(float(day_test["p 값"]), 0.0179)
    checks.append("day_level_p=0.0179")

    external = rows("t78_external_model_ranking.csv")
    close(float(external[0]["ROC-AUC"]), 0.899)
    assert len(external) == 9
    checks.append("external_auc_rank=0.899_1/9")

    manifest = json.loads((ROOT / "outputs" / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["cited_total"] == 94 and manifest["verdict"] == "PASS"
    checks.append("manifest=94_PASS")

    print("EVIDENCE_CHECK=PASS")
    for check in checks:
        print(check)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (AssertionError, KeyError, StopIteration, FileNotFoundError, ValueError) as exc:
        print(f"EVIDENCE_CHECK=FAIL: {exc}")
        sys.exit(1)
