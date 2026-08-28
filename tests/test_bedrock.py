"""The Bedrock provider's guarantees, proved against a stubbed `converse()` client.

**Every test here passes whether or not boto3 is installed, and that is itself under test.** The
client is a hand-written stand-in, never the real one, and `_error_code` duck-types the AWS error
shape rather than importing botocore's exception type. boto3 is an optional extra
(pyproject.toml's `aws`), so both states are normal and a test that only passes in one of them is
broken -- which happened: the missing-boto3 test originally *assumed* absence, and flipped to
failing the moment `uv sync --extra aws` ran. It now simulates absence via `sys.modules`.

What this buys: Converse translation is correct in both directions, cost is a projection from a
price table rather than a charged figure, the `us.` inference-profile prefix is applied to the
vendor that needs it and only that vendor, retry is bounded and selective, and constructing a
provider is free. What it does not buy: nothing here calls real Bedrock, so nothing here says a
real `converse()` call would accept the shapes this file asserts -- that is only provable with a
keyed run.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any

import pytest

import earshot
from earshot.llm.base import Completion, ModelConfig, ProviderError, ToolCall, Usage
from earshot.llm.bedrock import (
    DEFAULT_BEDROCK_MODEL,
    PRICE_PER_1M_TOKENS,
    BedrockProvider,
    LazyBedrockProvider,
    MissingBoto3,
    _cost,
    _wire_messages,
    _wire_tools,
    normalize_model_id,
)

HAIKU = DEFAULT_BEDROCK_MODEL


class FakeConverseClient:
    """Stands in for the boto3 bedrock-runtime client. No network, no credentials, no boto3.

    Replays queued responses (or raises queued exceptions) in order, and records every request
    `BedrockProvider.complete()` sent, so a test can inspect the wire shape without a real client.
    """

    def __init__(self, responses: list[Any]) -> None:
        self._responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    def converse(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(kwargs)
        item = self._responses.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item


class FakeClientError(Exception):
    """Stands in for `botocore.exceptions.ClientError` without importing botocore.

    `bedrock.py` deliberately duck-types on `.response["Error"]["Code"]` (see `_error_code`'s
    docstring) instead of `isinstance`-checking the real class, specifically so a stub this thin
    is enough and botocore never has to be installed to test retry behaviour.
    """

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.response = {"Error": {"Code": code}}


def converse_response(
    *,
    text: str = "",
    tool_uses: list[dict[str, Any]] | None = None,
    input_tokens: int = 100,
    output_tokens: int = 20,
) -> dict[str, Any]:
    blocks: list[dict[str, Any]] = []
    if text:
        blocks.append({"text": text})
    for tool_use in tool_uses or []:
        blocks.append({"toolUse": tool_use})
    return {
        "output": {"message": {"role": "assistant", "content": blocks}},
        "stopReason": "tool_use" if tool_uses else "end_turn",
        "usage": {"inputTokens": input_tokens, "outputTokens": output_tokens},
    }


# --- message translation, OpenAI-shaped -> Converse ----------------------------------------


def test_a_system_message_is_hoisted_into_the_separate_system_param() -> None:
    system, converse = _wire_messages(
        [
            {"role": "system", "content": "You are a careful reader."},
            {"role": "user", "content": "hello"},
        ]
    )
    assert system == [{"text": "You are a careful reader."}]
    assert converse == [{"role": "user", "content": [{"text": "hello"}]}]


def test_an_assistant_tool_call_becomes_a_touluse_block_with_dict_input() -> None:
    messages = [
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {"name": "get_ledger_summary", "arguments": {"customer_id": "C1"}},
                }
            ],
        }
    ]
    _, converse = _wire_messages(messages)
    assert converse == [
        {
            "role": "assistant",
            "content": [
                {
                    "toolUse": {
                        "toolUseId": "call_1",
                        "name": "get_ledger_summary",
                        "input": {"customer_id": "C1"},
                    }
                }
            ],
        }
    ]


def test_an_assistant_tool_call_carries_no_empty_text_block() -> None:
    """Converse rejects an empty `text` content block; `assistant_message()` (base.py) sets
    `content: completion.content or ""`, so a tool-calling turn's text is always ""."""
    messages = [
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {"id": "c1", "type": "function", "function": {"name": "t", "arguments": {}}}
            ],
        }
    ]
    _, converse = _wire_messages(messages)
    assert all("text" not in block for block in converse[0]["content"])


def test_consecutive_tool_result_messages_merge_into_one_converse_user_turn() -> None:
    """Load-bearing: Converse rejects two consecutive same-role messages, and
    `agent/investigator.py` appends one `{"role": "tool", ...}` message per call when a step
    makes several tool calls at once."""
    messages = [
        {"role": "tool", "tool_call_id": "call_1", "name": "get_ledger_summary", "content": "{}"},
        {"role": "tool", "tool_call_id": "call_2", "name": "get_account_state", "content": "{}"},
    ]
    _, converse = _wire_messages(messages)
    assert len(converse) == 1
    assert converse[0]["role"] == "user"
    assert [b["toolResult"]["toolUseId"] for b in converse[0]["content"]] == ["call_1", "call_2"]


def test_a_full_transcript_alternates_roles_after_translation() -> None:
    """The property Converse actually enforces: no two consecutive messages share a role. Built
    from the exact message shapes `agent/investigator.py`'s loop produces over one step."""
    messages = [
        {"role": "system", "content": "sys"},
        {"role": "user", "content": "go"},
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {"id": "c1", "type": "function", "function": {"name": "t1", "arguments": {}}},
                {"id": "c2", "type": "function", "function": {"name": "t2", "arguments": {}}},
            ],
        },
        {"role": "tool", "tool_call_id": "c1", "name": "t1", "content": "{}"},
        {"role": "tool", "tool_call_id": "c2", "name": "t2", "content": "{}"},
        {"role": "assistant", "content": "final answer"},
    ]
    _, converse = _wire_messages(messages)
    roles = [m["role"] for m in converse]
    assert roles == ["user", "assistant", "user", "assistant"]
    assert all(a != b for a, b in zip(roles, roles[1:])), "two consecutive turns share a role"


# --- tool spec translation -------------------------------------------------------------------


def test_a_tool_spec_translates_to_toolspec_with_input_schema() -> None:
    spec = {
        "type": "function",
        "function": {
            "name": "get_ledger_summary",
            "description": "Read the ledger.",
            "parameters": {
                "type": "object",
                "properties": {"customer_id": {"type": "string"}},
                "required": ["customer_id"],
                "additionalProperties": False,
            },
        },
    }
    assert _wire_tools([spec]) == [
        {
            "toolSpec": {
                "name": "get_ledger_summary",
                "description": "Read the ledger.",
                "inputSchema": {"json": spec["function"]["parameters"]},
            }
        }
    ]


def test_the_real_tool_registry_translates_without_error() -> None:
    """Against the actual specs the investigator sends, not a hand-built stand-in."""
    from earshot.agent.tools import tool_specs

    specs = tool_specs()
    wired = _wire_tools(specs)
    assert len(wired) == len(specs)
    names = {t["toolSpec"]["name"] for t in wired}
    assert "get_ledger_summary" in names
    assert all(t["toolSpec"]["inputSchema"]["json"] for t in wired)


# --- tool_use response -> ToolCall, through complete() ---------------------------------------


def test_a_tool_use_response_produces_a_toolcall_with_dict_arguments() -> None:
    client = FakeConverseClient(
        [
            converse_response(
                tool_uses=[
                    {"toolUseId": "call_9", "name": "get_account_state", "input": {"customer_id": "C1"}}
                ]
            )
        ]
    )
    provider = BedrockProvider(client=client)
    completion = provider.complete([{"role": "user", "content": "go"}], [], ModelConfig(model=HAIKU))

    assert completion.tool_calls == (
        ToolCall(id="call_9", name="get_account_state", arguments={"customer_id": "C1"}),
    )
    assert completion.content == ""
    assert isinstance(completion, Completion)


def test_a_string_tool_input_is_parsed_as_json_defensively() -> None:
    """boto3 deserialises Converse's `input` document to a dict already; guarded anyway in case
    a stub -- or a future botocore version -- hands back a JSON string instead."""
    client = FakeConverseClient(
        [converse_response(tool_uses=[{"toolUseId": "c1", "name": "t", "input": '{"a": 1}'}])]
    )
    provider = BedrockProvider(client=client)
    completion = provider.complete([{"role": "user", "content": "go"}], [], ModelConfig(model=HAIKU))
    assert completion.tool_calls[0].arguments == {"a": 1}


# --- cost: computed, never charged ------------------------------------------------------------


def test_cost_is_computed_from_the_price_table() -> None:
    client = FakeConverseClient([converse_response(text="ok", input_tokens=1000, output_tokens=500)])
    provider = BedrockProvider(client=client)
    completion = provider.complete([{"role": "user", "content": "go"}], [], ModelConfig(model=HAIKU))

    price_in, price_out = PRICE_PER_1M_TOKENS["anthropic.claude-haiku-4-5-20251001-v1:0"]
    expected = round(1000 / 1_000_000 * price_in + 500 / 1_000_000 * price_out, 6)
    assert completion.cost_usd == pytest.approx(expected)
    assert completion.cost_usd > 0.0


def test_cost_lookup_works_whether_or_not_the_us_prefix_was_applied() -> None:
    """The price table is keyed on the bare id; the request is sent with the prefixed one."""
    usage = Usage(prompt_tokens=1_000_000, completion_tokens=0)
    assert _cost("us.anthropic.claude-haiku-4-5-20251001-v1:0", usage) == pytest.approx(1.00)
    assert _cost("anthropic.claude-haiku-4-5-20251001-v1:0", usage) == pytest.approx(1.00)


def test_an_unpriced_model_id_reports_zero_cost_not_a_guess() -> None:
    client = FakeConverseClient([converse_response(text="ok", input_tokens=1000, output_tokens=500)])
    provider = BedrockProvider(client=client)
    completion = provider.complete(
        [{"role": "user", "content": "go"}], [], ModelConfig(model="cohere.command-r-v1:0")
    )
    assert completion.cost_usd == 0.0


# --- the `us.` inference-profile prefix ------------------------------------------------------


@pytest.mark.parametrize(
    "bare,expected",
    [
        (
            "anthropic.claude-haiku-4-5-20251001-v1:0",
            "us.anthropic.claude-haiku-4-5-20251001-v1:0",
        ),
        (
            "anthropic.claude-sonnet-4-5-20250929-v1:0",
            "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        ),
    ],
)
def test_anthropic_ids_get_the_us_prefix(bare: str, expected: str) -> None:
    assert normalize_model_id(bare) == expected


@pytest.mark.parametrize(
    "bare", ["amazon.nova-lite-v1:0", "amazon.nova-micro-v1:0", "meta.llama3-8b-instruct-v1:0"]
)
def test_amazon_and_meta_ids_are_left_bare(bare: str) -> None:
    """The bare id, not the `us.`-prefixed one -- prefixing an on-demand model fails just as
    hard as not prefixing an inference-profile one, the other direction of the same bug."""
    assert normalize_model_id(bare) == bare


def test_normalization_is_idempotent() -> None:
    prefixed = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
    assert normalize_model_id(prefixed) == prefixed


def test_default_model_is_haiku_not_sonnet() -> None:
    assert DEFAULT_BEDROCK_MODEL == "us.anthropic.claude-haiku-4-5-20251001-v1:0"
    assert "sonnet" not in DEFAULT_BEDROCK_MODEL.lower()


def test_an_unconfigured_model_cfg_resolves_to_the_bedrock_default_not_the_openrouter_one() -> None:
    """`ModelConfig()` carries base.py's OpenRouter-shaped default -- meaningless to Bedrock's
    Converse API. A caller that never overrode `model_cfg.model` must still reach Haiku 4.5."""
    client = FakeConverseClient([converse_response(text="ok")])
    provider = BedrockProvider(client=client)
    provider.complete([{"role": "user", "content": "go"}], [], ModelConfig())
    assert client.calls[0]["modelId"] == DEFAULT_BEDROCK_MODEL


# --- bounded, selective retry ------------------------------------------------------------------


def test_retries_on_throttling_then_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("earshot.llm.bedrock.time.sleep", lambda seconds: None)
    client = FakeConverseClient(
        [
            FakeClientError("ThrottlingException"),
            FakeClientError("ThrottlingException"),
            converse_response(text="ok"),
        ]
    )
    provider = BedrockProvider(client=client, max_attempts=3)
    completion = provider.complete([{"role": "user", "content": "go"}], [], ModelConfig(model=HAIKU))
    assert completion.content == "ok"
    assert len(client.calls) == 3


def test_gives_up_after_max_attempts_of_throttling(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("earshot.llm.bedrock.time.sleep", lambda seconds: None)
    client = FakeConverseClient([FakeClientError("ThrottlingException")] * 3)
    provider = BedrockProvider(client=client, max_attempts=3)
    with pytest.raises(ProviderError):
        provider.complete([{"role": "user", "content": "go"}], [], ModelConfig(model=HAIKU))
    assert len(client.calls) == 3


@pytest.mark.parametrize(
    "code", ["ModelTimeoutException", "ServiceUnavailableException", "ThrottlingException"]
)
def test_every_named_retryable_code_is_retried(monkeypatch: pytest.MonkeyPatch, code: str) -> None:
    monkeypatch.setattr("earshot.llm.bedrock.time.sleep", lambda seconds: None)
    client = FakeConverseClient([FakeClientError(code), converse_response(text="ok")])
    provider = BedrockProvider(client=client, max_attempts=2)
    completion = provider.complete([{"role": "user", "content": "go"}], [], ModelConfig(model=HAIKU))
    assert completion.content == "ok"


def test_a_non_retryable_client_error_is_not_retried() -> None:
    """Retry those, not everything: a validation error must fail on the first attempt, not
    consume the retry budget on something that will never succeed."""
    client = FakeConverseClient(
        [FakeClientError("ValidationException"), converse_response(text="should not be reached")]
    )
    provider = BedrockProvider(client=client, max_attempts=3)
    with pytest.raises(ProviderError):
        provider.complete([{"role": "user", "content": "go"}], [], ModelConfig(model=HAIKU))
    assert len(client.calls) == 1, "a non-retryable error must not consume a retry attempt"


# --- lazy construction: no client, no boto3, until actually used -----------------------------


def test_constructing_the_provider_builds_no_client() -> None:
    provider = BedrockProvider()
    assert provider._boto_client is None

    lazy = LazyBedrockProvider()
    assert lazy._inner is None


def test_a_lazy_provider_builds_its_inner_only_on_first_complete() -> None:
    client = FakeConverseClient([converse_response(text="ok")])
    lazy = LazyBedrockProvider(client=client)
    assert lazy._inner is None

    lazy.complete([{"role": "user", "content": "go"}], [], ModelConfig(model=HAIKU))
    assert lazy._inner is not None
    assert lazy._inner._boto_client is client


def test_constructing_and_importing_need_no_boto3() -> None:
    """Construction is free: no client, no credentials, no import of the optional extra.

    This says nothing about whether boto3 is installed here, because it cannot: `uv sync --extra
    aws` installs it and a plain `uv sync` does not, so both states are normal and an assertion
    about which one is running is an assertion about the machine. The docstring here used to
    claim the environment had no boto3, which was false in any venv synced with the extra -- and
    a test that states a fact about its own environment states it in the one place nothing checks.

    What makes the keyless claim true is two tests further down: the AST scan over every module
    in the package, and the import of every module with boto3 blocked outright.
    """
    provider = BedrockProvider()  # must not raise
    assert provider._boto_client is None


def test_using_the_provider_without_boto3_raises_a_clear_error_only_then(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """boto3's absence is SIMULATED, not assumed.

    This test used to just call `complete()` and expect the import to fail, which passed only
    because the dev venv happened to have no boto3. `uv sync --extra aws` installs it and the
    test flipped to failing -- an environment-dependent test that proves nothing about the code.
    Blocking the name in `sys.modules` makes `import boto3` raise ImportError either way.
    """
    monkeypatch.setitem(sys.modules, "boto3", None)
    provider = BedrockProvider()  # no injected client -- forces the real boto3 import attempt
    with pytest.raises(MissingBoto3, match="boto3"):
        provider.complete([{"role": "user", "content": "go"}], [], ModelConfig(model=HAIKU))


# --- the keyless guarantee, over the WHOLE package ---------------------------------------------
#
# Discovered, not listed. This started as two hand-written checks, one for `llm/bedrock.py` and
# one for `aws/stores.py`, while `aws/ingest.py`, `aws/transcripts.py` and `llm/select.py` were
# lazy by care alone -- a module-level `import boto3` in any of the three breaks a fresh keyless
# clone with every test green in a dev venv that happens to have the extra installed.

EAR = Path(earshot.__file__).resolve().parent
PACKAGE_MODULES = sorted(p.relative_to(EAR).as_posix() for p in EAR.rglob("*.py"))
OPTIONAL_EXTRAS = {"boto3", "botocore"}


def test_the_package_module_discovery_is_not_empty() -> None:
    """If the glob stops matching, both guards below pass by scanning nothing."""
    assert len(PACKAGE_MODULES) >= 20, (
        f"discovery found only {PACKAGE_MODULES} — the keyless guard covers nothing"
    )


@pytest.mark.parametrize("module", PACKAGE_MODULES)
def test_boto3_is_never_imported_at_module_level(module: str) -> None:
    """The static half. Checked by AST rather than by `sys.modules`, so it catches the regression
    in a dev environment that happens to have boto3 installed -- where an import-succeeded check
    would prove nothing. A deferred import inside a function is the supported pattern and passes.
    """
    tree = ast.parse((EAR / module).read_text(encoding="utf-8"))
    for node in tree.body:  # module top level only; a deferred import inside a function is fine
        if isinstance(node, ast.Import):
            names = {alias.name.split(".")[0] for alias in node.names}
            assert not names & OPTIONAL_EXTRAS, f"{module} imports boto3/botocore at module level"
        if isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            assert root not in OPTIONAL_EXTRAS, f"{module} imports boto3/botocore at module level"


def test_every_module_imports_with_boto3_blocked() -> None:
    """The behavioural half, and the one that actually holds (A6).

    The AST scan sees import statements. It does not see `importlib.import_module("boto3")` at
    module scope, a module-level call into a helper that imports it, or a package `__init__`
    pulling in a submodule that does. So this blocks `boto3` and `botocore` at `sys.meta_path`
    -- they raise ImportError however they are reached -- and imports every module in the
    package. That is the fresh-clone claim executed rather than asserted.

    Run in a subprocess because a meta_path blocker and a torn-down `sys.modules` are not state
    to hand back to the rest of the session.
    """
    import json
    import subprocess

    script = """
import importlib, json, sys
from pathlib import Path


class Blocker:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in {"boto3", "botocore"}:
            raise ImportError(f"{fullname} is not installed on a fresh clone")
        return None


for name in [m for m in sys.modules if m.split(".")[0] in {"boto3", "botocore"}]:
    del sys.modules[name]
sys.meta_path.insert(0, Blocker())

import earshot

root = Path(earshot.__file__).resolve().parent
failures = {}
for path in sorted(root.rglob("*.py")):
    parts = path.relative_to(root).with_suffix("").parts
    if parts[-1] == "__init__":
        parts = parts[:-1]
    name = ".".join(("earshot",) + parts)
    try:
        importlib.import_module(name)
    except Exception as exc:
        failures[name] = f"{type(exc).__name__}: {exc}"
print(json.dumps(failures))
"""
    completed = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, check=True
    )
    failures = json.loads(completed.stdout.strip().splitlines()[-1])
    assert not failures, (
        f"these modules cannot be imported without boto3 installed: {failures}. "
        f"`earshot[aws]` is optional and must stay optional -- a fresh clone runs every test "
        f"keyless, and that is only true while every boto3 import is deferred to first use."
    )


# --- region -----------------------------------------------------------------------------------


def test_region_defaults_to_us_east_1() -> None:
    """Every model ARN, `us.` profile id and price in the docs is us-east-1 (D-022); the client
    must default to the same region rather than boto3's ambient config."""
    assert BedrockProvider()._region == "us-east-1"


def test_region_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EARSHOT_BEDROCK_REGION", "us-west-2")
    assert BedrockProvider()._region == "us-west-2"
