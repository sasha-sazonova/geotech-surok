#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate traceability.yml: clauses <-> code <-> tests, and normative backing.

Fails (exit 1) on:
* a clause without code or tests;
* a code reference whose file or symbol does not exist;
* a test reference that does not exist;
* an orphan test (not referenced by any clause);
* a clause marked verified whose document is not verified or has no dated source.
"""
import ast
import io
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
TRACE = ROOT / "traceability.yml"


def scan_tests():
    tests = {}
    for path in sorted((ROOT / "tests").rglob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        rel = str(path.relative_to(ROOT))
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                tests[f"{rel}::{node.name}"] = node.lineno
    return tests


def scan_symbols(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {n.name: n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}


def main():
    data = yaml.safe_load(TRACE.read_text(encoding="utf-8"))
    errors = []
    docs = {d["id"]: d for d in data.get("documents", [])}
    tests = scan_tests()
    referenced = set()

    for clause in data.get("clauses", []):
        cid = clause.get("id", "?")
        doc = docs.get(clause.get("document"))
        if doc is None:
            errors.append(f"{cid}: unknown document {clause.get('document')!r}")
            continue
        code_refs = clause.get("code") or []
        test_refs = clause.get("tests") or []
        if not code_refs:
            errors.append(f"{cid}: no code reference")
        if not test_refs:
            errors.append(f"{cid}: no test reference")
        for ref in code_refs:
            f = ROOT / ref["file"]
            if not f.exists():
                errors.append(f"{cid}: code file missing {ref['file']}")
                continue
            symbols = scan_symbols(f)
            if ref["symbol"] not in symbols:
                errors.append(f"{cid}: symbol {ref['symbol']} not found in {ref['file']}")
        for t in test_refs:
            if t not in tests:
                errors.append(f"{cid}: test not found {t}")
            referenced.add(t)
        if clause.get("status") == "verified":
            ver = doc.get("verification", {})
            if ver.get("status") != "verified":
                errors.append(f"{cid}: clause verified but document is {ver.get('status')!r}")
            sources = ver.get("sources") or []
            if not sources or not all(s.get("url") and s.get("retrieved") for s in sources):
                errors.append(f"{cid}: verified clause without dated source")

    orphans = sorted(set(tests) - referenced)
    for t in orphans:
        errors.append(f"orphan test (no clause): {t}")

    if errors:
        print("TRACEABILITY: FAILED")
        for e in errors:
            print(" -", e)
        return 1
    print(f"TRACEABILITY: OK ({len(data.get('clauses', []))} clauses, {len(tests)} tests)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
