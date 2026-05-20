"""
CLI entry point for adversarial-ai-redteaming.

Usage:
    python -m redteaming inject "<prompt>"
    python -m redteaming inject "<prompt>" --techniques role_override,instruction_ignore
    python -m redteaming scan responses.jsonl
    python -m redteaming evaluate-code code.py spec.txt
    python -m redteaming report results.jsonl
"""

import sys
import json
import argparse
from pathlib import Path

from .prompt_injector import PromptInjector, SUPPORTED_TECHNIQUES
from .edge_case_detector import EdgeCaseDetector
from .coding_evaluator import CodingEvaluator
from .redteam_report import RedTeamReport


def cmd_inject(args):
    injector = PromptInjector()
    techniques = args.techniques.split(",") if args.techniques else None
    results = injector.generate_injections(args.prompt, techniques=techniques)
    for r in results:
        print(json.dumps(r.to_dict(), indent=2))


def cmd_scan(args):
    path = Path(args.file)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    pairs = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                pairs.append(json.loads(line))

    detector = EdgeCaseDetector()
    report = detector.scan_batch(pairs)
    print(report.summary())


def cmd_evaluate_code(args):
    code_path = Path(args.code)
    spec_path = Path(args.spec)
    if not code_path.exists():
        print(f"Error: code file not found: {code_path}", file=sys.stderr)
        sys.exit(1)
    if not spec_path.exists():
        print(f"Error: spec file not found: {spec_path}", file=sys.stderr)
        sys.exit(1)

    code = code_path.read_text()
    spec = spec_path.read_text()
    evaluator = CodingEvaluator()
    result = evaluator.evaluate(code, spec)
    print(json.dumps(result.to_dict(), indent=2))


def cmd_report(args):
    path = Path(args.file)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(path.read_text())
    report = RedTeamReport(title="Red Team Evaluation Report")
    print(report.to_markdown())


def main():
    parser = argparse.ArgumentParser(
        prog="python -m redteaming",
        description="Adversarial AI red-teaming toolkit",
    )
    subparsers = parser.add_subparsers(dest="command")

    # inject
    inject_parser = subparsers.add_parser("inject", help="Generate prompt injections")
    inject_parser.add_argument("prompt", help="Base prompt to inject")
    inject_parser.add_argument(
        "--techniques",
        help=f"Comma-separated techniques. Options: {','.join(SUPPORTED_TECHNIQUES)}",
        default=None,
    )

    # scan
    scan_parser = subparsers.add_parser("scan", help="Scan responses for edge cases")
    scan_parser.add_argument("file", help="JSONL file with response/prompt pairs")

    # evaluate-code
    eval_parser = subparsers.add_parser("evaluate-code", help="Evaluate code against a spec")
    eval_parser.add_argument("code", help="Path to Python code file")
    eval_parser.add_argument("spec", help="Path to spec text file")

    # report
    report_parser = subparsers.add_parser("report", help="Generate report from results JSON")
    report_parser.add_argument("file", help="Path to results JSON file")

    args = parser.parse_args()

    if args.command == "inject":
        cmd_inject(args)
    elif args.command == "scan":
        cmd_scan(args)
    elif args.command == "evaluate-code":
        cmd_evaluate_code(args)
    elif args.command == "report":
        cmd_report(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
