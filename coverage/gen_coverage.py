# -*- coding: utf-8 -*-
"""Генерирует страницу покрытия задач GEO5 (RU/EN) для репозитория geotech-surok."""
import html, pathlib

# (категория_ru, категория_en, модуль_ru, модуль_en, статус, комментарий_ru, комментарий_en)
# статус: full | partial | none
ROWS = [
 ("Подпорные стены","Retaining walls","Уголковая стена","Cantilever wall","partial",
  "Ренкин/Кулон и проверки устойчивости есть в geoeq/anaStruct; СП 542 подтверждён, но полного модуля стены с этапностью нет.",
  "Rankine/Coulomb and stability checks exist in geoeq/anaStruct; SP 542 is confirmed, but there is no full wall module with staged construction."),
 ("Подпорные стены","Retaining walls","Гравитационная стена","Gravity wall","partial",
  "Та же база: давление грунта и устойчивость считаются, специфических проверок гравитационной стены нет.",
  "Same base: earth pressure and stability are computed; gravity-wall specific checks are missing."),
 ("Подпорные стены","Retaining walls","Армированные насыпи","Reinforced embankments","none",
  "Армирования и нагелей в OSS-контуре нет — заявленный пробел ТЗ 12.3.",
  "Reinforcement and soil nails are absent from the OSS contour — a declared gap."),
 ("Подпорные стены","Retaining walls","Габионы","Gabions","none",
  "Габионных стен по СП 22/СП 542 в open-source нет; правило производителя — объект проверки, не расчёта.",
  "Gabion walls per SP 22/SP 542 do not exist in open source; manufacturer rules are a check object, not a calculation."),
 ("Подпорные стены","Retaining walls","Армированная стена","Reinforced wall","none",
  "Нет модуля армирования; возможно только давление грунта как вход.",
  "No reinforcement module; only earth pressure as an input."),
 ("Подпорные стены","Retaining walls","Стена Redi-Rock","Redi-Rock wall","none",
  "Каталоги блоков производителя — вне open-source контура.",
  "Vendor block catalogues are outside the open-source contour."),
 ("Подпорные стены","Retaining walls","Сборная стена","Precast wall","none",
  "Нет библиотеки сборных элементов и проверок узлов.",
  "No precast element library or joint checks."),
 ("Подпорные стены","Retaining walls","Нагельное крепление","Soil nailing","none",
  "Нагели и их выдёргивание не реализованы.",
  "Nails and pull-out checks are not implemented."),
 ("Подпорные стены","Retaining walls","Стабилизирующая свая","Stabilising pile","none",
  "Нет модели свая-грунт для стабилизации откоса.",
  "No pile-soil model for slope stabilisation."),
 ("Подпорные стены","Retaining walls","Давление грунта","Earth pressure","full",
  "Ренкин и Кулон реализованы в geoeq; используется как вход для стен и откосов.",
  "Rankine and Coulomb are implemented in geoeq; used as input for walls and slopes."),
 ("Устойчивость откосов","Slope stability","Устойчивость откоса","Slope stability","partial",
  "xslope: 7 методов LEM, сверка с pyslope; нет метода Шахунянца и армирования.",
  "xslope: 7 LEM methods, cross-checked with pyslope; no Shakhunyants method or reinforcement."),
 ("Устойчивость откосов","Slope stability","Устойчивость откоса – Фильтрация","Slope stability – seepage","partial",
  "Фильтрация считается через ogs/Kratos, геотехнического препроцессора нет — сетка и ГУ вручную.",
  "Seepage is computed with ogs/Kratos; there is no geotechnical preprocessor, mesh and BCs are manual."),
 ("Устойчивость откосов","Slope stability","Скальный откос","Rock slope","partial",
  "Кинематический анализ через mplstereonet; прочностные расчёты скального массива — нет.",
  "Kinematic analysis via mplstereonet; rock-mass strength calculations are missing."),
 ("Фундаменты","Foundations","Отдельные фундаменты","Spread footing","partial",
  "D1: R по п. 5.6.7 и осадка по прил. Г реализованы и проверены. Момент, крен и краевые давления — не определено.",
  "D1: R per clause 5.6.7 and settlement per Appendix G are implemented and checked. Moment, tilt and edge pressure are not determined."),
 ("Фундаменты","Foundations","Отдельные фундаменты CPT","Spread footing from CPT","partial",
  "CPT читается pygef/groundhog, но вариант «фундамент по CPT» в коде не реализован.",
  "CPT is read by pygef/groundhog, but the CPT-based footing route is not implemented in code."),
 ("Фундаменты","Foundations","Осадка","Settlement","full",
  "Послойное суммирование по СП 22 прил. Г реализовано в D1; ограничение задаётся данными, а не методом.",
  "Layer-by-layer summation per SP 22 Appendix G is implemented in D1; the limit comes from data, not from the method."),
 ("Фундаменты","Foundations","Плита","Slab","partial",
  "geofound/bedrock-ge дают плиту, но не плиту на грунтовом основании с СП-проверками.",
  "geofound/bedrock-ge provide a slab, but not a slab on soil with SP checks."),
 ("Фундаменты","Foundations","Балка","Beam","partial",
  "anaStruct считает балку; грунтовое основание — только через коэффициенты постели вручную.",
  "anaStruct computes the beam; soil support only via manually assigned subgrade moduli."),
 ("Фундаменты","Foundations","Устой","Abutment","none",
  "Нет модуля устоя и его специфических проверок.",
  "No abutment module or its specific checks."),
 ("Фундаменты","Foundations","Сваи","Piles","partial",
  "OpenPile: балочно-свайные модели и пружины; нормативного маршрута СП 24 в OSS нет — статус no_verified_SP_24_workflow.",
  "OpenPile: beam-pile models and springs; no SP 24 normative route in OSS — status no_verified_SP_24_workflow."),
 ("Фундаменты","Foundations","Микросвая","Micropile","none",
  "Микросвай и их несущей способности в контуре нет.",
  "Micropiles and their capacity are not in the contour."),
 ("Фундаменты","Foundations","Куст свай","Pile group","none",
  "Куст, взаимное влияние и групповая эффективность не реализованы.",
  "Pile group, interaction and group efficiency are not implemented."),
 ("Фундаменты","Foundations","Свая CPT","Pile from CPT","partial",
  "De Beer по CPT есть в groundhog/methodedebeer как метод, не как СП-маршрут.",
  "De Beer from CPT exists in groundhog/methodedebeer as a method, not as an SP route."),
 ("МКЭ","FEM","МКЭ","FEM","partial",
  "OpenSees/Kratos/Code_Aster есть; Hardening Soil и Soft Soil «из коробки» нет.",
  "OpenSees/Kratos/Code_Aster are available; Hardening Soil and Soft Soil are not available out of the box."),
 ("МКЭ","FEM","МКЭ – Тоннель","FEM – tunnel","none",
  "Шаблонов тоннеля и этапов проходки нет.",
  "No tunnel templates or excavation stages."),
 ("МКЭ","FEM","МКЭ – Консолидация","FEM – consolidation","partial",
  "Консолидация возможна в общей МКЭ-постановке Kratos/OpenSees, готового модуля нет.",
  "Consolidation is possible in a general Kratos/OpenSees formulation; no ready module."),
 ("МКЭ","FEM","МКЭ – Фильтрация","FEM – seepage","partial",
  "ogs/Kratos считают фильтрацию; препроцессинга и типовых ГУ нет.",
  "ogs/Kratos compute seepage; there is no preprocessing or standard BC set."),
 ("МКЭ","FEM","МКЭ – Землетрясение","FEM – earthquake","partial",
  "Динамика в OpenSees есть; проверок по СП 14.13330 нет (документ в очереди).",
  "Dynamics exist in OpenSees; SP 14.13330 checks are absent (document is queued)."),
 ("Ограждения котлованов","Excavation support","Ограждение котлованов – анализ","Excavation analysis","none",
  "Полного сценария «выемка по стадиям → анкеры → распорки → проверки» в OSS нет.",
  "No full scenario “staged excavation → anchors → struts → checks” in OSS."),
 ("Ограждения котлованов","Excavation support","Ограждение котлованов – проект","Excavation design","none",
  "Проектирования ограждения с подбором сечения и анкеров нет.",
  "No design of the support system with section and anchor selection."),
 ("Тоннели","Tunnels","Шахта","Shaft","none",
  "Шахта и крепь не реализованы.",
  "Shaft and lining are not implemented."),
 ("Тоннели","Tunnels","Выработка","Underground opening","none",
  "Выработки — только общее МКЭ-ядро, без шаблонов.",
  "Openings rely on the general FEM core only, without templates."),
 ("Изыскания","Site investigation","Стратиграфия","Stratigraphy","partial",
  "GemPy/LoopStructural строят геомодель; единой геомодели как источника расчёта нет.",
  "GemPy/LoopStructural build a geomodel; there is no single geomodel as a calculation source."),
 ("Изыскания","Site investigation","Стратиграфия – Земляные работы","Stratigraphy – earthworks","none",
  "Ведомостей земляных работ нет.",
  "No earthworks quantities."),
 ("Изыскания","Site investigation","Стратиграфия – Резервы","Stratigraphy – volumes","none",
  "Подсчёта объёмов/резервов нет.",
  "No volume or reserve calculation."),
 ("Изыскания","Site investigation","Стратиграфия – Таблицы","Stratigraphy – tables","partial",
  "Таблицы слоёв и параметров ведутся вручную, экспорт в расчёт — через сценарий.",
  "Layer and parameter tables are maintained manually; export to calculation goes through the scenario."),
 ("Изыскания","Site investigation","Лаборатория","Laboratory","partial",
  "groundhog/geolysis обрабатывают лабораторные данные; PMT/DMT и мобильный ввод — нет.",
  "groundhog/geolysis process lab data; PMT/DMT and mobile input are missing."),
 ("Изыскания","Site investigation","Облако точек","Point cloud","partial",
  "laspy/PDAL читают облака; геотехнической интерпретации нет.",
  "laspy/PDAL read point clouds; there is no geotechnical interpretation."),
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
.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1px;background:var(--line);border:1px solid var(--line);margin:26px 0 0}
.metric{background:var(--paper);padding:18px 20px}
.metric b{display:block;font-size:34px;letter-spacing:-.03em;line-height:1}
.metric span{font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);display:block;margin-top:6px}
section{padding:6vh 0;border-top:1px solid var(--line)}
h2{font-size:clamp(22px,3vw,32px);letter-spacing:-.02em;margin:0 0 10px}
h3{font-size:16px;margin:26px 0 8px;font-family:var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--muted);font-weight:400}
table{border-collapse:collapse;width:100%;font-size:14px;margin-top:8px}
th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-family:var(--mono);font-size:10px;letter-spacing:.13em;text-transform:uppercase;color:var(--muted);font-weight:400}
td.s{white-space:nowrap;font-family:var(--mono);font-size:11px;letter-spacing:.06em}
.full{color:#0B7A5A}.partial{color:#9A6A00}.none{color:#9B2C2C}
.tag{display:inline-block;font-family:var(--mono);font-size:10px;letter-spacing:.1em;text-transform:uppercase;border:1px solid var(--line);padding:3px 7px;margin:0 6px 6px 0;color:var(--muted)}
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
        stlabel = {"full":("закрываем","covered"),"partial":("частично","partial"),"none":("нет","not covered")}[st][0 if lang=='ru' else 1]
        out.append(f'<tr><td>{html.escape(name)}</td><td class="s {st}">{stlabel}</td><td>{html.escape(note)}</td></tr>')
    return "\n".join(out)

def page(lang):
    ru = lang=='ru'
    t = dict(
        title = "Что мы можем из задач GEO5 — Геотехник Сурок" if ru else "What we cover from GEO5 tasks — Surok",
        top_left = "Сурок · покрытие задач GEO5" if ru else "Surok · GEO5 task coverage",
        top_right = ('<a href="../index.html">Лендинг</a> · <a href="../presentation/ru/">Презентация</a> · <a href="en/index.html">EN</a>' if ru
                     else '<a href="../../index.html">Landing</a> · <a href="../../presentation/en/">Presentation</a> · <a href="../index.html">RU</a>'),
        kicker = "Для кого и зачем · честное сравнение по классам задач" if ru else "Who it is for · an honest class-by-class comparison",
        h1 = "Что мы можем из задач GEO5" if ru else "What we cover from GEO5 tasks",
        lead = ("GEO5 — зрелый коммерческий комплекс из 40 модулей. Мы не конкурируем с ним по широте: "
                "наша работа — нормативная прослеживаемость и протокол под экспертизу. Ниже — что из этого "
                "списка задач мы закрываем сегодня, что частично и чего у нас нет." if ru else
                "GEO5 is a mature commercial suite of 40 modules. We do not compete on breadth: our job is "
                "normative traceability and a report package for expert review. Below is what we cover today, "
                "what is partial, and what we do not have."),
        sub = ("Сравнение по классам задач, а не по функциям: одинаковое название модуля не означает одинаковый объём. "
               "Статус «закрываем» означает, что есть реализация, подтверждённая редакция нормы и проверка; "
               "«частично» — метод есть, нормативного маршрута или полноты нет; «нет» — модуля в контуре нет."
               if ru else
               "Compared by task class, not by feature list: the same module name does not mean the same scope. "
               "“Covered” means implementation + confirmed code edition + verification; “partial” means the method exists "
               "but the normative route or completeness is missing; “not covered” means no module in the contour."),
        m1 = "закрываем" if ru else "covered",
        m2 = "частично" if ru else "partial",
        m3 = "не закрываем" if ru else "not covered",
        m4 = "модулей в GEO5" if ru else "modules in GEO5",
        h2a = "Карта по категориям" if ru else "Map by category",
        h2b = "Кому и зачем это нужно" if ru else "Who needs this and why",
        h2c = "Как читать статусы" if ru else "How to read the statuses",
        foot = ("Сурок · геотехнический агент · 2026 · сравнение по классам задач, не рекламное сопоставление"
                if ru else "Surok · geotechnical agent · 2026 · class-level comparison, not marketing")
    )
    cats = "\n".join(f'<h3>{html.escape(c if ru else CAT_EN[c])}</h3><table><tr><th>{"Модуль GEO5" if ru else "GEO5 module"}</th><th>{"Статус" if ru else "Status"}</th><th>{"Что у нас" if ru else "What we have"}</th></tr>{rows_for(c, lang)}</table>' for c in CAT_ORDER)

    if ru:
        cards = """
        <div class="card"><h4>Бюро, которое уже считает в GEO5</h4><p>Мы не заменяем расчёт — мы достраиваем то, чего в решателе нет: реестр редакций, таблицу трассируемости и протокол, который принимает эксперт. GEO5 остаётся основным инструментом, Сурок — слоем обоснования.</p></div>
        <div class="card"><h4>Бюро без коммерческого комплекса</h4><p>Открытый контур для задач, где нужен не «максимум модулей», а проверяемый результат: фундаменты, осадка, откосы. Часть задач придётся закрывать вручную или не брать вовсе — это видно в таблице.</p></div>
        <div class="card"><h4>Экспертиза и ревью</h4><p>Проверка чужих расчётов: есть ли пункт, та ли редакция, сходится ли число с независимой реализацией. Здесь ценность не в расчёте, а в возможности его проверить.</p></div>"""
    else:
        cards = """
        <div class="card"><h4>Bureaux already using GEO5</h4><p>We do not replace the calculation — we add what a solver does not have: an edition registry, a traceability table and a report package an expert will accept. GEO5 stays the main tool; Surok is the justification layer.</p></div>
        <div class="card"><h4>Bureaux without a commercial suite</h4><p>An open contour for tasks where the goal is a verifiable result, not a maximum of modules: foundations, settlement, slopes. Some tasks must be done manually or declined — the table shows which.</p></div>
        <div class="card"><h4>Expert review</h4><p>Checking third-party calculations: is the clause cited, is the edition current, does the number match an independent implementation. The value is not the calculation but the ability to check it.</p></div>"""

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
    <div class="metric"><b>{counts['full']}</b><span>{t['m1']}</span></div>
    <div class="metric"><b>{counts['partial']}</b><span>{t['m2']}</span></div>
    <div class="metric"><b>{counts['none']}</b><span>{t['m3']}</span></div>
    <div class="metric"><b>{len(ROWS)}</b><span>{t['m4']}</span></div>
  </div>
 </header>
 <section><h2>{t['h2a']}</h2>{cats}</section>
 <section><h2>{t['h2b']}</h2><div class="cols">{cards}</div></section>
 <section><h2>{t['h2c']}</h2><p class="sub">{t['sub']}</p>
   <p class="sub" style="margin-top:10px"><a href="https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/norms/registry.csv">{"Реестр норм" if ru else "Normative registry"}</a> · <a href="https://github.com/sasha-sazonova/geotech-surok/tree/main/workspace-geotech_surok/tools">{"Карта OSS-покрытия" if ru else "OSS coverage map"}</a> · <a href="https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/docs/status.md">{"Статус" if ru else "Status"}</a></p>
 </section>
 <div class="foot"><span>{t['foot']}</span></div>
</div></body></html>"""

base = pathlib.Path(__file__).resolve().parent
(base / "index.html").write_text(page("ru"), encoding="utf-8")
(base / "en").mkdir(exist_ok=True)
(base / "en/index.html").write_text(page("en"), encoding="utf-8")
print("counts:", counts, "total:", len(ROWS))
