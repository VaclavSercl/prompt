# Plan — version-independent prompt authority and shared memory

## Goal
Publish the owner-requested next minor revision of both master prompts. Resolve approved prompts by role and authorized registry rather than fixed dependency filenames. Keep each run bound to the actual loaded revision. Define agent-independent, scoped memory without claiming a deployed shared-memory service.

## Non-goals
No infrastructure deployment, harness installation, agent invocation, paid calls, scheduler activation, secret handling, or changes to the owner's computers. Do not rewrite archived prompt releases.

## Detected environment
Target: `VaclavSercl/prompt`, branch `main`. Baseline: `6310dec256aa58219ad47f84132bbc3f52c8bc10`; tree: `4897622c2547991f5cd3dd0e80933f76620b4b86`.
The connected GitHub API supports authenticated Git-object creation and non-force ref updates. The hosted workspace has Git and Python; direct GitHub DNS resolution failed. It is not the owner's server. Use the connector for remote reads/writes; construct and verify local artifacts separately.
At baseline the repository contains four Markdown releases and no AGENTS.md, registry, CI, or installed harness.

## Impact analysis
Preserve all four baseline files by their original Git blob identifiers. Add two complete releases with one logical minor increment, a single registry, a stable agent entrypoint, release notes, and a dependency-free publication validator. Registry approval is task-scoped owner approval, not inferred from filenames, dates, or generated text. Prompt publication does not deploy the described system.

## File checklist
- Universal_Master_Prompt_v2_3.md: authority resolution, run pinning, scoped memory, evidence and acceptance requirements.
- Infrastructure_Master_Prompt_v2_3.md: role-based universal dependency, compatible shared-memory governance and readiness checks.
- PROMPT_REGISTRY.json: one current approved selection per role, exact content digests and role dependencies.
- AGENTS.md: version-independent bootstrap and documentation-repository operating rules.
- CHANGELOG.md: factual release changes and non-deployment boundary.
- tools/validate_prompts.py and tests/test_validate_prompts.py: local structural/integrity validation and negative tests.
- PLAN.md: this scoped plan and final evidence summary.

## Acceptance criteria
Both new documents retain all baseline sections outside explicitly scoped edits. Their self-declared versions and filenames agree and advance from 2_2 to 2_3. No operative dependency contains a fixed versioned master-prompt filename. The registry's selected paths, role dependencies, approval status and content digests validate. Explicit owner pins take precedence over a default registry selection; no highest-number/newest-date fallback is allowed. Run pins survive continuation without silently changing revision. Shared memory cannot grant authority or claim installed integrations. All four baseline blobs remain unchanged. Only the authorized branch is advanced non-forcibly after exact-candidate verification.

## Exact verification commands
Run in the generated local workspace:
`PYTHONDONTWRITEBYTECODE=1 python3 tools/validate_prompts.py .`
`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`
`git diff --check --cached`
Validate original Git blob hashes, release text preservation and the exact candidate tree independently. Read back the remote tree, commit parent and main ref via the connected GitHub API. Run Python syntax parsing without creating bytecode caches.

## Failure scenarios and recovery
Unreadable/incomplete source, hash mismatch, unknown authority, unsafe path, inconsistent version, or failed tests blocks publication. An advanced remote head blocks the prepared non-force publication rather than overwriting others. An uncertain API write must be reconciled by reading exact objects/ref before retrying. Preserve local artifacts and evidence on failure. No force pushes, reset, deletion, auto-stash, or production rollback.

## Approval requirements
The owner explicitly requested generalization, Git/GitHub publication, one version increment, and application of the master prompt to this task. This covers the named repository/branch and scoped documentation/validator changes only. Deployment, independent agents, external services, and access to the owner's local clone are not authorized by this publication.

## Verification evidence
Preliminary documentation validation passed, including integrity/structure checks and 20 fixture tests. The fixtures cover changed/missing content, unsafe paths and symlinks, duplicate keys/roles, unsupported schema, missing approval provenance, version and contract mismatch, cyclic dependencies, preserved eight-step scope, ignoring newer unapproved files, malformed dependency entries, and adoption of a different future version through only the documents and registry. A self-review checked the scoped semantic changes; no independent reviewer was invoked.

All four baseline document bytes were reconstructed from connector reads and verified against their exact Git blob identifiers. The exact baseline tree and commit were imported into a new owned shallow local Git mirror; this is not the owner's existing local clone. No historical release was altered. Direct network cloning remains unavailable in this workspace; remote Git objects and the final non-force ref update use the authenticated connector. The final candidate is revalidated after staging, and its exact Git tree and commit are compared with remote read-back evidence.

Limitations: no harness installation or full .gauntlet.sh exists in this document repository; no live agent, external memory, scheduler, host deployment, or cross-platform runtime test was performed. The validator does not establish owner authorization, semantic safety, or protection against a hostile concurrently mutating filesystem. Publication and final local-commit evidence are recorded outside the tracked candidate after verification so this plan does not pre-claim remote success.
