"""
adversarial-ai-redteaming: Tools for finding model failure modes,
designing adversarial prompts, and evaluating AI robustness.
"""

from .prompt_injector import PromptInjector, InjectionResult
from .edge_case_detector import EdgeCaseDetector, EdgeCaseResult, EdgeCaseScanReport
from .coding_evaluator import CodingEvaluator, CodeEvalResult, SolutionComparison
from .redteam_report import RedTeamReport

__version__ = "0.1.0"
__all__ = [
    "PromptInjector",
    "InjectionResult",
    "EdgeCaseDetector",
    "EdgeCaseResult",
    "EdgeCaseScanReport",
    "CodingEvaluator",
    "CodeEvalResult",
    "SolutionComparison",
    "RedTeamReport",
]
