"""
Zero-Backend-LLM invariant: AST scan to ensure no LLM SDK imports exist in backend/.
Violation = disqualification per Hackathon IV rules.
"""
import ast
from pathlib import Path

BACKEND_DIR = Path(__file__).parent.parent.parent / "backend"
FORBIDDEN_MODULES = {"openai", "anthropic", "langchain", "litellm", "cohere", "huggingface_hub"}


def _collect_imports(tree: ast.AST) -> list[str]:
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module.split(".")[0])
    return imports


def test_no_llm_imports_in_backend():
    violations = []
    for py_file in BACKEND_DIR.rglob("*.py"):
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_file))
        except SyntaxError:
            continue
        for mod in _collect_imports(tree):
            if mod in FORBIDDEN_MODULES:
                violations.append(f"{py_file.relative_to(BACKEND_DIR)}: imports '{mod}'")

    assert not violations, (
        "Zero-Backend-LLM invariant violated!\n"
        + "\n".join(f"  - {v}" for v in violations)
    )
