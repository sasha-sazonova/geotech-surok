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

## Update 2026-10-30: closing the four open items

| Пункт | Что сделано | Статус |
|---|---|---|
| Осадка при d ≥ 5 м | Реализовано второе слагаемое (5.16): `s = βΣ[σzp/E − σzγ/Ee]h`; σzγ = α·σzg,0 по (5.18) **с размерами котлована** (п.5.6.33); Ee ≈ 5E по прим. 1; отказ при попытке опустить слагаемое для d ≥ 5 м; отказ при p < σzg,0 (нужна (5.19), п.5.6.35) | **закрыто** (кроме (5.19)) |
| Строки 38/43 табл.5.5 | Введён `UnverifiedNormValue` + `RESTORED_ROWS = {38, 43}`: любое использование восстановленной ячейки (точное φ=38/43 или интерполяция через неё) даёт «не определено», а не число. `allow_restored=True` — только для исследования чувствительности | **закрыто как защита** (ячейки остаются неподтверждёнными) |
| Классы доверия источников | `docs/data-sources.md`: `normative` / `reference` / `computed` / `cancelled`; Engineering ToolBox зарегистрирован как `reference`; валидатор требует `trust_class` + дату у каждого источника и запрещает зелёный статус на справочнике | **закрыто** |
| Мониторинг контуров | runner v3: `in/requires.txt` (preflight путей), `health.txt` (интерпретаторы контуров + свободный диск), `failed preflight` в статусе, всё в `runner.log` | **закрыто** |

Проверка: 65 тестов, TRACEABILITY OK (12 пунктов, 39 тестов); D1 не сдвинулся — R=215,62 кПа,
s=4,232 см, Hc=3,6 м; расширенная плита 2,4×2,8 — R=218,82, p=214,57, s=3,595 см.

Остаётся открытым: СП 24.13330 (нормативный маршрут свай в OSS), формула (5.19) при p < σzg,0,
ячейки 38/43 до сверки с бумажным оригиналом.

## Update 2026-10-30 (2): one source of truth, one working folder

Прежняя раскладка расчётного кода (`calc/d1_foundation/` и `calc/d2_pile/` как каталоги)
перенесена в локальный архив `calc/legacy/` и в публичный репозиторий не входит: два
параллельных набора кода давали разъезжающиеся числа. Канон — `calc/d1_foundation.py`
и `calc/b1_slope.py` в этом репозитории; рабочая папка агента
(`~/.openclaw/workspace-geotech_surok`) синхронизируется из репозитория, а её публичный
снимок (`Documents/geotech_surok`) — односторонним `rsync --delete`.
