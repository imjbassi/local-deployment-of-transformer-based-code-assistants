#!/usr/bin/env python3
"""Run the preregistered prompt and 8-bit ablations for Qwen2.5-Coder-1.5B.

``EXPERIMENT_PLAN.md`` limits both ablations to Qwen2.5-Coder-1.5B at seed 11
and keeps every other sampling parameter at the reference condition: 20 samples
per task, temperature 0.2, top-p 0.95, 512 new tokens, and the pinned EvalPlus
0.3.1 generation path.

Each condition changes exactly one factor from that reference:

``chat-prompt``
    Stops forcing the base prompt. Qwen2.5-Coder-1.5B ships a chat template, so
    EvalPlus builds its instruction-style prompt and the completion is returned
    without the prompt prefix. The primary condition forces base mode precisely
    to exclude this path, so the ablation measures what that choice is worth.

``int8``
    Loads the same revision with bitsandbytes 8-bit weights instead of BF16.
    Everything else, including the prompt and stop texts, is unchanged.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
from pathlib import Path

from evalplus.codegen import codegen
from evalplus.provider import make_model
from huggingface_hub import snapshot_download
from primary_codegen import install_non_accumulating_codegen

REPOSITORY = Path(__file__).resolve().parents[1]
TARGETS = REPOSITORY / "protocol" / "published_targets.json"
OUTPUT_ROOT = REPOSITORY / "results" / "controls" / "qwen-secondary-ablations"
MODEL_KEY = "qwen2.5-coder-1.5b"
N_SAMPLES = 20
TEMPERATURE = 0.2
TOP_P = 0.95
MAX_NEW_TOKENS = 512

# EvalPlus 0.3.1 uses these defaults for its non-"-E" / non-reasoning chat path
# (evalplus/codegen.py, run_codegen). They are reproduced verbatim so the
# ablation uses the evaluator's own instruction prompt.
INSTRUCTION_PREFIX = (
    "Please provide a self-contained Python script that solves the following "
    "problem in a markdown code block:"
)
RESPONSE_PREFIX = (
    "Below is a Python script with a self-contained function that solves the "
    "problem and passes corresponding tests:"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--condition", required=True, choices=("chat-prompt", "int8"))
    parser.add_argument("--seed", type=int, default=11)
    parser.add_argument("--batch-size", type=int, default=20)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--id-range",
        nargs=2,
        type=int,
        metavar=("START", "END"),
        help="Optional half-open HumanEval task range used for a probe run.",
    )
    return parser.parse_args()


def install_int8_loading() -> str:
    """Load the checkpoint with bitsandbytes 8-bit weights.

    EvalPlus's provider has no quantization argument, so we wrap the model
    loader it calls and add only ``quantization_config``.
    """
    import transformers
    from transformers import BitsAndBytesConfig

    original_from_pretrained = transformers.AutoModelForCausalLM.from_pretrained

    def from_pretrained(name, *args, **kwargs):
        kwargs["quantization_config"] = BitsAndBytesConfig(load_in_8bit=True)
        model = original_from_pretrained(name, *args, **kwargs)
        # bitsandbytes places the model during loading and rejects a later
        # ``.to(device)``, which the EvalPlus provider always calls. Accept that
        # call as a no-op instead of patching the provider itself.
        model.to = lambda *args, **kwargs: model
        return model

    transformers.AutoModelForCausalLM.from_pretrained = from_pretrained
    return importlib.metadata.version("bitsandbytes")


def main() -> None:
    args = parse_args()
    version = importlib.metadata.version("evalplus")
    if version != "0.3.1":
        raise RuntimeError(f"Expected EvalPlus 0.3.1, found {version}")

    import torch
    from evalplus.provider.hf import HuggingFaceDecoder

    install_non_accumulating_codegen(HuggingFaceDecoder)
    bitsandbytes_version = install_int8_loading() if args.condition == "int8" else None

    targets = json.loads(TARGETS.read_text(encoding="utf-8"))["models"]
    target = next(item for item in targets if item["key"] == MODEL_KEY)
    snapshot = snapshot_download(repo_id=target["model_id"], revision=target["revision"])

    default = OUTPUT_ROOT / f"{MODEL_KEY}-{args.condition}-seed{args.seed}.jsonl"
    output = (args.output or default).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    force_base_prompt = args.condition != "chat-prompt"
    model = make_model(
        model=snapshot,
        backend="hf",
        batch_size=args.batch_size,
        temperature=TEMPERATURE,
        force_base_prompt=force_base_prompt,
        dataset="humaneval",
        attn_implementation="eager",
        dtype="bfloat16",
        instruction_prefix=INSTRUCTION_PREFIX,
        response_prefix=RESPONSE_PREFIX,
    )
    model.eos = list(dict.fromkeys(model.eos))
    model.max_new_tokens = MAX_NEW_TOKENS

    if args.condition == "chat-prompt" and model.is_direct_completion():
        raise RuntimeError("the chat-prompt ablation requires a tokenizer chat template")
    if args.condition == "int8":
        quantized = getattr(model.model, "is_loaded_in_8bit", False)
        if not quantized:
            raise RuntimeError("the int8 ablation did not load 8-bit weights")

    metadata = {
        "experiment": f"qwen_secondary_{args.condition.replace('-', '_')}",
        "preregistered": True,
        "post_hoc": False,
        "evalplus_version": version,
        "dataset": "humaneval",
        "dataset_version": "v0.1.10",
        "model_key": MODEL_KEY,
        "model_id": target["model_id"],
        "model_revision": target["revision"],
        "greedy": False,
        "n_samples": N_SAMPLES,
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
        "seed": args.seed,
        "batch_size": args.batch_size,
        "max_new_tokens": MAX_NEW_TOKENS,
        "condition": args.condition,
        "changed_factor": (
            "force_base_prompt=False (EvalPlus chat-template prompt)"
            if args.condition == "chat-prompt"
            else "bitsandbytes 8-bit weights instead of BF16"
        ),
        "dtype": "int8" if args.condition == "int8" else "bfloat16",
        "bitsandbytes_version": bitsandbytes_version,
        "force_base_prompt": force_base_prompt,
        "direct_completion": model.is_direct_completion(),
        "generation_path": "stock_stop_criteria_with_hook_restoration",
        "stop_texts": list(model.eos),
        "id_range": args.id_range,
        "output": str(output),
        "seed_note": (
            "The seed is applied once before generation, so only uninterrupted "
            "runs are reported."
        ),
    }
    output.with_suffix(".metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )

    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    codegen(
        target_path=str(output),
        model=model,
        dataset="humaneval",
        greedy=False,
        n_samples=N_SAMPLES,
        id_range=tuple(args.id_range) if args.id_range else None,
        version="v0.1.10",
        resume=True,
    )


if __name__ == "__main__":
    main()
