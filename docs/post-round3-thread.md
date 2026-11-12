# Round 3 — готовый тред для X

Трек: **Open Creation**. Публикуется до формы. В первом посте — упоминание и хештег.
Правила: не публиковать email, пост остаётся публичным до конца проверки.

---

## 1/6 — контекст

Most calculation tools answer every question with a number. Ours answers "not determined" when the data or a verified code edition is missing — and that is the feature engineers ask for first.

A geotechnical calculation agent built with @AutoClawAIer 🧵

#BuiltWithAutoClaw

## 2/6 — процесс

Inside: a normative registry (9 confirmed documents, 11 queued), 105 pinned packages, async compute jobs and 179 tests. Every number resolves to clause → formula → code → test, and a missing link blocks the result instead of guessing.

## 3/6 — результат D1

Case D1 — footing 2.0×2.4 m, N = 1200 kN, silty clay φ=16°, c=18 kPa:
R = 215.62 kPa vs p = 286.00 kPa → fails by 32.6%
s = 4.23 cm ≤ 10 cm → passes
Resized to 2.4×2.8 m: R = 218.82 vs p = 214.57 → passes with 1.9% margin.

## 4/6 — результат D2

Case D2 — laterally loaded pile D=1.2 m, L=24 m:
independent FEM solver vs exact beam theory: 0.09% (deflection) and 0.1% (moment);
vs OpenPile: +4.5% and +10.1%, within the declared ±8/±12%.
SP 24 defines no p-y procedure, so the normative status stays "not determined".

## 5/6 — уроки, часть 1

What we learned building this in OpenClaw:
1. Write the contract, not the prompt — if a rule can't be checked, the agent won't follow it.
2. Freeze the environment before the first calculation, not after.
3. Make "refused" a first-class result and test it like a happy path.

## 6/6 — уроки, часть 2

4. One implementation is not a verification — build a second, independent one.
5. Sync one way only: repo → agent. The live workspace lags, and a backwards sync overwrites published work.

Code, decks and demo: https://github.com/sasha-sazonova/geotech-surok
