"""Tests for PromptInjector."""

import pytest
from redteaming.prompt_injector import PromptInjector, InjectionResult, SUPPORTED_TECHNIQUES


@pytest.fixture
def injector():
    return PromptInjector()


def test_generate_injections_returns_list(injector):
    results = injector.generate_injections("Tell me about dogs")
    assert isinstance(results, list)
    assert len(results) > 0


def test_generate_injections_all_techniques(injector):
    results = injector.generate_injections("Hello world", techniques=SUPPORTED_TECHNIQUES)
    assert len(results) == len(SUPPORTED_TECHNIQUES)


def test_injection_result_fields(injector):
    results = injector.generate_injections("Test prompt", techniques=["role_override"])
    r = results[0]
    assert isinstance(r, InjectionResult)
    assert r.original_prompt == "Test prompt"
    assert r.technique == "role_override"
    assert r.severity in ("HIGH", "MEDIUM", "LOW")
    assert len(r.injected_prompt) > len(r.original_prompt)
    assert r.expected_failure_mode


def test_injection_preserves_original_prompt(injector):
    base = "What is the capital of France?"
    results = injector.generate_injections(base, techniques=["instruction_ignore"])
    assert results[0].original_prompt == base


def test_unknown_technique_raises(injector):
    with pytest.raises(ValueError, match="Unknown technique"):
        injector.generate_injections("test", techniques=["nonexistent_attack"])


def test_batch_inject_length(injector):
    prompts = ["Prompt A", "Prompt B", "Prompt C"]
    results = injector.batch_inject(prompts, technique="delimiter_attack")
    assert len(results) == len(prompts)


def test_batch_inject_same_technique(injector):
    prompts = ["foo", "bar"]
    results = injector.batch_inject(prompts, technique="context_overflow")
    for r in results:
        assert r.technique == "context_overflow"


def test_to_dict_serializable(injector):
    results = injector.generate_injections("serialize me", techniques=["indirect_injection"])
    d = results[0].to_dict()
    assert "original_prompt" in d
    assert "injected_prompt" in d
    assert "technique" in d
    assert "severity" in d
