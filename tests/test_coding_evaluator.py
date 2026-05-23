"""Tests for CodingEvaluator."""

import pytest
from redteaming.coding_evaluator import CodingEvaluator, CodeEvalResult, SolutionComparison


@pytest.fixture
def evaluator():
    return CodingEvaluator()


GOOD_CODE = '''
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together and return the result."""
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Both arguments must be numbers")
    return a + b
'''

BAD_CODE = "def foo( x y: return x+y"  # syntax error

FLAWED_CODE = '''
def process(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result
'''

SPEC_ADD = "Write a function that adds two numbers and returns the sum."


def test_evaluate_good_code(evaluator):
    result = evaluator.evaluate(GOOD_CODE, SPEC_ADD)
    assert isinstance(result, CodeEvalResult)
    assert result.syntax_valid is True
    assert result.overall_score > 0.5


def test_evaluate_syntax_error(evaluator):
    result = evaluator.evaluate(BAD_CODE, SPEC_ADD)
    assert result.syntax_valid is False
    criticals = [f for f in result.findings if f.severity == "CRITICAL"]
    assert len(criticals) > 0


def test_evaluate_score_range(evaluator):
    result = evaluator.evaluate(GOOD_CODE, SPEC_ADD)
    assert 0.0 <= result.overall_score <= 1.0


def test_evaluate_returns_summary(evaluator):
    result = evaluator.evaluate(GOOD_CODE, SPEC_ADD)
    assert isinstance(result.summary, str)
    assert "Score" in result.summary


def test_evaluate_missing_error_handling(evaluator):
    result = evaluator.evaluate(FLAWED_CODE, "Process a list of items")
    # Should flag missing error handling
    assert result.error_handling_present is False


def test_compare_solutions_winner(evaluator):
    comparison = evaluator.compare_solutions(GOOD_CODE, BAD_CODE, SPEC_ADD)
    assert isinstance(comparison, SolutionComparison)
    assert comparison.winner in ("A", "B", "TIE")
    assert comparison.solution_a_score > comparison.solution_b_score


def test_compare_solutions_has_reasoning(evaluator):
    comparison = evaluator.compare_solutions(GOOD_CODE, FLAWED_CODE, SPEC_ADD)
    assert isinstance(comparison.reasoning, str)
    assert len(comparison.reasoning) > 0


def test_evaluate_to_dict(evaluator):
    result = evaluator.evaluate(GOOD_CODE, SPEC_ADD)
    d = result.to_dict()
    assert "syntax_valid" in d
    assert "overall_score" in d
    assert "findings" in d
    assert isinstance(d["findings"], list)
