# Changelog

## 2_3 — 2026-09-19

Both master prompts advance one logical minor version from 2_2. Historical documents are preserved unchanged.

The universal prompt adds role-based discovery from an owner-authorized registry, explicit-owner-selection precedence, complete-read and digest evidence, compatibility checks, immutable per-run instruction records, and explicit migration/revocation handling. Its eight-step implementation, durable ledger, exact-checkpoint publication, interrupted-run continuation and recall-freshness requirements remain intact.

The infrastructure prompt no longer pins its universal dependency to a release filename. It resolves the `universal` role and required contract, records the actual selected revision, and uses that instruction set on continuation. Its staged infrastructure, single-host, network and lifecycle requirements are preserved.

Both prompts distinguish owner-wide, project and session memory; require provenance, access boundaries and truthful per-agent integration evidence; and prevent historical memory from authorizing actions or replacing approved instructions. Memory-schema evolution is independent of prompt or agent versions.

`PROMPT_REGISTRY.json` is the one default pointer for current approved role selections. `AGENTS.md` provides a stable, version-independent entrypoint. Explicit owner pins still take precedence. Future releases update the registry rather than rewriting all dependent prompts.

A dependency-free validator and negative tests check registry/document integrity and structural consistency. These are documentation checks, not implementation of the development harness or proof of a deployed shared-memory service. No infrastructure, agent, scheduler or user-machine installation is part of this release.
