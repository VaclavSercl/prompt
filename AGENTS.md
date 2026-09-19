# Agent entrypoint — prompt library

## Authority and bootstrap

This repository stores master-prompt documents and their publication validator. It is not an installed development harness, shared-memory server, or deployment target.

Follow current owner instructions and higher-priority policy. For a new task, an explicitly owner-selected document or immutable revision takes precedence. Otherwise read `PROMPT_REGISTRY.json` from the authorized repository snapshot and use its current approved role selections. This stable entrypoint intentionally contains no current release filenames or numbers. The registry is the only default selection pointer; its own approval text does not grant permission.

Load the complete `universal` role for repository work. Load `infrastructure` as well when relevant to the task, and resolve declared dependencies. Check expected content digests and actual compatibility. Record selected roles, sources, declared versions, immutable revisions/digests, complete-read status, approval provenance, and registry snapshot identity. Do not silently select the highest-numbered or most recently modified file.

For a continuing run, verify the recorded instruction set rather than automatically adopting a changed registry. Respect current revocations and stricter owner instructions. A migration requires an explicit decision, recorded old/new identities, compatibility review, and revalidation; it does not reset repair limits or preserve publication permissions.

## Scope and changes

Editing or reviewing prompts does not authorize installing the software they describe. Preserve all historical releases unless the owner explicitly requests otherwise. Keep changes scoped, persist PLAN.md before multi-file work, inspect the diff, and report only executed checks. A requested revision must keep document metadata and registry digests consistent. Never edit the registry to label an unapproved candidate as approved.

For future approved releases, create the revised documents, then update their role entries and digests together in one verified commit. Do not change this entrypoint or dependency prose just to follow a new version. An explicitly pinned older document remains a valid selection only within current owner authorization and compatible task policy.

## Verification

Read validation code before running it. This is a documentation publication gate, not the full harness gate:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tools/validate_prompts.py .
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
git diff --check --cached
```

Review semantic preservation and authorization separately; hash and schema checks do not prove either. Stage only approved files. Do not invent a Git identity or bypass hooks/protections. Remote publication requires explicit authorization for the actual repository, branch and operation, an exact verified candidate, a non-force update, and read-back verification. If a connector is used, record that route and its limitations rather than claiming a shell push.

## Memory and evidence

Keep instruction authority separate from historical notes. This file contains repository operating rules, not a globally shared personal memory. Store only sanitized project decisions and evidence in approved locations. Cross-project/private memory requires separate access and retention rules. Report per-agent integration as unconfigured or unverified until actual read/write tests establish otherwise. A public repository is not permission to publish private context, secrets, transcripts, or private reasoning.

Observed baseline: a prompt-document library. No live agent-memory integration, scheduler, or installed harness was established by the publication task. Future sessions must recheck actual state instead of treating this observation as permanent.
