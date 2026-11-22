# Tool catalog

This inventory comes from six developer machines across Bluefin, Ubuntu, Omarchy, and macOS. It records observed tools and sets a starting point for a new machine. The inventory establishes presence. Verify regularly used tools and their versions with the person or project that needs them.

## Choose the install source

| Platform | Practical starting point |
| --- | --- |
| Bluefin | Use the system image for system tools, Homebrew for user-space commands, and Flatpak for desktop apps. Keep base-image changes separate from user-space package installs. Check the image and any existing package layering before changing the host. |
| Ubuntu | Use APT for Git, OpenSSH, build prerequisites, and supported system packages. Use vendor or user-space installs where a project needs newer language tools or a specific Docker or Kubernetes version. Inspect existing packages and repositories before adding an alternate source. |
| Omarchy | Use Pacman for system packages. Check Mise and any repo-pinned versions for language runtimes. Preserve Omarchy-managed desktop configuration and verify custom provider launchers independently. |
| macOS | Install Apple Command Line Tools for Git and build prerequisites as needed, then use the existing Homebrew prefix for user tools. On Apple silicon it is normally `/opt/homebrew`. Use Homebrew casks or vendor apps for desktop software and confirm whether a terminal app, desktop app, or both are needed. |

For repeatable Homebrew installs, derive a small Brewfile from the selected tools. Check it with `brew bundle check --file <file>` and install with `brew bundle install --no-upgrade --file <file>`. Review any generated Brewfile before committing it. A full machine dump can include unrelated taps, apps, and services. [Homebrew Bundle](https://docs.brew.sh/Brew-Bundle-and-Brewfile)

## Select by workload

| Role | Observed tools and choices |
| --- | --- |
| Base terminal | Git, GitHub CLI (`gh`), Bash, Zsh, Fish, tmux, direnv, jq, ripgrep, curl, and OpenSSH. Optional GitLab CLI (`glab`), ghui, lazygit, Neovim, fd, fzf, bat, eza, yq, wget, and ShellCheck. Bring over the relevant shell and tmux configuration through its own repository or an inspected diff. |
| Languages and builds | Python 3, uv and uvx, pipx, Node.js and npm, pnpm, Yarn, Deno, Go, Rust and Cargo, Java, Make, CMake, and Just. Prefer the repository's lockfiles and version selectors to the source host's system defaults. [uv installation](https://docs.astral.sh/uv/getting-started/installation/) |
| Containers and operations | Docker Engine or Docker Desktop, Docker Compose, Podman, Buildah, Skopeo, Podman Desktop, lazydocker, kubectl, Helm, AWS CLI, Google Cloud CLI, Railway CLI, cloudflared, and Stripe CLI. Pick the container runtime the workload expects and confirm the active Docker or Kubernetes context before acting. [Docker install](https://docs.docker.com/get-started/get-docker/), [Kubernetes tools](https://kubernetes.io/docs/tasks/tools/), [Railway CLI](https://docs.railway.com/guides/cli) |
| Data and credentials | SQLite, DB Browser for SQLite, PostgreSQL client (`psql`), age, SOPS, and the 1Password CLI (`op`). Use the client version required by the project and use the approved credential store. Set up Git identities, signing, and per-environment access separately. |
| Agent clients and providers | T3 Code, Codex, Claude Code, Cursor Agent, GitHub Copilot, Gemini CLI, Antigravity, OpenCode, Kimi, Grok, Pi, Hermes, and Assury. Only install the providers selected for the target. Use the vendor package or the existing approved distribution for custom tools. Confirm the resolved command, version, provider identity, and service-account path. [T3 Code](https://github.com/pingdotgg/t3code), [Codex CLI](https://github.com/openai/codex), [Claude Code setup](https://code.claude.com/docs/en/setup) |
| Browser and desktop work | agent-browser, Playwright CLI, Chrome, Brave, Ghostty, Visual Studio Code, Cursor, Zed, Obsidian, draw.io, Remmina, Mission Center, Slack, Discord, Signal, Zoom, and 1Password where applicable. Install browser dependencies for headless browser workloads only when needed. Keep host GUI apps off a headless-only machine unless its role requires them. |
| Networking | Tailscale with the intended account and policy, plus an approved Secure Shell route if the machine is managed remotely. Check ordinary OpenSSH and Tailscale SSH independently. [Tailscale installation](https://tailscale.com/docs/install) |

The audit also probes adjacent tools such as Bun, Terraform, OpenTofu, and k9s to make gaps visible. An absent tool is required only if the chosen role needs it.

## Restore preferences and access

- Locate the shared skill folders and any agent-specific folders. Existing machines use some combination of `~/.agents/skills`, `~/.codex/skills`, `~/.claude/skills`, and `~/.config/opencode/skills`. Inspect links and check the agent's discovery rules. Install the selected complete skill directories and verify discovery. A raw recursive copy can pull in plugin caches and stale duplicates.
- Recreate approved tool connectors and hooks from their source configuration. Review commands and environment-variable names before bringing them over. Authenticate through the agent or application. Keep private endpoints and stored logins on the intended machine.
- For a Git identity, confirm the expected account with `gh auth status` and the required repository with `git ls-remote <repository>`. Keep remote access tests read-only. Avoid logging remote URLs that contain credentials.
- For provider binaries, check the account that runs them. Examples are `codex --version` and `codex login status`. A separate desktop sign-in does not establish headless provider availability.
- On a privileged container or cluster host, verify runtime access against the expected local context. Read-only version or status commands are enough to validate setup, with a build or execution smoke test when the user asks for one.
