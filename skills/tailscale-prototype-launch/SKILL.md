---
name: tailscale-prototype-launch
description: Publish a verified private Tailscale link when launching or sharing a prototype.
---

# Launch a prototype over Tailscale

1. Start the prototype on a loopback port and verify it responds. Keep the process running after the shell exits.
2. Check `tailscale serve status --json`. Reuse the prototype's existing private mapping or pick an unused Serve port and run `tailscale serve --bg --https=<serve-port> http://127.0.0.1:<app-port>`. Use Serve for private access.
3. Verify the printed address, including the port and prototype route, with `curl`. Confirm it returns the expected page, then share the clickable link. If verification fails, report the blocker.
