# Manuscript v1.9 / archive v1.9.0

This repository can produce a deterministic, history-free public archive for
the current manuscript and its matching checked-in evidence:

```powershell
python scripts/build_publication_release.py
```

The command refuses a dirty worktree by default and writes
`dist/local-code-benchmark-publication-v1.9.0.zip`. The archive contains all
Git-tracked files, a machine-readable release manifest, and SHA-256 hashes for
every packaged repository file. It intentionally excludes Git history,
ignored caches, build directories, credentials, and other untracked files.

The final ZIP is archived under the reserved version DOI
`10.5281/zenodo.22926448`; the concept DOI remains
`10.5281/zenodo.22800650`. DOI `10.5281/zenodo.22848609` identifies the earlier
v1.3.0 archive and does not contain manuscript v1.9.

Release procedure:

1. rebuild and validate the archive from the exact clean release commit;
2. publish that ZIP as Zenodo/GitHub release v1.9.0;
3. verify the version DOI in `CITATION.cff` and the manuscript while retaining
   the concept DOI;
4. tag the exact archived commit and verify the deposited checksum; and
5. rebuild the final PDFs if the independent review causes any text change.

The double-anonymous FORGE supplement is a different package. It must be
uploaded through the submission system and must not be replaced by this public,
identified archive during review.
