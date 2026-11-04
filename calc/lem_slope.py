# -*- coding: utf-8 -*-
"""LEM — устойчивость откоса семью методами предельного равновесия (движок xslope).

Зачем отдельный модуль: собственные ручные методы (calc/b1_slope.py) покрывают только
Fellenius и Bishop и служат контрольной реализацией. Полный набор методов даёт
xslope 1.0.6 (Apache-2.0) — зрелый публикуемый движок, проверенный на корпусе задач.

Методы (все — «инженерные методы предельного равновесия», НЕ пункт нормы):
    oms      — Ordinary Method of Slices (Fellenius)
    bishop   — упрощённый Bishop
    janbu    — Janbu corrected
    corps    — Corps of Engineers
    lowe     — Lowe & Karafiath
    spencer  — Spencer
    mprice   — Morgenstern–Price

Нормативная рамка: СП 22.13330.2016 требует расчёта устойчивости, но не фиксирует
конкретный LEM-метод; результат помечается как «инженерный метод», а не «пункт нормы».
Критерий приёмки — совпадение с контрольной реализацией (calc/b1_slope.py) и с pyslope
в пределах объявленного допуска.

Зависимость необязательная: при отсутствии xslope модуль поднимает LemUnavailable,
а вызывающий код обязан вернуть «не определено», а не подставлять другой метод.
"""
from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

try:  # необязательная зависимость
    import xslope  # noqa: F401
    from xslope.fileio import (default_template_path, load_slope_data,
                               save_slope_data_to_xlsx)
    from xslope.preflight import preflight as _preflight
    from xslope.search import generate_starting_circles
    import xslope.slice as _xslice
    import xslope.solve as _xsolve
    _XSLOPE_AVAILABLE = True
except Exception:  # pragma: no cover - зависит от окружения
    _XSLOPE_AVAILABLE = False


class LemUnavailable(RuntimeError):
    """xslope не установлен: расчёт LEM невозможен (не подменять суррогатом)."""


LEM_METHODS: Tuple[str, ...] = ("oms", "bishop", "janbu", "corps", "lowe", "spencer", "mprice")

METHOD_TITLES: Dict[str, str] = {
    "oms": "Ordinary / Fellenius",
    "bishop": "Bishop (упрощённый)",
    "janbu": "Janbu (corrected)",
    "corps": "Corps of Engineers",
    "lowe": "Lowe & Karafiath",
    "spencer": "Spencer",
    "mprice": "Morgenstern–Price",
}


@dataclass
class SlopeModel:
    """Плоский откос в координатах «вверх»: бровка (crest_x, crest_y), подошва ниже/правее."""
    crest_x: float = 40.0
    crest_y: float = 10.0
    toe_x: float = 60.0
    toe_y: float = 0.0
    extend_left: float = 40.0     # длина плоской бермы слева от бровки
    extend_right: float = 40.0    # длина плоской подошвы справа от подошвы
    base_depth: float = 0.0       # насколько грунт продолжается ниже подошвы (м)
    gamma: float = 18.0
    c: float = 10.0
    phi: float = 25.0
    unit_system: str = "si"

    def profile(self) -> List[Tuple[float, float]]:
        pts = [
            (self.crest_x - self.extend_left, self.crest_y),
            (self.crest_x, self.crest_y),
            (self.toe_x, self.toe_y),
            (self.toe_x + self.extend_right, self.toe_y),
        ]
        return pts


@dataclass
class Circle:
    """Круг скольжения в координатах модели (Depth — отметка низшей точки)."""
    xo: float
    yo: float
    R: float

    @property
    def depth(self) -> float:
        return self.yo - self.R

    def as_dict(self) -> Dict[str, float]:
        return {"Xo": self.xo, "Yo": self.yo, "Depth": self.depth}


def available() -> bool:
    return _XSLOPE_AVAILABLE


def _build_slope_data(model: SlopeModel, circles: Sequence[Circle]) -> dict:
    if not _XSLOPE_AVAILABLE:
        raise LemUnavailable(
            "xslope не установлен: pip install xslope (Apache-2.0). "
            "Расчёт LEM без движка не выполняется.")
    data = {
        "unit_system": model.unit_system,
        "gamma_water": 9.81,
        "tcrack_depth": 0.0,
        "tcrack_water": 0.0,
        "k_seismic": 0.0,
        "max_depth": min(model.toe_y, model.crest_y) - abs(model.base_depth),
        "profile_lines": [{"mat_id": 0, "coords": model.profile()}],
        "materials": [{
            "mat_id": 0, "name": "Soil", "gamma": model.gamma,
            "c": model.c, "phi": model.phi, "u": "none", "option": "mc",
        }],
        "circles": [c.as_dict() for c in circles],
    }
    return data


def _roundtrip(data: dict, path: str) -> dict:
    save_slope_data_to_xlsx(data, path, template=default_template_path())
    return load_slope_data(path)


def _workfile(workdir: str, name: str) -> str:
    """Уникальный путь: параллельные вызовы не должны перезаписывать файл друг друга."""
    os.makedirs(workdir, exist_ok=True)
    fd, path = tempfile.mkstemp(prefix=f"{name}_", suffix=".xlsx", dir=workdir)
    os.close(fd)
    return path


def factor_of_safety(model: SlopeModel, circle: Circle,
                     methods: Sequence[str] = LEM_METHODS,
                     num_slices: int = 40,
                     workdir: str = "/tmp") -> Dict[str, object]:
    """FS по каждому методу для ЗАДАННОГО круга.

    Возвращает {"fs": {метод: значение}, "spread": max-min, "failures": {метод: причина},
                "geometry": {...}}. Молчаливая подмена метода запрещена: если метод не
    сошёлся, он попадает в failures и НЕ участвует в spread.
    """
    data = _build_slope_data(model, [circle])
    path = _workfile(workdir, "lem_model")
    loaded = _roundtrip(data, path)

    # Проверка модели движком ДО расчёта: недопустимая геометрия/круг должны давать
    # внятную ошибку, а не «странный FS».
    report = _preflight(loaded, "lem", {"surface": "circular", "method": "bishop"})
    if not report.ok:
        raise ValueError("модель не прошла preflight движка:\n" + report.format())
    ok, packed = _xslice.generate_slices(loaded, circle=loaded["circles"][0],
                                         num_slices=num_slices, debug=False)
    if not ok:
        raise ValueError("не удалось нарезать срезы: проверьте геометрию и круг")
    slices = packed[0]

    fs: Dict[str, float] = {}
    failures: Dict[str, str] = {}
    details: Dict[str, dict] = {}
    for name in methods:
        if name not in LEM_METHODS:
            failures[name] = f"неизвестный метод {name!r}"
            continue
        fn = getattr(_xsolve, name)
        try:
            ok_m, payload = fn(slices)
            if not ok_m or payload.get("FS") is None:
                failures[name] = str(payload.get("warnings") or "метод не дал решения")
                continue
            fs[name] = float(payload["FS"])
            details[name] = {k: v for k, v in payload.items()
                             if k in ("theta", "lambda", "fo", "FS_base")}
        except Exception as exc:  # pragma: no cover - защита от сюрпризов движка
            failures[name] = f"{type(exc).__name__}: {exc}"

    spread = (max(fs.values()) - min(fs.values())) if len(fs) > 1 else 0.0
    return {
        "fs": {k: round(v, 4) for k, v in fs.items()},
        "spread": round(spread, 4),
        "failures": failures,
        "details": details,
        "circle": {"xo": circle.xo, "yo": circle.yo, "R": circle.R, "depth": circle.depth},
        "slices": num_slices,
        "status": "рассчитано" if fs else "не определено",
    }


def critical_circle(model: SlopeModel, num_slices: int = 40,
                    workdir: str = "/tmp") -> Dict[str, object]:
    """Автоподбор стартовых кругов движком и выбор критического по Bishop."""
    data = _build_slope_data(model, [])
    path = _workfile(workdir, "lem_search")
    loaded = _roundtrip(data, path)
    circles = generate_starting_circles(loaded)
    if not circles:
        raise ValueError("движок не предложил ни одного стартового круга")

    best = None
    tried = 0
    for c in circles:
        try:
            res = factor_of_safety(
                model, Circle(c["Xo"], c["Yo"], c["R"]), methods=("bishop",), num_slices=num_slices,
                workdir=workdir)
        except Exception:
            continue
        tried += 1
        if "bishop" in res["fs"]:
            val = res["fs"]["bishop"]
            if best is None or val < best["fs"]["bishop"]:
                best = res

    if best is None:
        raise ValueError("ни один стартовый круг не дал решения")
    # для критического круга считаем все методы
    full = factor_of_safety(
        model, Circle(best["circle"]["xo"], best["circle"]["yo"], best["circle"]["R"]),
        num_slices=num_slices, workdir=workdir)
    full["circles_tried"] = tried
    full["circles_offered"] = len(circles)
    return full


def to_status(result: Dict[str, object], fs_required: float) -> Dict[str, object]:
    """Статус проверки: сравнение критического FS (по Bishop, иначе минимум) с требуемым."""
    fs = result.get("fs") or {}
    if not fs:
        return {"check": "k_stability", "status": "не определено", "value": None,
                "criterion": fs_required}
    value = fs.get("bishop", min(fs.values()))
    return {"check": "k_stability", "value": round(float(value), 3),
            "criterion": fs_required,
            "status": "выполняется" if value >= fs_required else "не выполняется",
            "method": "bishop" if "bishop" in fs else "min"}
