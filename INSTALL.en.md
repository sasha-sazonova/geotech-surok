# Install and run your first calculation

Verified on a clean machine: macOS, Python 3.9.6, install from scratch took **27 seconds**,
after which `make verify` reported **65 passed**.

You need nothing but Python and git. Docker is optional.

---

## 1. Requirements

| Requirement | Minimum | Verified on |
|---|---|---|
| Python | **3.9** | 3.9.6 (macOS), 3.12 (CI, Docker) |
| git | any | 2.x |
| OS | macOS, Linux, Windows (WSL or Git Bash) | macOS 14, Ubuntu 24.04 |
| Docker | optional | only for the clean-machine check |

```bash
python3 --version
```

---

## 2. Install (macOS / Linux)

```bash
git clone https://github.com/sasha-sazonova/geotech-surok.git
cd geotech-surok
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.lock
```

---

## 3. Verify

```bash
make verify
```

Expected:

```
TRACEABILITY: OK (12 clauses, 39 tests)
65 passed
```

No `make`? Run the same two checks directly:

```bash
python tools/validate_traceability.py
python -m pytest -q
```

---

## 4. First calculation

```bash
python examples/quickstart_d1.py
```

Expected output: R = 215.62 kPa, p = 286.0 kPa, s = 4.232 cm, Hc = 3.6 m, with two check statuses.

To run your own case, edit the numbers in the `ВАШИ ДАННЫЕ` block at the top of
`examples/quickstart_d1.py`. Normative coefficients (tables 5.4 / 5.5 / 5.8, averaging depth,
compressible-thickness boundary) are handled by the library.

**"Not determined" is a valid result.** The system says so when input data is missing or a norm
cell is unverified. It is not a failure and must not be "adjusted" into a number.

---

## 5. Docker (no local install)

```bash
docker build -t geotech-surok .
docker run --rm geotech-surok
```

---

## 6. Windows

Use **WSL** (recommended) or **Git Bash**; activate with `source .venv/Scripts/activate`.
`make` is usually absent — use the direct commands from section 3.

---

## 7. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `No module named 'yaml'` | venv not activated / deps missing | `source .venv/bin/activate && pip install -r requirements.lock` |
| `No module named 'calc'` | not run from repo root | `cd geotech-surok` |
| `make: command not found` | no make | run `python -m pytest -q` directly |
| `command not found: python` | only `python3` present | use `python3` |
| `test_units.py` fails | broken Pint install | `pip install --force-reinstall Pint==0.24.4` |
