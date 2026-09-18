#!/usr/bin/env python3
"""Run the preregistered 20-sample stochastic sensitivity condition.

The condition is defined in EXPERIMENT_PLAN.md: 20 samples per task at
temperature 0.2 with top-p 0.95, BF16 weights, the forced base prompt, and the
pinned EvalPlus 0.3.1 generation path. Sampling is seeded once per run.

``--no-trailing-newline`` additionally applies the post-hoc prompt change
documented in ``scripts/prompt_newline_ablation.py``; it is not part of the
preregistered condition and is recorded in the run metadata.

``--batch-size`` controls how many of the 20 samples are generated per call. It
is a memory setting, not a scientific parameter: the sample count, temperature,
top-p, prompt, stops, and token cap are unchanged. DeepSeek-Coder-1.3B uses
multi-head attention, so its key/value cache for 20 concurrent sequences fills a
12 GB card; the driver then spills GPU memory into host RAM and a single task
takes over 15 minutes instead of seconds. That checkpoint therefore runs at
batch size 2, and the value used is recorded in the run metadata.
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
from prompt_newline_ablation import install_prompt_suffix_removal

REPOSITORY = Path(__file__).resolve().parents[1]
TARGETS = REPOSITORY / "protocol" / "published_targets.json"
OUTPUT_ROOT = REPOSITORY / "results" / "controls" / "sampling-sensitivity"
N_SAMPLES = 20
TEMPERATURE = 0.2
TOP_P = 0.95
MAX_NEW_TOKENS = 512


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="Primary target key.")
    parser.add_argument("--seed", type=int, default=11)
    parser.add_argument("--batch-size", type=int, default=20)
    parser.add_argument(
        "--no-trailing-newline",
        action="store_true",
        help="Also apply the post-hoc prompt change (records it in metadata).",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--id-range",
        nargs=2,
        type=int,
        metavar=("START", "END"),
        help="Optional half-open HumanEval task range used for a probe run.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    version = importlib.metadata.version("evalplus")
    if version != "0.3.1":
        raise RuntimeError(f"Expected EvalPlus 0.3.1, found {version}")

    import torch
    from evalplus.provider.hf import HuggingFaceDecoder

    install_non_accumulating_codegen(HuggingFaceDecoder)
    if args.no_trailing_newline:
        install_prompt_suffix_removal(HuggingFaceDecoder)

    targets = json.loads(TARGETS.read_text(encoding="utf-8"))["models"]
    target = next((item for item in targets if item["key"] == args.model), None)
    if target is None:
        raise ValueError(f"unknown model key: {args.model}")
    snapshot = snapshot_download(repo_id=target["model_id"], revision=target["revision"])

    suffix = "-no-trailing-newline" if args.no_trailing_newline else ""
    default = OUTPUT_ROOT / f"{args.model}{suffix}-seed{args.seed}.jsonl"
    output = (args.output or default).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    model = make_model(
        model=snapshot,
        backend="hf",
        batch_size=args.batch_size,
        temperature=TEMPERATURE,
        force_base_prompt=True,
        dataset="humaneval",
        attn_implementation="eager",
        dtype="bfloat16",
    )
    model.eos = list(dict.fromkeys(model.eos))
    model.max_new_tokens = MAX_NEW_TOKENS

    # The protocol forbids CPU or disk offload. Accelerate falls back to host
    # memory when the GPU is occupied, which makes generation orders of
    # magnitude slower and can exhaust system RAM, so fail fast instead.
    device_map = getattr(model.model, "hf_device_map", None) or {}
    offloaded = sorted(
        module for module, device in device_map.items() if str(device) in {"cpu", "disk"}
    )
    if offloaded:
        raise RuntimeError(
            f"{len(offloaded)} module(s) were offloaded off the GPU "
            f"(first: {offloaded[0]}); free GPU memory before running this condition"
        )

    metadata = {
        "experiment": "sampling_sensitivity",
        "preregistered": not args.no_trailing_newline,
        "evalplus_version": version,
        "dataset": "humaneval",
        "dataset_version": "v0.1.10",
        "model_key": args.model,
        "model_id": target["model_id"],
        "model_revision": target["revision"],
        "greedy": False,
        "n_samples": N_SAMPLES,
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
        "seed": args.seed,
        "batch_size": args.batch_size,
        "max_new_tokens": MAX_NEW_TOKENS,
        "dtype": "bfloat16",
        "force_base_prompt": True,
        "generation_path": "stock_stop_criteria_with_hook_restoration",
        "model_prompt": (
            'task["prompt"].strip()'
            if args.no_trailing_newline
            else 'task["prompt"].strip() + "\\n"'
        ),
        "stop_texts": list(model.eos),
        "id_range": args.id_range,
        "output": str(output),
        "seed_note": (
            "The seed is applied once before generation. A resumed run continues "
            "from a different point in the sampler stream than an uninterrupted "
            "run, so completed runs are reported only when uninterrupted."
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
