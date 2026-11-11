# Как это выглядит для инженера: диалог с ботом и чем он подкреплён

**Язык:** [Русский](#русский) · [English](#english)

---

<a id="русский"></a>

## Русский

Здесь нет ни одной команды. Это четыре реальных обращения к агенту «Геотехник Сурок»,
его ответы и файлы, которыми каждый ответ подкреплён.

Все ответы получены из репозитория (не «на словах»): запускались на чистом клоне,
вывод сохранён в [`examples/demo/`](https://github.com/sasha-sazonova/geotech-surok/tree/main/examples/demo).

### 1. «Фундамент 2,0 × 2,4 м, N = 1200 кН, суглинок φ = 16°, c = 18 кПа. Проходит?»

> **Бот:**
> Считаю по СП 22.13330.2016.
>
> | Показатель | Значение |
> |---|---|
> | Расчётное сопротивление R | **215,62 кПа** |
> | Среднее давление p | **286,00 кПа** |
> | Осадка s | **4,23 см** |
> | Сжимаемая толща Hc | **3,60 м** |
>
> **По несущей способности — не проходит:** p = 286,0 > R = 215,6 кПа, превышение **+32,6 %**.
> **По осадке — проходит:** 4,23 см ≤ 10 см (предел для ж/б каркаса, прил. Г).
>
> Фундамент нужно увеличивать. Если хотите, посчитаю вариант 2,4 × 2,8 м.

**Чем подкреплено**

| Файл | Что в нём |
|---|---|
| [examples/demo/01-d1-fail.txt](https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/examples/demo/01-d1-fail.txt) | полный вывод расчёта (этот ответ дословно) |
| [scenarios/d1-foundation.yaml](https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/scenarios/d1-foundation.yaml) | входные данные, которые бот принял |
| [calc/d1_foundation.py](https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/calc/d1_foundation.py) | формулы: R по п.5.6.7 ф.(5.7), осадка по ф.(5.16) |
| [traceability.yml](https://github.com/sasha-sazonova/geotech-surok/blob/main/traceability.yml) | привязка: пункт нормы → формула → код → тест |
| [docs/norm-sources/sp22-2016.md](https://github.com/sasha-sazonova/geotech-surok/blob/main/docs/norm-sources/sp22-2016.md) | сверка коэффициентов с официальным текстом СП |
| [docs/manual-check-d1.md](https://github.com/sasha-sazonova/geotech-surok/blob/main/docs/manual-check-d1.md) | независимый ручной пересчёт тех же чисел |

### 2. «А если 2,4 × 2,8 м?»

> **Бот:**
> Пересчитал с новой шириной и длиной.
>
> | Показатель | Было 2,0 × 2,4 | Стало 2,4 × 2,8 |
> |---|---|---|
> | R | 215,62 кПа | **218,82 кПа** |
> | p | 286,00 кПа | **214,57 кПа** |
> | Осадка s | 4,23 см | **3,60 см** |
> | Проверка p ≤ R | не проходит | **проходит** (запас 1,9 %) |
> | Проверка s ≤ 10 см | проходит | **проходит** |
>
> Оба условия выполнены. Запас по давлению небольшой — 1,9 %, при возможном росте нагрузки
> лучше заложить 2,7 × 3,0 м.

**Чем подкреплено:**
[examples/demo/02-d1-pass.txt](https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/examples/demo/02-d1-pass.txt),
[scenarios/d1-foundation-r2.yaml](https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/scenarios/d1-foundation-r2.yaml) —
та же цепочка норма → формула → код → тест, что и в первом ответе.

### 3. «Данных о грунте мало — только до 2 метров. Посчитаешь?»

> **Бот:**
> **Не посчитаю — и вот почему.**
>
> Для осреднения удельного веса по п.5.6.10 нужны данные на глубину z = b/2 = 3,0 м ниже
> подошвы, а у нас есть только 1,0 м. Подставлять нулевой вес вместо отсутствующего грунта
> нельзя — получилось бы занижение R.
>
> Что есть: осадка **0,66 см**, но граница сжимаемой толщи выходит за пределы данных,
> поэтому и она помечена как **«не определено»**.
>
> **Нужно:** описание грунта примерно до глубины d + 2b (для b = 6 м это ~13 м от поверхности),
> либо отчёт изысканий с ИГЭ до этой глубины.

**Чем подкреплено:**
[examples/demo/03-insufficient-data.txt](https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/examples/demo/03-insufficient-data.txt),
[calc/d1_foundation.py](https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/calc/d1_foundation.py) —
исключение `InsufficientData` и запись отказа в `refusals`; тест
[test_missing_soil_over_averaging_depth_is_refused](https://github.com/sasha-sazonova/geotech-surok/blob/main/tests/test_input_guards.py).

**Почему это важно:** система не выдаёт правдоподобное число там, где данных нет.
Такой отказ — штатный результат, а не сбой.

### 4. «Откос H = 10 м, заложение 1:2, φ = 25°, c = 10 кПа. Устойчив?»

> **Бот:**
> Проверил по круглоцилиндрической поверхности (центр 55,4; 61,0, R = 21,5 м):
>
> | Метод | Коэффициент устойчивости K |
> |---|---|
> | Fellenius (обычный метод срезов) | **1,590** |
> | Bishop (упрощённый) | **1,692** |
>
> Требуемый для сооружений I класса K ≥ 1,25–1,30. **Откос устойчив** с запасом ~30 %.
>
> Если нужен полный набор методов (Янбу, Corps of Engineers, Lowe–Karafiath, Spencer,
> Моргенштерн–Прайс) — они доступны, но требуют установки расчётного движка
> (`requirements-optional.txt`).

**Чем подкреплено:**
[examples/demo/04-slope.txt](https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/examples/demo/04-slope.txt),
[calc/b1_slope.py](https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/calc/b1_slope.py), сверка с внешним движком —
[docs/benchmarks/b1-slope.md](https://github.com/sasha-sazonova/geotech-surok/blob/main/docs/benchmarks/b1-slope.md)
(совпадение с xslope ≤ 0,02 %).

Команды и проверки повторяемости — отдельно, в
[docs/verify-step-by-step.md](https://github.com/sasha-sazonova/geotech-surok/blob/main/docs/verify-step-by-step.md).
Они нужны тем, кто хочет убедиться, что числа воспроизводятся, а не «нарисованы».

---

<a id="english"></a>

## English

No commands here. Four real requests to the Surok geotechnical agent, its answers, and the files
that back each answer.

Every answer below was produced from the repository, not written by hand: the runs were executed on
a clean clone and saved under
[`examples/demo/`](https://github.com/sasha-sazonova/geotech-surok/tree/main/examples/demo).

### 1. "Footing 2.0 × 2.4 m, N = 1200 kN, loam φ = 16°, c = 18 kPa. Does it pass?"

> **Agent:**
> Computing per SP 22.13330.2016 (Russian code; the abbreviation "СП" is kept as in the original).
>
> | Quantity | Value |
> |---|---|
> | Design resistance R | **215.62 kPa** |
> | Mean pressure p | **286.00 kPa** |
> | Settlement s | **4.23 cm** |
> | Compressible thickness Hc | **3.60 m** |
>
> **Bearing capacity — fails:** p = 286.0 > R = 215.6 kPa, exceeded by **+32.6 %**.
> **Settlement — passes:** 4.23 cm ≤ 10 cm (limit for an RC frame, appendix G).
>
> The footing has to grow. I can recalculate for 2.4 × 2.8 m.

**Backed by**

| File | Contents |
|---|---|
| [examples/demo/01-d1-fail.txt](https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/examples/demo/01-d1-fail.txt) | full run output (this answer verbatim) |
| [scenarios/d1-foundation.yaml](https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/scenarios/d1-foundation.yaml) | input data the agent accepted |
| [calc/d1_foundation.py](https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/calc/d1_foundation.py) | formulas: R by 5.6.7 (5.7), settlement by (5.16) |
| [traceability.yml](https://github.com/sasha-sazonova/geotech-surok/blob/main/traceability.yml) | clause → formula → code → test |
| [docs/norm-sources/sp22-2016.md](https://github.com/sasha-sazonova/geotech-surok/blob/main/docs/norm-sources/sp22-2016.md) | coefficients checked against the official code text |
| [docs/manual-check-d1.md](https://github.com/sasha-sazonova/geotech-surok/blob/main/docs/manual-check-d1.md) | independent manual recomputation of the same numbers |

### 2. "And for 2.4 × 2.8 m?"

> **Agent:**
> Recalculated with the new width and length.
>
> | Quantity | Before 2.0 × 2.4 | After 2.4 × 2.8 |
> |---|---|---|
> | R | 215.62 kPa | **218.82 kPa** |
> | p | 286.00 kPa | **214.57 kPa** |
> | Settlement s | 4.23 cm | **3.60 cm** |
> | Check p ≤ R | fails | **passes** (1.9 % margin) |
> | Check s ≤ 10 cm | passes | **passes** |
>
> Both conditions are met. The pressure margin is small — 1.9 %; if the load may grow, use 2.7 × 3.0 m.

**Backed by:**
[examples/demo/02-d1-pass.txt](https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/examples/demo/02-d1-pass.txt),
[scenarios/d1-foundation-r2.yaml](https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/scenarios/d1-foundation-r2.yaml) —
the same clause → formula → code → test chain as in the first answer.

### 3. "Soil data goes only to 2 m depth. Will you compute it?"

> **Agent:**
> **No — and here is why.**
>
> Averaging the unit weight per 5.6.10 needs data down to z = b/2 = 3.0 m below the footing base,
> while only 1.0 m is available. Substituting zero weight for the missing soil is not allowed —
> it would understate R.
>
> What is available: settlement **0.66 cm**, but the compressible-thickness boundary falls outside
> the data, so that too is marked **"not determined"**.
>
> **Needed:** a soil description down to about d + 2b (for b = 6 m that is ~13 m below surface),
> or a investigation report with soil units to that depth.

**Backed by:**
[examples/demo/03-insufficient-data.txt](https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/examples/demo/03-insufficient-data.txt),
[calc/d1_foundation.py](https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/calc/d1_foundation.py) —
the `InsufficientData` exception and the refusal recorded in `refusals`; test
[test_missing_soil_over_averaging_depth_is_refused](https://github.com/sasha-sazonova/geotech-surok/blob/main/tests/test_input_guards.py).

**Why it matters:** the system never returns a plausible number where data is missing.
Such a refusal is a normal result, not a failure.

### 4. "Slope H = 10 m, 1:2 batter, φ = 25°, c = 10 kPa. Is it stable?"

> **Agent:**
> Checked on a circular slip surface (centre 55.4; 61.0, R = 21.5 m):
>
> | Method | Factor of safety K |
> |---|---|
> | Fellenius (ordinary method of slices) | **1.590** |
> | Bishop (simplified) | **1.692** |
>
> The requirement for class I structures is K ≥ 1.25–1.30. **The slope is stable** with ~30 % margin.
>
> The full method set (Janbu, Corps of Engineers, Lowe–Karafiath, Spencer, Morgenstern–Price)
> is available as well, but requires the optional solver package (`requirements-optional.txt`).

**Backed by:**
[examples/demo/04-slope.txt](https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/examples/demo/04-slope.txt),
[calc/b1_slope.py](https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/calc/b1_slope.py), cross-checked against an external engine —
[docs/benchmarks/b1-slope.md](https://github.com/sasha-sazonova/geotech-surok/blob/main/docs/benchmarks/b1-slope.md)
(agreement with xslope ≤ 0.02 %).

Commands and reproducibility checks are kept separately in
[docs/verify-step-by-step.md](https://github.com/sasha-sazonova/geotech-surok/blob/main/docs/verify-step-by-step.md).
They are for those who want to make sure the numbers reproduce rather than being drawn by hand.
