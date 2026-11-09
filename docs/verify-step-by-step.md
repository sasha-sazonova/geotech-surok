# Пошаговая проверка: как убедиться, что расчёты воспроизводятся

Для тех, кто хочет проверить сам — от установки до сверки чисел. Занимает **около 3 минут**
на чистой машине. Все команды копируются как есть.

---

## Шаг 0. Что нужно

- Python 3.9 или новее (`python3 --version`)
- git
- ~200 МБ свободного места

Ничего больше устанавливать не требуется: все зависимости ставятся из
зафиксированного списка `requirements.lock`.

**Debian/Ubuntu:** если `python3 -m venv` жалуется на `ensurepip`, доставьте пакет:

```bash
sudo apt install python3-venv
```

---

## Шаг 1. Скачать проект

```bash
git clone https://github.com/sasha-sazonova/geotech-surok.git
cd geotech-surok
```

---

## Шаг 2. Создать окружение

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows (Git Bash): source .venv/Scripts/activate
```

---

## Шаг 3. Поставить зависимости

```bash
pip install -r requirements.lock
```

Занимает 20–40 секунд. Версии зафиксированы — результат не зависит от дня установки.

---

## Шаг 4. Прогнать проверки

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

---

## Шаг 5. Повторить расчёт из демо

```bash
make scenario SCENARIO=scenarios/d1-foundation.yaml
```

Сверьте с [`examples/demo/01-d1-fail.txt`](../examples/demo/01-d1-fail.txt):

```
R = 215.62 кПа   p = 286.00 кПа   s = 4.23 см
p_le_R → не выполняется
```

Числа должны совпасть **до второго знака**. Если не совпали — пришлите вывод,
это повод разбираться, а не «списать на округление».

---

## Шаг 6. Проверить, что движки тоже работают (необязательно)

Полный набор: 7 методов устойчивости откосов и проверки подпорных стен.

```bash
pip install -r requirements-optional.txt
python -m pytest -q -rs
```

Ожидаемо: **177 passed, 0 skipped**. Если появятся `skipped` — значит движки не
установились, и интеграционные тесты не выполнялись (именно этот случай ловит
CI-задача `optional`).

---

## Шаг 7. Сверить нормативную базу

Все документы, по которым считает система, перечислены с датой и источником:

- список: [`docs/norms-queue.md`](norms-queue.md)
- контрольные суммы PDF: [`docs/norms-manifest.sha256`](norms-manifest.sha256)
- сверка коэффициентов СП 22: [`docs/norm-sources/sp22-2016.md`](norm-sources/sp22-2016.md)

```bash
shasum -a 256 -c docs/norms-manifest.sha256      # на Linux: sha256sum -c
```

---

## Что проверить особенно

| Вопрос | Где смотреть |
|---|---|
| Формулы — из нормы, а не «по памяти»? | [`traceability.yml`](../traceability.yml): каждый пункт → код → тест |
| Числа не подогнаны? | [`docs/manual-check-d1.md`](manual-check-d1.md): ручной пересчёт |
| Движки не врут? | [`docs/benchmarks/`](benchmarks/): сверка с xslope и pyslope |
| А где система отказывается считать? | [`docs/status.md`](status.md): раздел «что осознанно не считается» |
| А были ли ошибки? | [`docs/self-audit-2026-11-05.md`](self-audit-2026-11-05.md): 10 найденных дефектов, включая два ложных «зелёных» статуса |

---

## Если что-то пошло не так

| Симптом | Причина | Решение |
|---|---|---|
| `No module named 'yaml'` | окружение не активировано | `source .venv/bin/activate` |
| `No module named 'calc'` | запуск не из корня проекта | `cd geotech-surok` |
| `make: command not found` | нет make | команды из шага 4 напрямую |
| тесты `skipped` | не поставлены движки | `pip install -r requirements-optional.txt` |
| `ensurepip is not available` | Debian без `python3-venv` | `sudo apt install python3-venv` |
