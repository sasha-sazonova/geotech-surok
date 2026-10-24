# -*- coding: utf-8 -*-
"""Страница возможностей Сурка + отдельный раздел сравнения с GEO5 (RU/EN)."""
import html, pathlib

# ---------------------------------------------------------------- возможности
# (номер, заголовок_ru, заголовок_en, что_делаем_ru, что_делаем_en, основа_ru, основа_en, проверка_ru, проверка_en)
CAPS = [
 ("01","Несущая способность и осадка фундамента","Bearing resistance and settlement",
  "Считает среднее давление под подошвой, несущую способность R и осадку послойным суммированием. Возвращает статус каждой проверки, а не одно число.",
  "Computes average pressure under the footing, bearing resistance R and settlement by layer-by-layer summation. Returns a status per check, not a single number.",
  "СП 22.13330.2016: п.5.6.7 ф.(5.7), табл.5.4/5.5; п.5.6.10; п.5.6.31 ф.(5.16); п.5.6.32 ф.(5.17), табл.5.8; п.5.6.41; прил. Г табл. Г.1",
  "SP 22.13330.2016: clause 5.6.7 (5.7), tables 5.4/5.5; 5.6.10; 5.6.31 (5.16); 5.6.32 (5.17), table 5.8; 5.6.41; appendix G, table G.1",
  "Эталон D1: p = 286.0 кПа против R = 215.62 кПа — «не выполняется» (+32.6%); осадка s = 4.232 см ≤ su = 10 см — «выполняется» (Hc = 3.6 м); ручной пересчёт закреплён тестом",
  "Benchmark D1: p = 286.0 kPa vs R = 215.62 kPa — fails (+32.6%); settlement s = 4.232 cm ≤ su = 10 cm — passes (Hc = 3.6 m); pinned by a manual reference test"),
 ("02","Устойчивость откосов","Slope stability",
  "Считает коэффициент запаса семью методами LEM, строит поверхности скольжения и сверяет результат вторым инструментом. Для скальных откосов — кинематический анализ.",
  "Computes the factor of safety with seven LEM methods, builds slip surfaces and cross-checks with a second tool. For rock slopes — kinematic analysis.",
  "СП 22.13330.2016; СП 116.13330 — в очереди на подтверждение редакции",
  "SP 22.13330.2016; SP 116.13330 is queued for edition confirmation",
  "xslope 1.0.5 (7 методов) + pyslope 1.4.0; расхождение сверх допуска останавливает расчёт",
  "xslope 1.0.5 (7 methods) + pyslope 1.4.0; a discrepancy beyond tolerance stops the run"),
 ("03","Давление грунта и подпорные стены","Earth pressure and retaining walls",
  "Считает активное и пассивное давление по Ренкину и Кулону, проверяет сдвиг, опрокидывание и общую устойчивость стены.",
  "Computes active and passive pressure by Rankine and Coulomb, checks sliding, overturning and overall stability.",
  "СП 542.1325800.2024 с Изм. 1; СП 22.13330.2016",
  "SP 542.1325800.2024 with amendment 1; SP 22.13330.2016",
  "geoeq (Ренкин/Кулон), anaStruct для стены; реестр норм подтверждает редакции",
  "geoeq (Rankine/Coulomb), anaStruct for the wall; the registry confirms editions"),
 ("04","Сваи под вертикальной и горизонтальной нагрузкой","Piles under axial and lateral load",
  "Строит балочно-свайную модель с грунтовыми пружинами, считает усилия и перемещения, сравнивает с независимым решением. Осевую способность по CPT оценивает через De Beer.",
  "Builds a beam-pile model with soil springs, computes forces and displacements, compares with an independent solution. Axial capacity from CPT via De Beer.",
  "СП 24.13330.2021 с Изм. 1 и 2 — реестр подтверждён; прямого OSS-модуля СП 24 нет, результат несёт ограничение",
  "SP 24.13330.2021 with amendments 1 and 2 — registry confirmed; there is no direct OSS module for SP 24, so the result carries a limitation",
  "OpenPile 1.0.3, groundhog / methodedebeer; сценарий D2 — свая D = 1.2 м, L = 24 м",
  "OpenPile 1.0.3, groundhog / methodedebeer; scenario D2 — pile D = 1.2 m, L = 24 m"),
 ("05","Изыскания и параметры грунта","Site investigation and soil parameters",
  "Читает GEF/CPT и AGS4, разбирает скважины и SPT, считает статистику по ГОСТ 20522 и собирает паспорт параметра: значение, ИГЭ, проба, протокол, метод обработки.",
  "Reads GEF/CPT and AGS4, parses boreholes and SPT, runs statistics per GOST 20522 and assembles a parameter passport: value, soil unit, sample, test, processing method.",
  "ГОСТ 20522-2012 с Изм. 1; ГОСТ 25100 — в очереди, классификация помечается",
  "GOST 20522-2012 with amendment 1; GOST 25100 is queued, classification is flagged",
  "pygef, groundhog, python-ags4, geolysis; импорт-тест контура 21/21",
  "pygef, groundhog, python-ags4, geolysis; contour import test 21/21"),
 ("06","Протокол и трассируемость","Report and traceability",
  "Собирает протокол, в котором у каждого числа есть пункт нормы, редакция, формула с подстановкой и статус проверки. Отдельно — таблица трассируемости для эксперта.",
  "Builds a report where every number carries a clause, an edition, a formula with substituted values and a check status. A separate traceability table for the reviewer.",
  "СП 22, СП 24, СП 542, СП 248, СП 47, СП 446, ГОСТ 20522, ГОСТ Р 21.101-2026, ПП РФ № 87",
  "SP 22, SP 24, SP 542, SP 248, SP 47, SP 446, GOST 20522, GOST R 21.101-2026, RF Government Decree 87",
  "reports/d1-foundation-v2: протокол и таблица трассируемости по каждому пункту",
  "reports/d1-foundation-v2: report and traceability table clause by clause"),
 ("07","Воспроизводимость расчёта","Reproducibility",
  "Считает в замороженном окружении на вычислительном узле: задание, статус, результат, контрольные суммы. Три повтора — дальше честное «расчёта нет».",
  "Runs in a frozen environment on a compute node: job, status, result, checksums. Three retries, then an honest “no result”.",
  "Freeze контура: 105 пакетов, Python 3.12.3; свайный контур отдельно",
  "Contour freeze: 105 packages, Python 3.12.3; the pile contour is separate",
  "6/6 приёмочных проверок живого агента, включая ловушку анти-фоллбэка",
  "6/6 acceptance checks of the live agent, including the anti-fallback trap"),
]

# ---------------------------------------------------------------- сравнение
ROWS = [
 ("Подпорные стены","Retaining walls","Уголковая стена","Cantilever wall","partial",
  "Давление грунта и проверки устойчивости есть; полного модуля стены с этапностью нет.",
  "Earth pressure and stability checks exist; no full wall module with staged construction."),
 ("Подпорные стены","Retaining walls","Гравитационная стена","Gravity wall","partial",
  "Давление и устойчивость считаются; специфических проверок гравитационной стены нет.",
  "Pressure and stability are computed; gravity-wall specific checks are missing."),
 ("Подпорные стены","Retaining walls","Армированные насыпи","Reinforced embankments","none",
  "Армирование и нагели вне контура.",
  "Reinforcement and nails are outside the contour."),
 ("Подпорные стены","Retaining walls","Габионы","Gabions","none",
  "Габионных стен по СП в open-source нет — заявленный пробел.",
  "No gabion walls per SP in open source — a declared gap."),
 ("Подпорные стены","Retaining walls","Армированная стена","Reinforced wall","none",
  "Нет модуля армирования; давление грунта доступно как вход.",
  "No reinforcement module; earth pressure is available as input."),
 ("Подпорные стены","Retaining walls","Стена Redi-Rock","Redi-Rock wall","none",
  "Каталоги блоков производителя вне контура.",
  "Vendor block catalogues are outside the contour."),
 ("Подпорные стены","Retaining walls","Сборная стена","Precast wall","none",
  "Нет библиотеки сборных элементов и проверок узлов.",
  "No precast library or joint checks."),
 ("Подпорные стены","Retaining walls","Нагельное крепление","Soil nailing","none",
  "Нагели и выдёргивание не реализованы.",
  "Nails and pull-out are not implemented."),
 ("Подпорные стены","Retaining walls","Стабилизирующая свая","Stabilising pile","none",
  "Нет модели свая-грунт для стабилизации откоса.",
  "No pile-soil model for slope stabilisation."),
 ("Подпорные стены","Retaining walls","Давление грунта","Earth pressure","full",
  "Ренкин и Кулон реализованы, используются как вход для стен и откосов.",
  "Rankine and Coulomb implemented, used as input for walls and slopes."),
 ("Устойчивость откосов","Slope stability","Устойчивость откоса","Slope stability","partial",
  "7 методов LEM и сверка вторым инструментом; нет Шахунянца и армирования.",
  "7 LEM methods and cross-check; no Shakhunyants method or reinforcement."),
 ("Устойчивость откосов","Slope stability","Устойчивость откоса – Фильтрация","Slope stability – seepage","partial",
  "Фильтрация через ogs/Kratos, без геотехнического препроцессора.",
  "Seepage via ogs/Kratos, without a geotechnical preprocessor."),
 ("Устойчивость откосов","Slope stability","Скальный откос","Rock slope","partial",
  "Кинематический анализ через mplstereonet; прочность массива — нет.",
  "Kinematic analysis via mplstereonet; rock-mass strength is missing."),
 ("Фундаменты","Foundations","Отдельные фундаменты","Spread footing","partial",
  "R и осадка реализованы и проверены; момент, крен и краевые давления — «не определено».",
  "R and settlement implemented and checked; moment, tilt and edge pressure — not determined."),
 ("Фундаменты","Foundations","Отдельные фундаменты CPT","Spread footing from CPT","partial",
  "CPT читается, но маршрут «фундамент по CPT» в коде не реализован.",
  "CPT is read, but the CPT-based footing route is not implemented."),
 ("Фундаменты","Foundations","Осадка","Settlement","full",
  "Послойное суммирование по СП 22 прил. Г реализовано и проверено в D1.",
  "Layer-by-layer summation per SP 22 Appendix G implemented and checked in D1."),
 ("Фундаменты","Foundations","Плита","Slab","partial",
  "Плита считается, но не на грунтовом основании с СП-проверками.",
  "Slab is computed, but not on soil with SP checks."),
 ("Фундаменты","Foundations","Балка","Beam","partial",
  "Балка есть; основание — через коэффициенты постели вручную.",
  "Beam exists; soil support via manual subgrade moduli."),
 ("Фундаменты","Foundations","Устой","Abutment","none",
  "Модуля устоя нет.",
  "No abutment module."),
 ("Фундаменты","Foundations","Сваи","Piles","partial",
  "Балочно-свайные модели и пружины; нормативного маршрута СП 24 в OSS нет.",
  "Beam-pile models and springs; no SP 24 normative route in OSS."),
 ("Фундаменты","Foundations","Микросвая","Micropile","none",
  "Микросвай нет.",
  "Micropiles are absent."),
 ("Фундаменты","Foundations","Куст свай","Pile group","none",
  "Куст и групповая эффективность не реализованы.",
  "Pile group and efficiency are not implemented."),
 ("Фундаменты","Foundations","Свая CPT","Pile from CPT","partial",
  "De Beer по CPT как метод, не как СП-маршрут.",
  "De Beer from CPT as a method, not as an SP route."),
 ("МКЭ","FEM","МКЭ","FEM","partial",
  "OpenSees/Kratos/Code_Aster есть; Hardening Soil «из коробки» нет.",
  "OpenSees/Kratos/Code_Aster available; no Hardening Soil out of the box."),
 ("МКЭ","FEM","МКЭ – Тоннель","FEM – tunnel","none",
  "Шаблонов тоннеля и этапов проходки нет.",
  "No tunnel templates or stages."),
 ("МКЭ","FEM","МКЭ – Консолидация","FEM – consolidation","partial",
  "Консолидация в общей постановке, готового модуля нет.",
  "Consolidation in a general formulation, no ready module."),
 ("МКЭ","FEM","МКЭ – Фильтрация","FEM – seepage","partial",
  "Фильтрация считается; препроцессинга и типовых ГУ нет.",
  "Seepage is computed; no preprocessing or standard BCs."),
 ("МКЭ","FEM","МКЭ – Землетрясение","FEM – earthquake","partial",
  "Динамика есть; проверок по СП 14.13330 нет.",
  "Dynamics exist; no SP 14.13330 checks."),
 ("Ограждения котлованов","Excavation support","Ограждение котлованов – анализ","Excavation analysis","none",
  "Полного сценария «выемка по стадиям → анкеры → распорки» нет.",
  "No full staged excavation scenario with anchors and struts."),
 ("Ограждения котлованов","Excavation support","Ограждение котлованов – проект","Excavation design","none",
  "Проектирования ограждения нет.",
  "No support-system design."),
 ("Тоннели","Tunnels","Шахта","Shaft","none",
  "Шахта и крепь не реализованы.",
  "Shaft and lining are not implemented."),
 ("Тоннели","Tunnels","Выработка","Underground opening","none",
  "Только общее МКЭ-ядро, без шаблонов.",
  "General FEM core only, without templates."),
 ("Изыскания","Site investigation","Стратиграфия","Stratigraphy","partial",
  "Геомодель строится, но не как единый источник расчёта.",
  "A geomodel is built, but not as a single calculation source."),
 ("Изыскания","Site investigation","Стратиграфия – Земляные работы","Stratigraphy – earthworks","none",
  "Ведомостей земляных работ нет.",
  "No earthworks quantities."),
 ("Изыскания","Site investigation","Стратиграфия – Резервы","Stratigraphy – volumes","none",
  "Подсчёта объёмов нет.",
  "No volume calculation."),
 ("Изыскания","Site investigation","Стратиграфия – Таблицы","Stratigraphy – tables","partial",
  "Таблицы слоёв ведутся вручную, экспорт через сценарий.",
  "Layer tables are manual, export via scenario."),
 ("Изыскания","Site investigation","Лаборатория","Laboratory","partial",
  "Лабораторные данные обрабатываются; PMT/DMT нет.",
  "Lab data is processed; PMT/DMT is missing."),
 ("Изыскания","Site investigation","Облако точек","Point cloud","partial",
  "Облака читаются, геотехнической интерпретации нет.",
  "Point clouds are read; no geotechnical interpretation."),
 ("Изыскания","Site investigation","Data Collector","Data Collector","none",
  "Мобильного сбора данных нет.",
  "No mobile data collection."),
]

CAT_ORDER = ["Подпорные стены","Устойчивость откосов","Фундаменты","МКЭ","Ограждения котлованов","Тоннели","Изыскания"]
CAT_EN = {"Подпорные стены":"Retaining walls","Устойчивость откосов":"Slope stability","Фундаменты":"Foundations",
          "МКЭ":"FEM","Ограждения котлованов":"Excavation support","Тоннели":"Tunnels","Изыскания":"Site investigation"}

counts = {"full":0,"partial":0,"none":0}
for r in ROWS: counts[r[4]] += 1

CSS = """
:root{--paper:#F4F2EC;--ink:#101113;--muted:#5F6270;--line:rgba(16,17,19,.14);--accent:#1236B8;--mono:"SF Mono",Menlo,Consolas,monospace}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none;border-bottom:1px solid rgba(18,54,184,.3)}
.wrap{max-width:1120px;margin:0 auto;padding:0 5vw}
.top{display:flex;flex-wrap:wrap;justify-content:space-between;gap:8px 18px;padding:22px 0;border-bottom:1px solid var(--line);font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.hero{padding:8vh 0 5vh;border-bottom:1px solid var(--line)}
.kicker{font-family:var(--mono);font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:var(--accent);margin:0 0 16px}
h1{font-size:clamp(38px,6vw,76px);line-height:.92;letter-spacing:-.04em;margin:0 0 18px;font-weight:600}
.lead{font-size:clamp(17px,1.9vw,22px);line-height:1.4;max-width:34em;margin:0 0 14px}
.sub{font-size:15px;line-height:1.6;color:var(--muted);max-width:46em;margin:0}
.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:1px;background:var(--line);border:1px solid var(--line);margin:26px 0 0}
.metric{background:var(--paper);padding:18px 20px}
.metric b{display:block;font-size:32px;letter-spacing:-.03em;line-height:1}
.metric span{font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);display:block;margin-top:6px}
section{padding:6vh 0;border-top:1px solid var(--line)}
h2{font-size:clamp(22px,3vw,32px);letter-spacing:-.02em;margin:0 0 10px}
h3{font-size:15px;margin:26px 0 8px;font-family:var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--muted);font-weight:400}
.cap{border:1px solid var(--line);padding:20px 20px 18px;margin-bottom:14px}
.cap h4{margin:0 0 8px;font-size:19px;letter-spacing:-.01em}
.cap p{margin:0 0 8px;font-size:14.5px;line-height:1.6}
.cap .kv{font-family:var(--mono);font-size:11.5px;line-height:1.6;color:var(--muted)}
.cap .kv b{color:var(--ink);font-weight:600}
.num{font-family:var(--mono);font-size:10px;letter-spacing:.18em;color:var(--accent);display:block;margin-bottom:8px}
table{border-collapse:collapse;width:100%;font-size:14px;margin-top:8px}
th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-family:var(--mono);font-size:10px;letter-spacing:.13em;text-transform:uppercase;color:var(--muted);font-weight:400}
td.s{white-space:nowrap;font-family:var(--mono);font-size:11px;letter-spacing:.06em}
.full{color:#0B7A5A}.partial{color:#9A6A00}.none{color:#9B2C2C}
.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;margin-top:18px}
.card{border:1px solid var(--line);padding:18px}
.card h4{margin:0 0 8px;font-size:16px}
.card p{margin:0;font-size:14px;line-height:1.55;color:#33343A}
.foot{border-top:1px solid var(--line);padding:22px 0 40px;font-family:var(--mono);font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
"""

def rows_for(cat_ru, lang):
    out=[]
    for c_ru,c_en,m_ru,m_en,st,note_ru,note_en in ROWS:
        if c_ru!=cat_ru: continue
        name = m_ru if lang=='ru' else m_en
        note = note_ru if lang=='ru' else note_en
        label = {"full":("есть","yes"),"partial":("частично","partial"),"none":("нет","no")}[st][0 if lang=='ru' else 1]
        out.append(f'<tr><td>{html.escape(name)}</td><td class="s {st}">{label}</td><td>{html.escape(note)}</td></tr>')
    return "\n".join(out)

def caps_html(lang):
    ru = lang=='ru'
    out=[]
    for num,tr,en,dr,de,br,be,vr,ve in CAPS:
        title = tr if ru else en
        what = dr if ru else de
        base = br if ru else be
        check = vr if ru else ve
        out.append(f'''<div class="cap"><span class="num">{num}</span><h4>{html.escape(title)}</h4>
<p>{html.escape(what)}</p>
<p class="kv"><b>{"Основа" if ru else "Basis"}:</b> {html.escape(base)}<br><b>{"Чем подтверждено" if ru else "Evidence"}:</b> {html.escape(check)}</p></div>''')
    return "\n".join(out)

def page(lang):
    ru = lang=='ru'
    t = dict(
        title = "Что мы умеем — Геотехник Сурок" if ru else "What we can do — Surok",
        top_left = "Сурок · возможности" if ru else "Surok · capabilities",
        top_right = ('<a href="../index.html">Лендинг</a> · <a href="../presentation/ru/">Презентация</a> · <a href="en/index.html">EN</a>' if ru
                     else '<a href="../../index.html">Landing</a> · <a href="../../presentation/en/">Presentation</a> · <a href="../index.html">RU</a>'),
        kicker = "Возможности · нормативная основа · проверка" if ru else "Capabilities · normative basis · evidence",
        h1 = "Что мы умеем" if ru else "What we can do",
        lead = ("Семь направлений, в которых агент доводит расчёт до протокола, который можно проверить: "
                "от давления под подошвой до таблицы трассируемости для эксперта." if ru else
                "Seven areas where the agent takes a calculation all the way to a report that can be checked: "
                "from pressure under a footing to a traceability table for a reviewer."),
        sub = ("Для каждого направления указано, на какой норме оно стоит и чем подтверждено — эталонным расчётом, "
               "второй реализацией или приёмочной проверкой. Ниже, в разделе сравнения, — честная карта относительно "
               "GEO5 как отраслевого ориентира." if ru else
               "Each area states the code it rests on and the evidence behind it: a benchmark run, a second implementation "
               "or an acceptance check. Below, in the comparison section, is an honest map against GEO5 as the industry reference."),
        m1 = ("направлений" if ru else "areas"),
        m2 = ("норм подтверждено" if ru else "codes confirmed"),
        m3 = ("эталонных расчёта" if ru else "benchmark runs"),
        m4 = ("модулей в сравнении" if ru else "modules compared"),
        h2a = "Направления работы" if ru else "Areas of work",
        h2b = "Сравнение с топовым продуктом отрасли" if ru else "Comparison with the industry reference",
        b_intro = ("GEO5 — зрелый коммерческий комплекс, и по широте модулей мы с ним не конкурируем. "
                   "Таблица показывает, где мы дополняем решатель, где закрываем задачу иначе, а где честно не берёмся. "
                   "Статус «есть» — реализация плюс подтверждённая редакция нормы и проверка."
                   if ru else
                   "GEO5 is a mature commercial suite, and we do not compete with it on module breadth. "
                   "The table shows where we complement a solver, where we cover a task differently, and where we honestly do not. "
                   "“Yes” means implementation plus a confirmed code edition and a check."),
        h2c = "Кому и зачем" if ru else "Who needs this and why",
        foot = ("Сурок · геотехнический агент · 2026" if ru else "Surok · geotechnical agent · 2026")
    )
    cats = "\n".join(f'<h3>{html.escape(c if ru else CAT_EN[c])}</h3><table><tr><th>{"Модуль GEO5" if ru else "GEO5 module"}</th><th>{"У нас" if ru else "Ours"}</th><th>{"Комментарий" if ru else "Comment"}</th></tr>{rows_for(c, lang)}</table>' for c in CAT_ORDER)

    if ru:
        cards = """
        <div class="card"><h4>Бюро, которое уже считает в GEO5</h4><p>GEO5 остаётся основным инструментом, Сурок достраивает слой обоснования: реестр редакций, трассируемость и протокол, который принимает эксперт.</p></div>
        <div class="card"><h4>Бюро без коммерческого комплекса</h4><p>Открытый контур для фундаментов, осадки и откосов — там, где нужен проверяемый результат, а не максимум модулей.</p></div>
        <div class="card"><h4>Экспертиза и ревью</h4><p>Проверка чужих расчётов: есть ли пункт, та ли редакция, воспроизводится ли число независимой реализацией.</p></div>"""
    else:
        cards = """
        <div class="card"><h4>Bureaux already using GEO5</h4><p>GEO5 stays the main tool; Surok adds the justification layer: edition registry, traceability and a report an expert will accept.</p></div>
        <div class="card"><h4>Bureaux without a commercial suite</h4><p>An open contour for foundations, settlement and slopes — where a verifiable result matters more than module count.</p></div>
        <div class="card"><h4>Expert review</h4><p>Checking third-party calculations: is the clause cited, is the edition current, does an independent implementation reproduce the number.</p></div>"""

    return f"""<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(t['title'])}</title>
<meta name="description" content="{html.escape(t['lead'])}">
<style>{CSS}</style></head><body>
<div class="wrap">
 <div class="top"><span><b>{t['top_left']}</b></span><span>{t['top_right']}</span></div>
 <header class="hero">
  <p class="kicker">{t['kicker']}</p>
  <h1>{t['h1']}</h1>
  <p class="lead">{t['lead']}</p>
  <p class="sub">{t['sub']}</p>
  <div class="metrics">
    <div class="metric"><b>{len(CAPS)}</b><span>{t['m1']}</span></div>
    <div class="metric"><b>9</b><span>{t['m2']}</span></div>
    <div class="metric"><b>2</b><span>{t['m3']}</span></div>
    <div class="metric"><b>{len(ROWS)}</b><span>{t['m4']}</span></div>
  </div>
 </header>
 <section><h2>{t['h2a']}</h2>{caps_html(lang)}</section>
 <section><h2>{t['h2b']}</h2><p class="sub">{t['b_intro']}</p>{cats}</section>
 <section><h2>{t['h2c']}</h2><div class="cols">{cards}</div>
   <p class="sub" style="margin-top:12px"><a href="https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/norms/registry.csv">{"Реестр норм" if ru else "Normative registry"}</a> · <a href="https://github.com/sasha-sazonova/geotech-surok/tree/main/workspace-geotech_surok/tools">{"Карта OSS-покрытия" if ru else "OSS coverage map"}</a> · <a href="https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/docs/status.md">{"Статус" if ru else "Status"}</a></p>
 </section>
 <div class="foot"><span>{t['foot']}</span></div>
</div></body></html>"""

base = pathlib.Path(__file__).resolve().parent
(base / "index.html").write_text(page("ru"), encoding="utf-8")
(base / "en").mkdir(exist_ok=True)
(base / "en/index.html").write_text(page("en"), encoding="utf-8")
print("caps:", len(CAPS), "modules:", len(ROWS), counts)
