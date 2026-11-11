# Сурок — геотехнический агент с прослеживаемой нормативной цепочкой · Surok

[![verify](https://github.com/sasha-sazonova/geotech-surok/actions/workflows/verify.yml/badge.svg)](https://github.com/sasha-sazonova/geotech-surok/actions/workflows/verify.yml)

**Язык / Language:** [Русский](#русский) · [English](#english)

---

<a id="русский"></a>

## Русский


**Расчёт имеет ценность только тогда, когда его можно проверить.** Сурок готовит, выполняет
и проверяет геотехнические расчёты на открытых решателях, оборачивая каждое число в цепочку
`данные → пункт нормы → формула → реализация → тест → отчёт`, и считает статус
**«не определено»** полноценным результатом.

- Лендинг: <https://sasha-sazonova.github.io/geotech-surok/>
- Презентация: [RU](https://sasha-sazonova.github.io/geotech-surok/presentation/ru/) · [EN](https://sasha-sazonova.github.io/geotech-surok/presentation/en/)
- Техническое задание: [ТЗ v1.6](https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/docs/TZ-geotech-surok.md)

## Для чего агент

| Проблема | Что делает агент |
|---|---|
| Расчёты живут в проприетарных силосах, протокол перепечатывают руками | ведёт реестр норм с редакциями, изменениями и датами проверки |
| Экспертиза спрашивает происхождение, а получает скриншот | собирает таблицу трассируемости от исходных данных до пункта |
| Пропущенная проверка молча становится зелёной галочкой | возвращает «не определено» и останавливается вместо догадки |
| Результат невозможно воспроизвести | считает в замороженных окружениях с контрольными суммами и журналом задания |

Агент готовит, считает и проверяет. Подписывает и выпускает специалист.

## Как это выглядит в работе

Три реальных обращения к агенту — вопрос в чате, ответ и файлы, которыми ответ подкреплён:
[**DEMO.md**](DEMO.md). Без единой команды: что спросили, что ответили, чем доказали.

Установка одной командой (создаст окружение, поставит зависимости, прогонит проверки):

```bash
./install.sh                  # ядро: СП 22 + СП 24
./install.sh --with-engines   # плюс движки: 7 методов устойчивости откосов, подпорные стены
```

Пошаговая проверка воспроизводимости для тех, кто хочет убедиться сам:
[docs/verify-step-by-step.md](docs/verify-step-by-step.md).

## Установка за четыре команды

```bash
git clone https://github.com/sasha-sazonova/geotech-surok.git
cd geotech-surok
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
make verify        # ожидаемо: TRACEABILITY: OK + 179 passed
make quickstart    # первый расчёт по СП 22.13330.2016
```

Нужен только Python ≥ 3.9 и git. Подробности, вариант с Docker, Windows и разбор типовых ошибок —
[INSTALL.md](INSTALL.md). Проверено на чистой машине: установка 27 секунд, 179 тестов проходят.

## Как использовать

1. **Постановка** — объект, стадия, что считать и по какой норме.
2. **Данные** — отчёт изысканий, GEF/CPT, AGS4, скважины, SPT, УГВ, нагрузки, геометрия.
3. **Расчёт** — маршрут из реестра, замороженное окружение, сверка вторым инструментом.
4. **Протокол** — формулы с подстановкой чисел, статусы проверок, ограничения, таблица трассируемости.

Если данных не хватает, агент формирует список вопросов и останавливается до ответа.

## Структура репозитория

```
workspace-geotech_surok/          воркспейс агента (зеркало живого)
├── AGENTS.md SOUL.md IDENTITY.md TOOLS.md DESCRIPTION.md USER.md
├── norms/          реестр норм: 9 подтверждённых, 11 в очереди, registry.csv
├── methods/        модули, уровни верификации, правила приёмки
├── workflows/      П-1 изыскания, П-2 откосы, П-3 сваи, П-4 протоколы, протокол заданий
├── tools/          67 OSS-инструментов + карта покрытия 13 классов + лицензионная политика
├── calc/           расчётный код: d1_foundation (R, осадка, крен), b1_slope, sp24_piles,
│                   sp24_group, sp24_csp
├── scenarios/      сценарии YAML для запуска без программирования
├── examples/       quickstart_d1.py — расчёт с блоком «ВАШИ ДАННЫЕ»
├── tests/          179 тестов: golden, property-based, размерности, негативные, СП 24
├── procedures/     политика статусов расчёта и чек-лист приёмки
├── envs/           freeze контуров + packages.csv (105 пакетов, лицензии, ссылки)
├── reports/        протоколы и таблицы трассируемости по ревизиям
└── docs/           ТЗ v1.6, конкурентный анализ, статус
presentation/       презентации ru/ и en/ (назначение, использование, архитектура, факты)
index.html          двуязычный лендинг (корень GitHub Pages)
```

| Раздел | Ссылка |
|---|---|
| Воркспейс агента | <https://github.com/sasha-sazonova/geotech-surok/tree/main/workspace-geotech_surok> |
| Реестр норм | <https://github.com/sasha-sazonova/geotech-surok/tree/main/workspace-geotech_surok/norms> |
| Методики | <https://github.com/sasha-sazonova/geotech-surok/tree/main/workspace-geotech_surok/methods> |
| Воркфлоу | <https://github.com/sasha-sazonova/geotech-surok/tree/main/workspace-geotech_surok/workflows> |
| Инструментарий | <https://github.com/sasha-sazonova/geotech-surok/tree/main/workspace-geotech_surok/tools> |
| Расчётный код | <https://github.com/sasha-sazonova/geotech-surok/tree/main/workspace-geotech_surok/calc> |
| Окружения и пакеты | <https://github.com/sasha-sazonova/geotech-surok/tree/main/workspace-geotech_surok/envs> |
| Протокол D1 | <https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/reports/d1-foundation-v2/protocol.md> |
| Статус | <https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/docs/status.md> |
| Конкурентный анализ | <https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/docs/competitor-analysis.md> |
| Что мы умеем и сравнение с GEO5 | <https://sasha-sazonova.github.io/geotech-surok/coverage/> |
| Источники данных и классы доверия | <https://github.com/sasha-sazonova/geotech-surok/blob/main/docs/data-sources.md> |
| Покрытие СП 24.13330.2021 | <https://github.com/sasha-sazonova/geotech-surok/blob/main/docs/sp24-coverage.md> |

## Принципы

1. **Прослеживаемость** — каждое число раскрывается до пункта, редакции и версии инструмента.
2. **Честные статусы** — реализовано / воспроизведено / нормативный маршрут проверен / не определено.
3. **Воспроизводимость по контракту** — замороженные окружения, зафиксированный хост, SHA-256.
4. **Асинхронный расчёт** — каталог задания с входом, статусом и выходом; три повтора, затем честное «расчёта нет».
5. **Человек в контуре** — агент готовит, специалист подписывает.

## Состояние

ТЗ **v1.6** · расчётный контур: 105 пакетов, импорт-тест 21/21, freeze записан ·
runner **v3** (preflight контуров и health-мониторинг) · агент прошёл **6/6** приёмочных проверок.

**Что считается сейчас** (всё закреплено тестами, 179 тестов, трассируемость 30 пунктов / 154 тестов):

| Блок | Норма | Что реализовано | Ключевые числа |
|---|---|---|---|
| **D1 — фундамент мелкого заложения** | СП 22.13330.2016 | R по ф.(5.7); осадка по (5.16) с двумя слагаемыми, включая `d ≥ 5 м`; формула (5.19) при `p ≤ σzg,0`; расширение толщи при слое `E ≤ 7 МПа` (п.5.6.41); **крен** по (5.24)–(5.26) с табл. 5.9/5.10 | p = 286.0 против R = 215.62 кПа → не выполняется (+32.6 %); s = 4.232 см ≤ 10 см; Hc = 3.6 м; плита 2.4×2.8: R = 218.82, p = 214.57, s = 3.595 |
| **D2 — свая под горизонтальной нагрузкой** | API/Reese p-y (СП 24 этот расчёт не регламентирует) | openpile 1.0.3 + независимый МКЭ-решатель (`calc/d2_pile.py`): сверка с точной формой 0.1 %, с openpile +4.5 % / +10.1 % | H = 500 кН: y = 6.28 / 6.56 мм, Mmax = 890.5 / 980.4 кНм |
| **СП 24 — несущая способность** | СП 24.13330.2021 | сваи-стойки (7.5–7.8); забивные/вдавливаемые ф.(7.9) с **табл. 7.2 полностью** (пески и глины IL 0.1…0.6) и табл. 7.3/7.4; выдёргивание (7.11); буровые (7.13) с табл. 7.6 | пример: песок ср. крупности d = 10 м → R = 5000 кПа; глина IL = 0.1, d = 10 м → R = 7300 кПа |
| **СП 24 — осадки свай** | СП 24.13330.2021 | одиночная свая (7.34–7.39, табл. 7.18, обе ветви κ); взаимное влияние (7.40–7.42); куст n ≤ 25 с гибким и жёстким ростверком | δ = 0.17·ln(x)/x — максимум при x = e (свойство нормы) |
| **СП 24 — поле свай** | СП 24.13330.2021 | условный фундамент (7.45–7.49): `sef` по СП 22 + продавливание Δsp + сжатие ствола Δsc; границы по 7.4.9 | — |
| **СП 24 — КСП** | СП 24.13330.2021 | суммарные жёсткости по 7.4.18/7.4.8; нелинейная жёсткость сваи (7.44); отпор плиты (7.4.20); распределение нагрузки и три проверки | 25 свай, Nd = 20 МН → осадка ≈ 5 мм, 96 % на сваи |
| **Устойчивость откосов — LEM** | методы предельного равновесия (не пункт нормы) | 7 методов: OMS/Fellenius, Bishop, Janbu, Corps, Lowe–Karafiath, Spencer, Morgenstern–Price; автопоиск критического круга (движок xslope 1.0.7, Apache-2.0) | на круге B1: OMS 1.590, Bishop 1.692, разброс 7 методов 0.147 |
| **Давление грунта и подпорные стены** | СП 22.13330.2016 / СП 542.1325800.2024 (частично) | K_a/K_p Ранкин, K_a Кулон, эпюра с УГВ и пригрузкой, трещина отрыва, FS сдвига и опрокидывания, краевые давления, шпунт по Блюму | Ka и Ea сверены с geoeq: ΔKa 0.001 %, ΔEa 0.0 % |

**Проверки на сторонних решателях:** B1 откос (наши Fellenius/Bishop против движка xslope — совпадение ≤0.02 %; прежняя сверка с pyslope «2.2 %» аннулирована как ложный зелёный статус),
B2 табл. 5.8 против точного решения Буссинеска (таблица консервативна на 3–32 %),
B3 осевая свая (unit-формулы API против ручного расчёта — 0.0 %).

**Что осознанно не считается** (возвращается «не определено», не догадка): краевые давления при
моменте; сваи в грунтах, для которых издание нормы печатает прочерк в таблице; КСП с краевыми
эффектами; численные методы 7.4.13 и 7.5; отрицательное трение.

Проверка: ручной эталон (`docs/manual-check-d1.md`), **179 тестов**, валидатор трассируемости
(30 пунктов, 154 тестов) — CI зелёный (verify + docker). Полная матрица покрытия СП 24 —
[`docs/sp24-coverage.md`](docs/sp24-coverage.md).

### Быстрый старт

```bash
make verify      # трассируемость + тесты
make quickstart  # расчёт D1 с данными по умолчанию
make scenario    # расчёт из YAML-сценария (без программирования)
```

## Лицензия

Документация и презентации: Apache-2.0 (см. `LICENSE`, `NOTICE`).
Упомянутые open-source инструменты и нормативные документы принадлежат их авторам;
тексты норм в репозитории не размещаются.

## Проверка

Расчётное ядро покрыто проверяемой цепочкой: `traceability.yml` связывает каждый нормативный
пункт (документ → редакция → пункт → формула) с символами кода и тестами; валидатор роняет сборку
на сиротских пунктах, тестах без пункта и статусе «verified» без датированного источника.

```bash
make verify      # валидатор трассируемости + pytest (Python ≥ 3.9)
make regen       # перегенерация golden-файлов (только при осознанном изменении результатов)
make quickstart  # первый расчёт: workspace-geotech_surok/examples/quickstart_d1.py
docker build -t geotech-surok . && docker run --rm geotech-surok   # те же проверки на чистой машине
```

Пошаговая установка с нуля — [INSTALL.md](INSTALL.md).

Доказательства на сегодня:

| Пункт | Состояние |
|---|---|
| Независимый ручной расчёт (R = 215,62 кПа; s = 4,232 см) | `docs/manual-check-d1.md`, закреплён `test_manual_reference` |
| Нормативный текст сверен (СП 22.13330.2016, п.5.6.7/5.6.10/5.6.31/5.6.32/5.6.41, табл.5.4/5.5/5.8, прил.Г) | `docs/norm-sources/sp22-2016.md` |
| Golden / property / шаг / размерности / негативные | `tests/` |

---

<a id="english"></a>

## English

[![verify](https://github.com/sasha-sazonova/geotech-surok/actions/workflows/verify.yml/badge.svg)](https://github.com/sasha-sazonova/geotech-surok/actions/workflows/verify.yml)

**A calculation is only worth something if it can be checked.** Surok prepares, runs and verifies
geotechnical calculations over open-source solvers, wrapping every number in the chain
`data → clause → formula → implementation → test → report`, and treats **“not determined”**
as a first-class result.

- Landing: <https://sasha-sazonova.github.io/geotech-surok/>
- Presentation: [EN](https://sasha-sazonova.github.io/geotech-surok/presentation/en/) · [RU](https://sasha-sazonova.github.io/geotech-surok/presentation/ru/)
- Specification: [TZ v1.6](https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/docs/TZ-geotech-surok.md)

## What it is for

| Problem | What the agent does |
|---|---|
| Calculations live in proprietary silos; the report is retyped by hand | keeps a normative registry with editions, amendments and check dates |
| Expert review asks for provenance and gets a screenshot | builds a traceability table from source data to the clause |
| A missing check silently becomes a green tick | returns “not determined” and stops instead of guessing |
| Results cannot be reproduced | runs in frozen environments with checksums and a job journal |

The agent prepares, calculates and checks. A specialist signs and releases.

## What it looks like in use

Three real requests to the agent — the question in chat, the answer, and the files backing it:
[**DEMO.md**](DEMO.md) (Russian). No commands: what was asked, what was answered, what proves it.

One-command install (creates the environment, installs dependencies, runs the checks):

```bash
./install.sh                  # core: SP 22 + SP 24
./install.sh --with-engines   # plus engines: 7 slope-stability methods, retaining walls
```

Step-by-step reproducibility check: [docs/verify-step-by-step.md](docs/verify-step-by-step.md).

## Install in four commands

```bash
git clone https://github.com/sasha-sazonova/geotech-surok.git
cd geotech-surok
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
make verify        # expect: TRACEABILITY: OK + 179 passed
make quickstart    # first calculation (SP 22.13330.2016)
```

Only Python >= 3.9 and git are required. Docker, Windows notes and troubleshooting —
[INSTALL.en.md](INSTALL.en.md). Verified on a clean machine: 27 s install, 179 tests pass.

## How to use

1. **Brief** — object, design stage, what to calculate and to which code.
2. **Data** — investigation report, GEF/CPT, AGS4, boreholes, SPT, groundwater, loads, geometry.
3. **Calculation** — route from the registry, frozen environment, cross-tool verification.
4. **Report** — formulas with substituted numbers, check statuses, limits, traceability table.

If input data is missing, the agent produces a question list and stops until it is answered.

## Repository map

```
workspace-geotech_surok/          the agent workspace (mirrors the live one)
├── AGENTS.md SOUL.md IDENTITY.md TOOLS.md DESCRIPTION.md USER.md
├── norms/          normative registry: 9 confirmed, 11 queued, registry.csv
├── methods/        modules, verification levels, acceptance rules
├── workflows/      P-1 investigation, P-2 slopes, P-3 piles, P-4 reports, jobs protocol
├── tools/          67 OSS tools + 13-class coverage map + licence policy
├── calc/           calculation code: d1_foundation (R, settlement, tilt), b1_slope,
│                   sp24_piles, sp24_group, sp24_csp
├── scenarios/      YAML scenarios for calculation without coding
├── examples/       quickstart_d1.py — calculation with a "your data" block
├── tests/          179 tests: golden, property-based, dimensional, negative, SP 24
├── procedures/     calculation status policy and acceptance checklist
├── envs/           contour freezes + packages.csv (105 packages, licences, links)
├── reports/        protocols and traceability tables per revision
└── docs/           TZ v1.6, competitor analysis, status
presentation/       ru/ and en/ decks (purpose, usage, architecture, evidence)
index.html          bilingual landing page (GitHub Pages root)
```

| Section | Link |
|---|---|
| Agent workspace | <https://github.com/sasha-sazonova/geotech-surok/tree/main/workspace-geotech_surok> |
| Normative registry | <https://github.com/sasha-sazonova/geotech-surok/tree/main/workspace-geotech_surok/norms> |
| Methods | <https://github.com/sasha-sazonova/geotech-surok/tree/main/workspace-geotech_surok/methods> |
| Workflows | <https://github.com/sasha-sazonova/geotech-surok/tree/main/workspace-geotech_surok/workflows> |
| Tools | <https://github.com/sasha-sazonova/geotech-surok/tree/main/workspace-geotech_surok/tools> |
| Calculation code | <https://github.com/sasha-sazonova/geotech-surok/tree/main/workspace-geotech_surok/calc> |
| Environments and packages | <https://github.com/sasha-sazonova/geotech-surok/tree/main/workspace-geotech_surok/envs> |
| D1 protocol | <https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/reports/d1-foundation-v2/protocol.md> |
| Status | <https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/docs/status.md> |
| Competitor analysis | <https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/docs/competitor-analysis.md> |
| What we can do (EN) | <https://sasha-sazonova.github.io/geotech-surok/coverage/en/> |

## Design pillars

1. **Traceability** — every number resolves to a clause, an edition and a tool version.
2. **Honest statuses** — implemented / reproduced / normative route verified / not determined.
3. **Reproducibility by contract** — frozen environments, recorded host, SHA-256 checksums.
4. **Async compute** — job directory with input, status and output; three retries, then an honest “no result”.
5. **Human in the loop** — the agent prepares; a specialist signs.

## Status

Spec **v1.6** · compute contour: 105 packages, import test 21/21, freeze recorded ·
runner **v3** (contour preflight + health monitoring) · agent passed **6/6** acceptance checks.

**What is computed today** (all pinned by tests — 179 tests, traceability 30 clauses / 154 tests):

| Block | Norm | Implemented | Key numbers |
|---|---|---|---|
| **D1 — shallow foundation** | SP 22.13330.2016 | R by (5.7); settlement by (5.16) with both terms including `d ≥ 5 m`; formula (5.19) for `p ≤ σzg,0`; compressible-thickness extension for a layer with `E ≤ 7 MPa` (5.6.41); **tilt** by (5.24)–(5.26) with tables 5.9/5.10 | p = 286.0 vs R = 215.62 kPa → fails (+32.6 %); s = 4.232 cm ≤ 10 cm; Hc = 3.6 m; 2.4×2.8 m footing: R = 218.82, p = 214.57, s = 3.595 |
| **D2 — laterally loaded pile** | API/Reese p-y (СП 24 does not regulate this analysis) | openpile 1.0.3 + independent FEM solver (`calc/d2_pile.py`): 0.1 % vs exact closed form, +4.5 % / +10.1 % vs openpile | H = 500 kN: y = 6.28 / 6.56 mm, Mmax = 890.5 / 980.4 kNm |
| **SP 24 — bearing capacity** | SP 24.13330.2021 | end-bearing piles (7.5–7.8); driven piles (7.9) with **table 7.2 in full** (sands and clays IL 0.1…0.6) plus tables 7.3/7.4; pull-out (7.11); bored piles (7.13) with table 7.6 | example: medium sand at d = 10 m → R = 5000 kPa; clay IL = 0.1 at d = 10 m → R = 7300 kPa |
| **SP 24 — pile settlement** | SP 24.13330.2021 | single pile (7.34–7.39, table 7.18, both κ branches); interaction (7.40–7.42); group n ≤ 25 with flexible and rigid cap | δ = 0.17·ln(x)/x — maximum at x = e (a property of the norm) |
| **SP 24 — pile field** | SP 24.13330.2021 | fictitious footing (7.45–7.49): `sef` via SP 22 + punch Δsp + shaft compression Δsc; boundaries per 7.4.9 | — |
| **SP 24 — combined pile-raft (CSP)** | SP 24.13330.2021 | combined stiffness per 7.4.18/7.4.8; nonlinear pile stiffness (7.44); plate subgrade reaction (7.4.20); load split with three checks | 25 piles, Nd = 20 MN → settlement ≈ 5 mm, 96 % carried by piles |
| **Slope stability — LEM** | limit equilibrium methods (not a norm clause) | 7 methods: OMS/Fellenius, Bishop, Janbu, Corps, Lowe–Karafiath, Spencer, Morgenstern–Price; automatic critical-circle search (xslope 1.0.7 engine, Apache-2.0) | on the B1 circle: OMS 1.590, Bishop 1.692, spread across 7 methods 0.147 |
| **Earth pressure and retaining walls** | SP 22.13330.2016 / SP 542.1325800.2024 (partial) | K_a/K_p Rankine, Coulomb K_a, diagram with water table and surcharge, tension crack, sliding/overturning factors, edge pressures, Blum sheet pile | Ka and Ea cross-checked against geoeq: ΔKa 0.001 %, ΔEa 0.0 % |

**Cross-tool benchmarks:** B1 slope (our Fellenius/Bishop vs the xslope engine — agreement ≤0.02 %; the earlier pyslope "2.2 %" claim is withdrawn as a false green status),
B2 table 5.8 vs exact Boussinesq (table is conservative by 3–32 %),
B3 axial pile (API unit formulas vs hand calculation — 0.0 %).

**Deliberately not computed** (returns "not determined", never a guess): edge pressures under moment;
piles in soils where the printed norm shows a dash in the table; CSP edge effects; numerical methods
7.4.13 and 7.5; negative friction.

Verification: manual reference (`docs/manual-check-d1.md`), **179 tests**, traceability validator
(30 clauses, 154 tests) — CI green (verify + docker). Full SP 24 coverage matrix:
[`docs/sp24-coverage.md`](docs/sp24-coverage.md).

### Quick start

```bash
make verify      # traceability + tests
make quickstart  # D1 calculation with default data
make scenario    # calculation from a YAML scenario (no coding)
```

## License

Documentation and presentations: Apache-2.0 (see `LICENSE`, `NOTICE`).
Referenced open-source tools and normative documents remain with their respective authors;
normative texts are not included.

## Verification

The calculation core is covered by a verifiable chain: `traceability.yml` links every normative
clause (document → edition → clause → formula) to code symbols and tests; the validator fails the
build on orphan clauses, unreferenced tests, or a "verified" status without a dated source.

```bash
make verify      # traceability validator + pytest (Python >= 3.9)
make regen       # regenerate golden files (only when results intentionally change)
make quickstart  # first calculation: workspace-geotech_surok/examples/quickstart_d1.py
docker build -t geotech-surok . && docker run --rm geotech-surok   # clean-machine run of the same checks
```

Step-by-step install from scratch — [INSTALL.en.md](INSTALL.en.md).

Evidence today:

| Item | State |
|---|---|
| Manual independent calculation (R = 215.62 kPa; s = 4.232 cm) | `docs/manual-check-d1.md`, pinned by `test_manual_reference` |
| Normative text verified (СП 22.13330.2016, п.5.6.7/5.6.10/5.6.31/5.6.32/5.6.41, табл.5.4/5.5/5.8, прил.Г) | `docs/norm-sources/sp22-2016.md` |
| Golden / property / step / units / negative tests | `tests/` |

