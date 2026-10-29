# Status — 2026-10-24

Detailed numbers: [docs/results.md](results.md).

## Что сделано в этом проходе

* Код D1 вынесен в `calc/d1_foundation.py`; коэффициенты приведены к официальному тексту СП:
  γc1=1,2 (табл.5.4, IL 0,25–0,5), γc2=1,0 (L/H≥4), α — табл.5.8, σzp=α·p, Hc по п.5.6.41
  (0,5σzg), su=10 см (прил. Г, табл. Г.1).
* `traceability.yml` + `tools/validate_traceability.py`: сборка падает на сиротских пунктах,
  тестах без пункта и зелёных статусах без подтверждённой редакции нормы.
* Тесты: golden (pytest-regressions), property-based (hypothesis), независимость шага (0,4/0,2/0,1 м),
  размерности (pint), негативные сценарии.
* Воспроизводимость: `requirements.lock`, `Dockerfile`, GitHub Actions, `make verify`.
* Ручной контроль: `docs/manual-check-d1.md` — R=215,62 кПа; s=4,232 см; Hc=3,6 м.

## Открытые пункты (не закрыты)

1. Сверка с коммерческим ядром ±5 % — не выполнена (нет лицензий/доступа); см. `docs/benchmarks/README.md`.
2. Строки 38/43 табл.5.5 восстановлены интерполяцией из-за OCR-повреждения PDF.
3. Осадка при d ≥ 5 м требует учёта σzγ (п.5.6.34) — код отказывается считать.
4. Нормативный маршрут СП 24.13330 для свай в OSS отсутствует — стратегический пробел.
5. D2 (openpile): кросс-модель Dunkirk применима только при D≈2 м, L=12 м; иное — отказ.

## Пункты прошлого прохода: закрыто / открыто

| Пункт | Статус |
|---|---|
| Единицы `initial_subgrade_modulus` (kN/m³) | закрыто: формула + эмпирическая проверка dp/dy = k·X (0,9969–0,9991) |
| Кросс-модель Dunkirk (Dr в %, X/D вне диапазона → NaN) | закрыто: Dr=75; валидная сверка D=2,0/L=12 — различие 2,2–3,6× (один порядок) |
| Противоречие приложения su (Г/Е/Д) | закрыто: Г — новое строительство, Д — категории состояния, Е — реконструкция |
| Нормативные коэффициенты D1 (γc1, γc2, α, σzp, Hc) | закрыто: сверено по официальному тексту, числа обновлены (R=215,62; s=4,232) |
| Сверка с коммерческим ядром ±5 % | **открыто**: нет лицензионного доступа; план — docs/benchmarks/README.md |
| Строки 38/43 табл.5.5 (OCR) | **открыто**: восстановлены интерполяцией, помечено |
| Осадка при d ≥ 5 м (σzγ) | **открыто**: код отказывается считать |
| Нормативный маршрут СП 24.13330 (сваи) | **открыто**: в OSS отсутствует |


## Update 2026-10-29: B2 benchmark (table 5.8 vs Boussinesq) and crash-recovery test

* **Table 5.8 benchmark closed.** Exact elastic center values (closed-form angular-point
  formula, validated against numeric integration to 0.4–0.6%) run 2.7–31.6% ABOVE the
  tabulated α as ξ grows. Tabulated α is conservative by design — our settlement uses it,
  so results stay on the safe side. Pinned by `tests/test_boussinesq_table58.py` (15 checks)
  and wired into `traceability.yml` under the табл.5.8 clause.
* **Crash-recovery test (unplanned, real).** On 2026-10-26 the compute node's venvs were wiped
  by a third-party cleanup (not our cron). On 2026-10-28 the geotech-base contour was fully
  rebuilt from its freeze file in 3 minutes (job venv-rebuild-001) with import test 21/21 —
  the freeze contract (clause 6.1.6) proved itself in a real outage.

## Open items (unchanged)

1. Commercial-core cross-check (±5%) — no licensed access.
2. Table 5.5 rows 38/43 restored by interpolation (OCR damage) — flagged.
3. Settlement for d ≥ 5 m (σzγ term) — code refuses.
4. SP 24.13330 normative route for piles — absent in OSS.

## Update 2026-10-29 (2): clean-machine verification

* Full `pip install -r requirements.lock` + `make verify` re-run on a second clean venv:
  TRACEABILITY OK (10 clauses, 19 tests), 31 tests passed.
* Found: Pint 0.24.4 has no Python 3.9 wheel — declared Python ≥ 3.10 requirement in README.
  CI (Python 3.12) and Docker (3.12-slim) are unaffected.
* Subagent norm-check and adversarial review were dispatched on 2026-10-28 (bench2); their
  findings on slope/pile benchmarks are to be applied in the next benchmark round (B1/B3).

## Update 2026-10-29: commercial cross-check cancelled; B1/B3 benchmarks started

Owner decision: no commercial-core verification. Oracle stack now: manual closed form (done),
independent second implementation (done), cross-tool comparisons (B1/B3 in progress), exact elastic
closed forms (done, table 5.8 conservative 3–32 %). Details: docs/benchmarks/README.md.
