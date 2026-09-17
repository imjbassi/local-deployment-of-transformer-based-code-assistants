#!/usr/bin/env python3
"""Run the post-hoc trailing-newline prompt ablation for one primary checkpoint."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
from functools import wraps
from pathlib import Path

from evalplus.codegen import codegen
from evalplus.provider import make_model
from huggingface_hub import snapshot_download
from primary_codegen import install_non_accumulating_codegen

REPOSITORY = Path(__file__).resolve().parents[1]
TARGETS = REPOSITORY / "protocol" / "published_targets.json"
OUTPUT_ROOT = REPOSITORY / "results" / "controls" / "prompt-newline-ablation"
REMOVED_SUFFIX = "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the stock EvalPlus primary condition for one checkpoint while "
            "removing only the trailing newline EvalPlus appends to the model prompt."
        )
    )
    parser.add_argument("--model", default="starcoder2-3b", help="Primary target key.")
    parser.add_argument(
        "--output",
        type=Path,
        help="Sanitized JSONL path; defaults to <results>/<model>-no-trailing-newline.jsonl.",
    )
    parser.add_argument(
        "--id-range",
        nargs=2,
        type=int,
        metavar=("START", "END"),
        help="Optional half-open HumanEval task range used for a probe run.",
    )
    return parser.parse_args()


def install_prompt_suffix_removal(decoder_class: type) -> None:
    """Remove EvalPlus's appended newline from the model input only.

    EvalPlus 0.3.1 builds ``task["prompt"].strip() + "\\n"``. The stored raw
    solution remains ``prompt + completion``, so sanitization and evaluation are
    unchanged apart from the completion the model produces.
    """
    original_codegen = decoder_class.codegen

    @wraps(original_codegen)
    def codegen_without_suffix(decoder, prompt, *args, **kwargs):
        if not prompt.endswith(REMOVED_SUFFIX):
            raise RuntimeError("EvalPlus prompt no longer ends with the expected newline")
        return original_codegen(decoder, prompt[: -len(REMOVED_SUFFIX)], *args, **kwargs)

    decoder_class.codegen = codegen_without_suffix


def main() -> None:
    args = parse_args()
    version = importlib.metadata.version("evalplus")
    if version != "0.3.1":
        raise RuntimeError(f"Expected EvalPlus 0.3.1, found {version}")

    import stop_sequencer.stop_sequencer as stop_module
    from evalplus.provider.hf import HuggingFaceDecoder
    from transformers import StoppingCriteria

    class DecodeOnceStopCriteria(StoppingCriteria):
        """Exact batch-one EvalPlus predicate with one decode per token."""

        def __init__(self, model_type, tokenizer, stop_texts, input_length, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.model_type = model_type
            self.tokenizer = tokenizer
            self.stop_texts = stop_texts
            self.input_length = input_length

        def __call__(self, input_ids, scores, **kwargs):
            del scores, kwargs
            if input_ids.shape[0] != 1:
                raise RuntimeError("the optimized stop criterion requires batch size one")
            token_ids = input_ids[0].long().tolist()
            if self.model_type == "causal":
                token_ids = token_ids[self.input_length :]
            decoded = self.tokenizer.decode(token_ids)
            return any(text in decoded for text in self.stop_texts)

    stop_module.StopSequenceCriteria = DecodeOnceStopCriteria
    install_non_accumulating_codegen(HuggingFaceDecoder)
    install_prompt_suffix_removal(HuggingFaceDecoder)

    targets = json.loads(TARGETS.read_text(encoding="utf-8"))["models"]
    target = next((item for item in targets if item["key"] == args.model), None)
    if target is None:
        raise ValueError(f"unknown model key: {args.model}")
    snapshot = snapshot_download(repo_id=target["model_id"], revision=target["revision"])

    output = (args.output or OUTPUT_ROOT / f"{args.model}-no-trailing-newline.jsonl").resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    model = make_model(
        model=snapshot,
        backend="hf",
        batch_size=1,
        temperature=0.0,
        force_base_prompt=True,
        dataset="humaneval",
        attn_implementation="eager",
        dtype="bfloat16",
    )
    model.eos = list(dict.fromkeys(model.eos))

    metadata = {
        "experiment": "no_trailing_prompt_newline",
        "model_key": args.model,
        "post_hoc": True,
        "evalplus_version": version,
        "dataset": "humaneval",
        "dataset_version": "v0.1.10",
        "model_id": target["model_id"],
        "model_revision": target["revision"],
        "greedy": True,
        "n_samples": 1,
        "max_new_tokens": 512,
        "dtype": "bfloat16",
        "force_base_prompt": True,
        "generation_path": "verified_primary_decode_once_with_hook_restoration",
        "model_prompt": 'task["prompt"].strip()',
        "stock_model_prompt": 'task["prompt"].strip() + "\\n"',
        "stop_texts": list(model.eos),
        "id_range": args.id_range,
        "output": str(output),
    }
    output.with_suffix(".metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )

    model.max_new_tokens = 512
    codegen(
        target_path=str(output),
        model=model,
        dataset="humaneval",
        greedy=True,
        n_samples=1,
        id_range=tuple(args.id_range) if args.id_range else None,
        version="v0.1.10",
        resume=True,
    )


if __name__ == "__main__":
    main()
