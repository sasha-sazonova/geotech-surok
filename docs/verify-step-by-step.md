# Пошаговая проверка: как убедиться, что расчёты воспроизводятся

**Язык:** [Русский](#русский) · [English](#english)

---

<a id="русский"></a>

## Русский

Для тех, кто хочет проверить сам — от установки до сверки чисел. Занимает **около 3 минут**
на чистой машине. Все команды копируются как есть.

### Шаг 0. Что нужно

- Python 3.9 или новее (`python3 --version`)
- git
- ~400 МБ свободного места (ядро ~200 МБ, с движками ~750 МБ)

Ничего больше устанавливать не требуется: все зависимости ставятся из
зафиксированного списка `requirements.lock`.

**Debian/Ubuntu:** если `python3 -m venv` жалуется на `ensurepip`, доставьте пакет:

```bash
sudo apt install python3-venv
```

### Шаг 1. Скачать проект

```bash
git clone https://github.com/sasha-sazonova/geotech-surok.git
cd geotech-surok
```

### Шаг 2. Поставить всё одной командой

```bash
./install.sh                  # ядро: СП 22 + СП 24
./install.sh --with-engines   # плюс движки: 7 методов откосов и подпорные стены
```

Скрипт проверит Python и свободное место, создаст `.venv`, поставит зависимости,
прогонит валидатор и тесты.

### Шаг 3. Либо то же вручную

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows (Git Bash): source .venv/Scripts/activate
pip install -r requirements.lock
```

### Шаг 4. Прогнать проверки

```bash
make verify
```

Ожидаемый вывод:

```
TRACEABILITY: OK (30 clauses, 147 tests)
177 passed
```

Если `make` нет (Windows, минимальные образы) — те же две проверки напрямую:

```bash
python tools/validate_traceability.py
python -m pytest -q
```

### Шаг 5. Повторить расчёт из демо

```bash
make scenario SCENARIO=scenarios/d1-foundation.yaml
```

Сверьте с
[examples/demo/01-d1-fail.txt](https://github.com/sasha-sazonova/geotech-surok/blob/main/examples/demo/01-d1-fail.txt):

```
R = 215.62 кПа   p = 286.00 кПа   s = 4.23 см
p_le_R → не выполняется
```

Числа должны совпасть **до второго знака**. Если не совпали — пришлите вывод,
это повод разбираться, а не «списать на округление».

### Шаг 6. Проверить, что движки тоже работают (необязательно)

Полный набор: 7 методов устойчивости откосов и проверки подпорных стен.

```bash
pip install -r requirements-optional.txt
python -m pytest -q -rs
```

Ожидаемо: **177 passed, 0 skipped**. Если появятся `skipped` — значит движки не
установились, и интеграционные тесты не выполнялись.

### Шаг 7. Сверить нормативную базу

Все документы, по которым считает система, перечислены с датой и источником:

- список: [docs/norms-queue.md](https://github.com/sasha-sazonova/geotech-surok/blob/main/docs/norms-queue.md)
- контрольные суммы PDF: [docs/norms-manifest.sha256](https://github.com/sasha-sazonova/geotech-surok/blob/main/docs/norms-manifest.sha256)
- сверка коэффициентов СП 22: [docs/norm-sources/sp22-2016.md](https://github.com/sasha-sazonova/geotech-surok/blob/main/docs/norm-sources/sp22-2016.md)

```bash
shasum -a 256 -c docs/norms-manifest.sha256      # на Linux: sha256sum -c
```

### Что проверить особенно

| Вопрос | Где смотреть |
|---|---|
| Формулы — из нормы, а не «по памяти»? | [traceability.yml](https://github.com/sasha-sazonova/geotech-surok/blob/main/traceability.yml): каждый пункт → код → тест |
| Числа не подогнаны? | [docs/manual-check-d1.md](https://github.com/sasha-sazonova/geotech-surok/blob/main/docs/manual-check-d1.md): ручной пересчёт |
| Движки не врут? | [docs/benchmarks/](https://github.com/sasha-sazonova/geotech-surok/tree/main/docs/benchmarks): сверка с xslope и pyslope |
| А где система отказывается считать? | [docs/status.md](https://github.com/sasha-sazonova/geotech-surok/blob/main/docs/status.md): раздел «что осознанно не считается» |
| А были ли ошибки? | [docs/self-audit-2026-11-05.md](https://github.com/sasha-sazonova/geotech-surok/blob/main/docs/self-audit-2026-11-05.md): 10 найденных дефектов, включая два ложных «зелёных» статуса |

### Если что-то пошло не так

| Симптом | Причина | Решение |
|---|---|---|
| `No module named 'yaml'` | окружение не активировано | `source .venv/bin/activate` |
| `No module named 'calc'` | запуск не из корня проекта | `cd geotech-surok` |
| `make: command not found` | нет make | команды из шага 4 напрямую |
| тесты `skipped` | не поставлены движки | `pip install -r requirements-optional.txt` |
| `ensurepip is not available` | Debian без `python3-venv` | `sudo apt install python3-venv` |

---

<a id="english"></a>

## English

For those who want to verify the numbers themselves — from install to reproducing the values.
Takes **about 3 minutes** on a clean machine. Every command can be copied as is.

### Step 0. What you need

- Python 3.9 or newer (`python3 --version`)
- git
- ~400 MB free space (core ~200 MB, with engines ~750 MB)

Nothing else: all dependencies come from the pinned `requirements.lock`.

**Debian/Ubuntu:** if `python3 -m venv` complains about `ensurepip`, install the package:

```bash
sudo apt install python3-venv
```

### Step 1. Get the project

```bash
git clone https://github.com/sasha-sazonova/geotech-surok.git
cd geotech-surok
```

### Step 2. Install everything with one command

```bash
./install.sh                  # core: SP 22 + SP 24
./install.sh --with-engines   # plus engines: 7 slope methods and retaining walls
```

The script checks Python and free space, creates `.venv`, installs dependencies and runs the
validator plus the test suite.

### Step 3. Or do the same manually

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows (Git Bash): source .venv/Scripts/activate
pip install -r requirements.lock
```

### Step 4. Run the checks

```bash
make verify
```

Expected:

```
TRACEABILITY: OK (30 clauses, 147 tests)
177 passed
```

No `make`? Run the two checks directly:

```bash
python tools/validate_traceability.py
python -m pytest -q
```

### Step 5. Reproduce the demo calculation

```bash
make scenario SCENARIO=scenarios/d1-foundation.yaml
```

Compare with
[examples/demo/01-d1-fail.txt](https://github.com/sasha-sazonova/geotech-surok/blob/main/examples/demo/01-d1-fail.txt):

```
R = 215.62 kPa   p = 286.00 kPa   s = 4.23 cm
p_le_R → fails
```

The numbers must match **to the second decimal**. If they do not, send the output — that is a reason
to investigate, not something to explain away as rounding.

### Step 6. Verify the engines (optional)

Full set: seven slope-stability methods and retaining-wall checks.

```bash
pip install -r requirements-optional.txt
python -m pytest -q -rs
```

Expected: **177 passed, 0 skipped**. If you see `skipped`, the engines did not install and the
integration tests did not run.

### Step 7. Check the normative base

Every document the system relies on is listed with a date and a source:

- list: [docs/norms-queue.md](https://github.com/sasha-sazonova/geotech-surok/blob/main/docs/norms-queue.md)
- PDF checksums: [docs/norms-manifest.sha256](https://github.com/sasha-sazonova/geotech-surok/blob/main/docs/norms-manifest.sha256)
- SP 22 coefficient verification: [docs/norm-sources/sp22-2016.md](https://github.com/sasha-sazonova/geotech-surok/blob/main/docs/norm-sources/sp22-2016.md)

```bash
shasum -a 256 -c docs/norms-manifest.sha256      # Linux: sha256sum -c
```

### What to look at in particular

| Question | Where |
|---|---|
| Are the formulas taken from the code, not memory? | [traceability.yml](https://github.com/sasha-sazonova/geotech-surok/blob/main/traceability.yml): clause → code → test |
| Are the numbers not fudged? | [docs/manual-check-d1.md](https://github.com/sasha-sazonova/geotech-surok/blob/main/docs/manual-check-d1.md): manual recomputation |
| Do the engines agree? | [docs/benchmarks/](https://github.com/sasha-sazonova/geotech-surok/tree/main/docs/benchmarks): cross-checks against xslope and pyslope |
| Where does the system refuse to compute? | [docs/status.md](https://github.com/sasha-sazonova/geotech-surok/blob/main/docs/status.md): "deliberately not computed" |
| Have there been defects? | [docs/self-audit-2026-11-05.md](https://github.com/sasha-sazonova/geotech-surok/blob/main/docs/self-audit-2026-11-05.md): 10 defects found, including two false green statuses |

### Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `No module named 'yaml'` | environment not activated | `source .venv/bin/activate` |
| `No module named 'calc'` | not run from the project root | `cd geotech-surok` |
| `make: command not found` | no make | use the commands from step 4 directly |
| tests `skipped` | engines not installed | `pip install -r requirements-optional.txt` |
| `ensurepip is not available` | Debian without `python3-venv` | `sudo apt install python3-venv` |
