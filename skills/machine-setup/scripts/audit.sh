#!/bin/sh

# Report installed tools without executing their binaries or reading credentials.
set -eu

if [ "$#" -ne 0 ]; then
    printf 'Usage: sh audit.sh\n' >&2
    exit 2
fi

printf 'Platform: %s %s\n' "$(uname -s)" "$(uname -m)"
if [ -r /etc/os-release ]; then
    awk -F= '$1 == "PRETTY_NAME" {gsub(/^"|"$/, "", $2); print "OS: " $2}' /etc/os-release
elif command -v sw_vers >/dev/null 2>&1; then
    printf 'OS: macOS %s\n' "$(sw_vers -productVersion)"
fi

login_path=$PATH
candidate_path="$PATH:$HOME/.local/bin:$HOME/.t3/bin:$HOME/.cargo/bin:$HOME/.bun/bin:$HOME/.local/go/bin:/opt/homebrew/bin:/home/linuxbrew/.linuxbrew/bin"

report() {
    printf '\n%s\n' "$1"
    shift
    for tool do
        if PATH=$login_path command -v "$tool" >/dev/null 2>&1; then
            printf '  %-17s on PATH\n' "$tool"
        elif PATH=$candidate_path command -v "$tool" >/dev/null 2>&1; then
            printf '  %-17s found outside PATH\n' "$tool"
        else
            printf '  %-17s absent\n' "$tool"
        fi
    done
}

report 'Package and environment managers' brew apt dnf rpm-ostree bootc pacman flatpak nix mise direnv
report 'Shell and source control' bash zsh fish tmux zellij git gh glab ghui lazygit nvim
report 'Language and build tools' uv uvx python3 pipx node npm pnpm yarn bun deno go rustup rustc cargo java make cmake ninja just shellcheck
report 'Utilities' jq yq rg fd fzf bat eza curl wget sqlite3 psql redis-cli
report 'Containers and operations' docker podman buildah skopeo lazydocker kubectl helm k9s kind minikube kustomize terraform tofu aws gcloud az railway fly cloudflared stripe
report 'Access and secrets' tailscale ssh age sops op
report 'Coding agents' t3 codex claude cursor cursor-agent copilot gemini agy antigravity opencode kimi grok pi hermes openclaw assury enforce
report 'Browser tools' agent-browser playwright-cli

if [ "$(uname -s)" = Darwin ]; then
    printf '\nDesktop application bundles\n'
    for app in 'T3 Code (Nightly)' 'T3 Code' Tailscale Codex Claude Cursor +        'Visual Studio Code' Ghostty Docker 'Brave Browser' 'Google Chrome' +        Obsidian Slack Discord Signal 1Password; do
        if [ -d "/Applications/$app.app" ] || [ -d "$HOME/Applications/$app.app" ]; then
            printf '  %s\n' "$app"
        fi
    done
elif command -v flatpak >/dev/null 2>&1; then
    printf '\nSelected Flatpak applications\n'
    flatpak list --app --columns=application 2>/dev/null | awk '
        /^(com\.brave\.Browser|com\.google\.Chrome|com\.slack\.Slack|com\.discordapp\.Discord|org\.signal\.Signal|md\.obsidian\.Obsidian|org\.remmina\.Remmina|com\.jgraph\.drawio\.desktop|io\.missioncenter\.MissionCenter|io\.podman_desktop\.PodmanDesktop)$/ {
            print "  " $0
        }'
fi

if command -v systemctl >/dev/null 2>&1; then
    printf '\nT3 Code user service\n'
    systemctl --user is-active t3code.service 2>/dev/null || :
    systemctl --user is-enabled t3code.service 2>/dev/null || :
    if command -v loginctl >/dev/null 2>&1; then
        loginctl show-user "$(id -un)" -p Linger 2>/dev/null || :
    fi
fi

printf '\nSkill directories present\n'
for path in .agents/skills .codex/skills .claude/skills .config/opencode/skills; do
    if [ -d "$HOME/$path" ]; then
        printf '  %s\n' "$path"
    fi
done
