# adversarial-ai-redteaming

After doing AI evaluation work I kept noticing that standard RLHF rating catches obvious quality issues but misses the subtle ones — the responses that look fine on first read but fall apart under adversarial pressure. This toolkit is how I practice finding those.

It covers three things I care about most in AI evaluation: generating adversarial prompt injections, scanning model outputs for edge case failures, and evaluating AI-generated code against specs with severity-tagged findings. Everything is composable and runs without any external API calls, so you can use it on any model's outputs.

## What It Does

**`PromptInjector`** — generates adversarial prompt variants using five attack techniques:
- `role_override` — convince the model it has a different identity
- `instruction_ignore` — instruct the model to disregard prior context
- `context_overflow` — bury instructions in noise to dilute attention
- `delimiter_attack` — exploit prompt formatting to break structure
- `indirect_injection` — embed instructions in data the model processes

**`EdgeCaseDetector`** — scans responses for failure modes that rating often misses: empty responses, truncated output, ignored instructions, hallucination patterns, format violations, safety bypass attempts, inconsistent reasoning.

**`CodingEvaluator`** — evaluates AI-generated code for syntax validity, spec compliance, edge case handling, error handling, complexity, and documentation. Produces severity-tagged findings (CRITICAL → broken output, HIGH → missing edge case, MEDIUM → no error handling, LOW → style).

**`RedTeamReport`** — aggregates all results into a single Markdown + JSON report with summary stats and recommendations.

## Quickstart

```bash
git clone https://github.com/LaelaZorana/adversarial-ai-redteaming
cd adversarial-ai-redteaming
pip install -r requirements.txt
```

**Generate injections:**
```python
from redteaming import PromptInjector

injector = PromptInjector()
results = injector.generate_injections(
    "Explain how neural networks work",
    techniques=["role_override", "instruction_ignore"]
)
for r in results:
    print(f"[{r.severity}] {r.technique}: {r.injected_prompt[:80]}...")
```

**Scan responses for edge cases:**
```python
from redteaming import EdgeCaseDetector

detector = EdgeCaseDetector()
pairs = [
    {"response": model_output, "prompt": original_prompt, "rubric": {"required_keywords": ["neural network"]}}
]
report = detector.scan_batch(pairs)
print(report.summary())
```

**Evaluate code:**
```python
from redteaming import CodingEvaluator

evaluator = CodingEvaluator()
result = evaluator.evaluate(code=some_code, spec="Write a function that sorts a list")
print(f"Score: {result.overall_score:.2f}")
for finding in result.findings:
    print(f"  [{finding.severity}] {finding.message}")
```

**CLI:**
```bash
python -m redteaming inject "Tell me about dogs" --techniques role_override,delimiter_attack
python -m redteaming scan examples/sample_prompts.jsonl
python -m redteaming evaluate-code examples/sample_code_eval.py spec.txt
```

**Run tests:**
```bash
python -m pytest tests/ -q
```

## Why Severity Matters

Not all findings are equal. I tag everything by severity so you can triage:

| Severity | Meaning | Example |
|----------|---------|---------|
| CRITICAL | Output is broken or non-functional | Syntax error in generated code |
| HIGH | Significant failure mode | Instruction ignored, safety bypass |
| MEDIUM | Quality issue worth fixing | Missing error handling, hallucination pattern |
| LOW | Style/polish | No docstring |

## About

Built for adversarial AI evaluation practice. I'm an applied ML and cloud engineer building production AI systems.

- GitHub: [github.com/LaelaZorana](https://github.com/LaelaZorana)
- HuggingFace: [huggingface.co/LaelaZ](https://huggingface.co/LaelaZ)
- Kaggle: [kaggle.com/laelazorana](https://www.kaggle.com/laelazorana)

MIT License.
