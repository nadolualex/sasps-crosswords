"""Descriptive AST counts, not an overall maintainability score."""

import ast
import json
from pathlib import Path


def collect() -> dict:
    output = {}
    for variant in ("conditional", "strategy"):
        path = Path("crosswords") / f"{variant}.py"
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        dispatcher = next(
            node for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name.endswith("Dispatcher")
        )
        select = next(node for node in dispatcher.body
                      if isinstance(node, ast.FunctionDef) and node.name == "select")
        output[variant] = {
            "file": str(path),
            "nonblank_noncomment_lines": sum(
                bool(line.strip()) and not line.lstrip().startswith("#")
                for line in source.splitlines()
            ),
            "class_definitions_including_protocol": sum(
                isinstance(node, ast.ClassDef) for node in ast.walk(tree)
            ),
            "dispatcher_select_if_nodes": sum(
                isinstance(node, ast.If) for node in ast.walk(select)
            ),
        }
    return output


if __name__ == "__main__":
    output = Path("results/m1/code_metrics.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(collect(), indent=2) + "\n", encoding="utf-8")
    print(output)
