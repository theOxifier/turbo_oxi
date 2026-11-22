---
name: machine-setup
description: Audit or reproduce a personal developer machine, agent worker, or desktop on Bluefin, Ubuntu, Omarchy, or macOS. Use for new or replacement machines, host parity, tool inventories, or adding a T3 Code host to an existing project pool.
---

# Machine Setup

Establish the target operating system, architecture, account, and job. A desktop, a headless agent worker, and a machine that builds containers need different subsets of the same toolbox. Use the nearest working machine as evidence when available.

## Audit

Run [the inventory script](scripts/audit.sh) as the account that will use the tools. It measures command availability on the current path and likely user-bin paths, optional application presence, and Linux T3 Code service state. It prints no paths, hostnames, accounts, configuration contents, or credentials. It makes no changes.

```sh
sh scripts/audit.sh
ssh <host> 'sh -s' < scripts/audit.sh
```

Use the host's existing verified remote route. Compare the login shell and service environment if a provider is installed but the background server cannot see it. A shim found by the audit still needs a version and authentication check. Report unreachable hosts and untested functionality explicitly.

## Set up

1. Select the core, desktop, and workload tools from [Tool catalog](references/tool-catalog.md). Use the project's version files and the working reference host to choose runtime versions. Install missing tools through the platform or upstream package source.
2. Establish independent Git and provider access for the target account. Bring over non-secret preferences, selected skill directories, and project-specific instructions as needed. Reauthenticate via the vendor or approved secret store. Keep credentials, agent session data, private endpoints, and raw machine configuration out of shared artifacts.
3. For remote agent work, follow [T3 Code and Tailscale](references/t3-code.md). Keep existing application ports and routes intact. Inspect active turns before replacing or restarting an existing backend.
4. Repeat the inventory on the target. Verify version commands, Git authentication with a read-only remote query, selected provider login status, and the project-specific runtime or build prerequisites. For a headless worker, verify it from the intended initiating machine with the desktop closed.

Use repository-level files to supply local dependencies and scripts. Preserve existing checkouts, untracked files, and unrelated settings when bringing an established machine into the pool. Report what was installed, what works from the target account, and any sign-in or verification still pending.
