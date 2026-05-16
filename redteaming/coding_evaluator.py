"""
coding_evaluator.py — Evaluate AI-generated code for spec compliance, edge case handling,
error handling, and overall quality. Designed for use in adversarial AI evaluation workflows.
"""

import ast
import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class CodeFinding:
    dimension: str
    severity: str  # CRITICAL / HIGH / MEDIUM / LOW
    message: str
    evidence: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "dimension": self.dimension,
            "severity": self.severity,
            "message": self.message,
            "evidence": self.evidence,
        }


@dataclass
class CodeEvalResult:
    syntax_valid: bool
    spec_compliance: bool
    edge_cases_handled: bool
    error_handling_present: bool
    complexity_appropriate: bool
    documentation_present: bool
    findings: List[CodeFinding]
    overall_score: float  # 0.0 - 1.0
    summary: str

    def to_dict(self) -> dict:
        return {
            "syntax_valid": self.syntax_valid,
            "spec_compliance": self.spec_compliance,
            "edge_cases_handled": self.edge_cases_handled,
            "error_handling_present": self.error_handling_present,
            "complexity_appropriate": self.complexity_appropriate,
            "documentation_present": self.documentation_present,
            "findings": [f.to_dict() for f in self.findings],
            "overall_score": self.overall_score,
            "summary": self.summary,
        }


@dataclass
class SolutionComparison:
    solution_a_score: float
    solution_b_score: float
    winner: str  # 'A', 'B', or 'TIE'
    reasoning: str
    a_strengths: List[str]
    b_strengths: List[str]
    recommendation: str

    def to_dict(self) -> dict:
        return {
            "solution_a_score": self.solution_a_score,
            "solution_b_score": self.solution_b_score,
            "winner": self.winner,
            "reasoning": self.reasoning,
            "a_strengths": self.a_strengths,
            "b_strengths": self.b_strengths,
            "recommendation": self.recommendation,
        }


def _check_syntax(code: str) -> tuple[bool, Optional[str]]:
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, str(e)


def _check_spec_compliance(code: str, spec: str) -> tuple[bool, List[str]]:
    """
    Heuristic spec compliance: extract key nouns/verbs from spec and look for them in code.
    Not semantic analysis — just coverage signal.
    """
    # Extract function names or class names mentioned in spec
    func_mentions = re.findall(r'\b([a-z_][a-z0-9_]*)\s*\(', spec.lower())
    class_mentions = re.findall(r'\bclass\s+([A-Za-z_][A-Za-z0-9_]*)', spec)

    code_lower = code.lower()
    missing = []
    for fn in set(func_mentions):
        if len(fn) > 3 and fn not in ("def", "for", "if", "not", "and", "or"):
            if fn not in code_lower:
                missing.append(fn)

    compliant = len(missing) == 0 or len(missing) <= len(func_mentions) * 0.3
    return compliant, missing


def _check_edge_cases(code: str) -> tuple[bool, List[str]]:
    """Check for common edge case handling patterns."""
    missing = []

    # None/null handling
    if "None" in code and "is None" not in code and "is not None" not in code:
        missing.append("potential unchecked None value")

    # Empty input handling
    if not re.search(r'(len\s*\(|not\s+\w+\s*:|if\s+not\s+)', code):
        missing.append("no empty input guard detected")

    # Index bounds
    if "[" in code and not re.search(r'(len\s*\(|try|except|IndexError)', code):
        missing.append("no index bounds checking detected")

    handled = len(missing) == 0
    return handled, missing


def _check_error_handling(code: str) -> tuple[bool, List[str]]:
    """Check for presence of try/except or explicit error handling."""
    issues = []
    has_try_except = bool(re.search(r'\btry\s*:', code))
    has_raises = bool(re.search(r'\braise\s+\w+', code))
    has_value_checks = bool(re.search(r'(ValueError|TypeError|KeyError|AttributeError)', code))

    if not any([has_try_except, has_raises, has_value_checks]):
        issues.append("no error handling or exception raising detected")

    return len(issues) == 0, issues


def _check_complexity(code: str) -> tuple[bool, List[str]]:
    """Rough complexity check: deeply nested code or very long functions."""
    issues = []
    lines = code.split("\n")

    # Check nesting depth
    max_indent = 0
    for line in lines:
        stripped = line.lstrip()
        if stripped:
            indent = len(line) - len(stripped)
            max_indent = max(max_indent, indent)

    if max_indent > 24:  # 6+ levels of 4-space indentation
        issues.append(f"deeply nested code (max indent: {max_indent} spaces)")

    # Check function length
    func_blocks = re.split(r'\ndef ', code)
    for block in func_blocks[1:]:
        block_lines = [l for l in block.split("\n") if l.strip() and not l.strip().startswith("#")]
        if len(block_lines) > 60:
            fn_name = block.split("(")[0].strip()
            issues.append(f"function '{fn_name}' is very long ({len(block_lines)} lines)")

    return len(issues) == 0, issues


def _check_documentation(code: str) -> tuple[bool, List[str]]:
    """Check for docstrings and inline comments."""
    issues = []
    has_module_docstring = code.lstrip().startswith('"""') or code.lstrip().startswith("'''")
    has_function_docstring = bool(re.search(r'def\s+\w+[^:]*:\s*\n\s+"""', code))
    has_comments = bool(re.search(r"#\s+\w+", code))

    if not has_function_docstring and not has_comments:
        issues.append("no docstrings or inline comments found")

    return len(issues) == 0, issues


class CodingEvaluator:
    """
    Evaluate AI-generated code against a natural language specification.

    Usage:
        evaluator = CodingEvaluator()
        result = evaluator.evaluate(code="def add(a, b): return a + b", spec="Write a function that adds two numbers")
    """

    def evaluate(self, code: str, spec: str) -> CodeEvalResult:
        """
        Evaluate code against a spec.

        Args:
            code: The Python code string to evaluate.
            spec: Natural language specification describing what the code should do.

        Returns:
            CodeEvalResult with dimension scores and severity-tagged findings.
        """
        findings = []

        # Syntax
        syntax_ok, syntax_err = _check_syntax(code)
        if not syntax_ok:
            findings.append(CodeFinding(
                dimension="syntax",
                severity="CRITICAL",
                message="Code has syntax errors and cannot be parsed.",
                evidence=syntax_err,
            ))

        # Spec compliance
        spec_ok, missing_spec = _check_spec_compliance(code, spec)
        if not spec_ok:
            findings.append(CodeFinding(
                dimension="spec_compliance",
                severity="HIGH",
                message="Code may not fully address the specification.",
                evidence=f"Possibly missing: {missing_spec[:5]}",
            ))

        # Edge cases
        edges_ok, edge_issues = _check_edge_cases(code)
        if not edges_ok:
            for issue in edge_issues:
                findings.append(CodeFinding(
                    dimension="edge_cases",
                    severity="HIGH",
                    message=f"Edge case issue: {issue}",
                ))

        # Error handling
        err_ok, err_issues = _check_error_handling(code)
        if not err_ok:
            for issue in err_issues:
                findings.append(CodeFinding(
                    dimension="error_handling",
                    severity="MEDIUM",
                    message=f"Error handling: {issue}",
                ))

        # Complexity
        complex_ok, complex_issues = _check_complexity(code)
        if not complex_ok:
            for issue in complex_issues:
                findings.append(CodeFinding(
                    dimension="complexity",
                    severity="MEDIUM",
                    message=f"Complexity concern: {issue}",
                ))

        # Documentation
        doc_ok, doc_issues = _check_documentation(code)
        if not doc_ok:
            for issue in doc_issues:
                findings.append(CodeFinding(
                    dimension="documentation",
                    severity="LOW",
                    message=f"Documentation: {issue}",
                ))

        # Score: start at 1.0, subtract per finding
        deductions = {"CRITICAL": 0.35, "HIGH": 0.15, "MEDIUM": 0.08, "LOW": 0.03}
        score = 1.0
        for f in findings:
            score -= deductions.get(f.severity, 0.05)
        score = max(0.0, min(1.0, score))

        criticals = [f for f in findings if f.severity == "CRITICAL"]
        highs = [f for f in findings if f.severity == "HIGH"]
        summary_parts = []
        if criticals:
            summary_parts.append(f"{len(criticals)} critical issue(s)")
        if highs:
            summary_parts.append(f"{len(highs)} high-severity issue(s)")
        if not findings:
            summary_parts.append("no significant issues found")
        summary = f"Score: {score:.2f}. " + "; ".join(summary_parts) + "."

        return CodeEvalResult(
            syntax_valid=syntax_ok,
            spec_compliance=spec_ok,
            edge_cases_handled=edges_ok,
            error_handling_present=err_ok,
            complexity_appropriate=complex_ok,
            documentation_present=doc_ok,
            findings=findings,
            overall_score=score,
            summary=summary,
        )

    def compare_solutions(
        self, solution_a: str, solution_b: str, spec: str
    ) -> SolutionComparison:
        """
        Compare two code solutions against the same spec.

        Returns:
            SolutionComparison with winner, reasoning, and strengths.
        """
        result_a = self.evaluate(solution_a, spec)
        result_b = self.evaluate(solution_b, spec)

        a_strengths = []
        b_strengths = []

        if result_a.syntax_valid and not result_b.syntax_valid:
            a_strengths.append("valid syntax")
        if result_b.syntax_valid and not result_a.syntax_valid:
            b_strengths.append("valid syntax")

        if result_a.error_handling_present and not result_b.error_handling_present:
            a_strengths.append("better error handling")
        if result_b.error_handling_present and not result_a.error_handling_present:
            b_strengths.append("better error handling")

        if result_a.edge_cases_handled and not result_b.edge_cases_handled:
            a_strengths.append("handles edge cases")
        if result_b.edge_cases_handled and not result_a.edge_cases_handled:
            b_strengths.append("handles edge cases")

        if result_a.documentation_present and not result_b.documentation_present:
            a_strengths.append("better documentation")
        if result_b.documentation_present and not result_a.documentation_present:
            b_strengths.append("better documentation")

        if result_a.overall_score > result_b.overall_score + 0.05:
            winner = "A"
            reasoning = f"Solution A scores {result_a.overall_score:.2f} vs B's {result_b.overall_score:.2f}."
        elif result_b.overall_score > result_a.overall_score + 0.05:
            winner = "B"
            reasoning = f"Solution B scores {result_b.overall_score:.2f} vs A's {result_a.overall_score:.2f}."
        else:
            winner = "TIE"
            reasoning = f"Both solutions score similarly (A: {result_a.overall_score:.2f}, B: {result_b.overall_score:.2f})."

        recommendation = (
            f"Prefer solution {winner}. "
            + (f"A strengths: {', '.join(a_strengths)}. " if a_strengths else "")
            + (f"B strengths: {', '.join(b_strengths)}." if b_strengths else "")
        ).strip()

        return SolutionComparison(
            solution_a_score=result_a.overall_score,
            solution_b_score=result_b.overall_score,
            winner=winner,
            reasoning=reasoning,
            a_strengths=a_strengths,
            b_strengths=b_strengths,
            recommendation=recommendation,
        )
