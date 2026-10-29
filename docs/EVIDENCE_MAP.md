# Evidence Map — 주장과 산출물의 연결

README와 면접에서 사용하는 대표 수치가 어떤 산출물에서 나왔는지 바로 추적할 수 있도록 정리했다. `python tools/check_evidence.py`로 핵심 수치를 다시 대조할 수 있다.

| 주장 | 근거 산출물 | 확인 항목 |
|---|---|---|
| 행 무작위 AUC 0.586 → 작업일 그룹 AUC 0.305 | `outputs/tables/t13_naive_binary_contrast.csv` | 일자 전가 방식의 분할별 ROC-AUC |
| 800점×4일, 전체 26.8% 복제 | `t19_block_identity.csv`, `t21_integrity_verdict.csv` | 연속구간 길이·반복일·전체 비중 |
| 작업일 불량건수 LOO-MAE 1.536 | `t10_loo_cv.csv`, `t22_taskA_model_comparison.csv` | 절편 전용 기준선 |
| 정상운전 관계 LODO R² 0.509 | `t30_c1_normal_model.csv` | 가압력만×HistGradientBoosting |
| 합성 7유형 평균/최악 AUC 0.971/0.954 | `t41_severity_sweep.csv`, `t44_final_detector.csv` | 유형별 평균의 전체 평균·최솟값 |
| 중첩 교차검증 5/5 폴드 k=3 | `t50_nested_k.csv` | 바깥 평가일별 선택 k |
| 실제 불량 연결 최소 순열 p=0.651 | `t51_defect_link_main.csv`, `t54_defect_link_conclusion.csv` | 검정 가능한 집계지표의 순열 p |
| 일 단위 공정 이동 3/3, 안정일 오경보 0/5 | `t55b_day_control_chart.csv` | 가압력 중앙값 2σ 관리도 |
| 작업일 단위 정확 순열 p=0.0179 | `t61_analysis_unit.csv` | 작업일 분석단위 행 |
| 외부 실제라벨 AUC 0.899, 9모형 중 1위 | `t78_external_model_ranking.csv`, `t79_external_conclusion.csv` | 고정 kNN 설정의 외부 순위 |
| 보고서 인용 산출물 94개 PASS | `outputs/run_manifest.json` | cited_total·verdict·파일별 SHA-256 |

## 증거 수준

| 표기 | 말할 수 있는 것 | 말하면 안 되는 것 |
|---|---|---|
| 용접 실제운전 | 복제 구간, 공정 이동, 정상운전 관계 | 실제 불량 용접점 위치 |
| 용접 실제불량 | 작업일 불량건수와 집계 수준 관계 | 용접점 단위 FN·FP |
| 합성 이상 | 설계한 고장모드에 대한 민감도 | 실제 불량 탐지율 |
| 외부 실제라벨 | 고정한 탐지 절차의 외부 작동 가능성 | 로봇용접 도메인의 실제 성능 |

이 구분은 낮은 수치를 숨기기 위한 장치가 아니라, 서로 다른 정답지에서 얻은 숫자를 같은 의미로 섞지 않기 위한 장치다.
