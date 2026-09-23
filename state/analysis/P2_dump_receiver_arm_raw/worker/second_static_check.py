"""Syntax and AST checks only; never import/run the receiver or its generated bodies."""
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[4]
raw = Path(__file__).parent
source = (root / "tools/dump_match.py").read_bytes()
frozen = (raw / "second_dump_match.py").read_bytes()
assert source == frozen
tree = ast.parse(source, filename="tools/dump_match.py")
baseline = ast.parse((raw / "baseline_dump_match.py").read_bytes())
compile(tree, "tools/dump_match.py", "exec")

def literal(module, name):
    return next(ast.literal_eval(node.value) for node in module.body
                if isinstance(node, ast.Assign) and any(
                    isinstance(target, ast.Name) and target.id == name
                    for target in node.targets))

assert literal(tree, "REMOTE_RECEIVER") == literal(baseline, "REMOTE_RECEIVER")
schema = literal(tree, "_CONNECTION_SCHEMA")
remote = literal(tree, "_CONNECTION_REMOTE")
programs = {"schema": schema, "observer": schema + remote + literal(tree, "_CONNECTION_OBSERVER"),
            "receiver": schema + remote + literal(tree, "_CONNECTION_RECEIVER")}
sizes = []
for name, text in programs.items():
    parsed = ast.parse(text, filename=name)
    compile(parsed, name, "exec")
    sizes.extend(dict(program=name, function=node.name, lines=node.end_lineno-node.lineno+1)
                 for node in ast.walk(parsed) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)))
    if name == "schema":
        assert all(isinstance(node, (ast.Import, ast.ImportFrom, ast.Assign, ast.FunctionDef))
                   for node in parsed.body)

def iteration(module):
    owner = next(node for node in module.body if isinstance(node, ast.ClassDef) and node.name == "LiveCapture")
    return next(node for node in owner.body if isinstance(node, ast.FunctionDef) and node.name == "__iter__")

old, current = iteration(baseline), iteration(tree)
assert isinstance(current.body[0], ast.If)
assert [ast.dump(node) for node in old.body] == [ast.dump(node) for node in current.body[1:]]
sizes.extend(dict(program="host", function=node.name, lines=node.end_lineno-node.lineno+1)
             for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)))
report = dict(observed_utc=datetime.now(timezone.utc).isoformat(), python=sys.version,
              source_sha256=hashlib.sha256(source).hexdigest(), syntax="PASS",
              generated_program_syntax="PASS", original_receiver_literal="BYTE_IDENTICAL",
              legacy_iteration_body="AST_IDENTICAL_AFTER_OPT_IN_DISPATCH",
              schema_top_level="IMPORTS_ASSIGNMENTS_FUNCTION_DEFINITIONS_ONLY",
              maximum_function_lines=max(item["lines"] for item in sizes),
              functions_over_60_lines=[item for item in sizes if item["lines"] >= 60],
              execution="No module import, receiver/observer execution, independent tests or board actions")
(raw / "second_static_checks.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
print(json.dumps(report, indent=2))
