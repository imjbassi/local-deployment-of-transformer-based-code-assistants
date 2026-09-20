# Independent review packet

This packet is for a reviewer who did not generate the results or edit the
manuscript. It converts the remaining publication gate into a reproducible,
signed review rather than a self-attestation.

## Reviewer instructions

1. Record the exact commit reviewed and declare any conflicts or prior
   involvement.
2. Verify `artifacts/**/SHA256SUMS` before opening generated samples.
3. Treat generated Python as untrusted text. Do not execute it on a host;
   reproduce evaluation only through the documented network-isolated container.
4. Run the test suite and paper build from a clean checkout.
5. Trace every quantitative manuscript claim through `paper/REVIEW.md` to its
   source JSON/JSONL file. Independently recompute at least the primary scores,
   Kendall tau-b, the StarCoder2 prompt-newline scores, and the fourth factorial
   cell's 50/164 HumanEval and 43/164 HumanEval+ counts.
6. Inspect every rendered PDF page for clipping, overlap, broken links,
   unresolved references, and illegible tables.

## Required sign-off

- Reviewer name or stable pseudonym:
- Review date:
- Commit SHA:
- Independence/conflict statement:
- Commands and environment used:
- Checksum verification: pass / fail
- Quantitative spot checks: pass / fail (attach calculations)
- Claim-to-evidence audit: pass / fail (list exceptions)
- PDF rendering audit: pass / fail (list exceptions)
- Recommendation: ready / minor revision / major revision / reject
- Signed review URL or attached file:

The publication gate is complete only when this form is returned by an
independent person and all blocking findings are resolved. Repository maintainers
must not fill in the reviewer fields on that person's behalf.

