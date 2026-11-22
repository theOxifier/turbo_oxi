# T3 Code and Tailscale

Install the desktop client for an interactive workstation. On a machine expected to run threads without its desktop, use the supported command-line install and background service. Check the installed release with `t3 --version`, `t3 status`, and command help. Desktop and background service releases are managed separately, and each host's service can run a different build. [T3 Code install](https://github.com/pingdotgg/t3code/blob/main/docs/user/install.md)

## Enable the worker

1. Choose the account that owns the project and provider sign-ins. Verify the intended T3 Code home and the provider commands in that account. Avoid a second backend pointing at an existing T3 Code home. The data lock and listening port belong to one backend.
2. For an existing desktop backend, record the working port, proxy routes, version, and linked-client access. Verify that active turns have finished, then close the desktop backend and install the service against the same data home. For a fresh headless install, there is no desktop backend to stop.
3. Run `t3 service install` and confirm `t3 service status`. On Linux, check `systemctl --user is-enabled t3code.service` and `systemctl --user is-active t3code.service`. If boot without a login is required, verify `loginctl show-user "$(id -un)" -p Linger` and enable user lingering if needed. Verify the actual listening port, commonly `3773`.
4. Choose one remote route approved for the worker. For tailnet-only access, keep T3 Code on loopback and use Tailscale Serve with the verified port and an available or existing dedicated HTTPS route. For account-based access, use the documented T3 Connect flow. Check routes before changing anything on a host that serves other apps. [T3 Code remote access](https://github.com/pingdotgg/t3code/blob/main/docs/user/remote-access.md)
5. Verify the loopback listener, remote endpoint, and an authenticated read with the desktop closed. If a desktop-managed Tailscale route vanished during cutover, restore just that route as a persistent Tailscale Serve proxy and verify the existing client still works.

Example for an unused HTTPS route, with the backend confirmed on port `3773`:

```sh
tailscale serve status
tailscale serve --bg --https=15443 http://127.0.0.1:3773
```

Use the host's actual endpoint and route in place of the example. Serve may need to provision a certificate before the first request succeeds. A pending certificate, a failed proxy, and an unavailable provider cause different symptoms. [Tailscale Serve](https://tailscale.com/docs/reference/tailscale-cli/serve)

## Pair clients, link machines, and add projects

- **Desktop or web pairing** gives the initiating client access to the worker. Add the actual worker under the app's Connections or Environments settings. Verify that the entry is connected, and that its projects and enabled providers are visible. Send any one-time pairing credential through the app or protected input.
- **Linked environments** let agents on one host act on another. Enable the target's Linked environments setting in **Settings → Labs**, then link from the initiating host. These links are directional. Verify using `t3 environment list` from each intended initiator. A practical headless equivalent on releases that support it is setting `"linkedEnvironmentsEnabled": true` in the target's T3 home under `userdata/settings.json`, preserving the other settings. Use the app's link flow or the installed `t3 environment link --help` to choose the appropriate access and pairing method. Prefer approval-required access unless broader permissions are requested.
- **Project load balancing** requires a connected desktop or web client, the same Git repository registered on the worker, and an enabled, authenticated provider matching the thread's provider. Register an existing checkout with `t3 project add --title <name> <checkout>` after verifying its origin and branch. Fetch the intended base and preserve local changes. Enable automatic load balancing in the initiating client's environment settings and use **Auto** on a new thread for the repository-grouped project. Confirm the worker is eligible in that client. Start a test thread only when requested, and inspect routing on that thread before claiming a successful dispatch. Manual-only weight excludes the machine from automatic selection.

## Verify and maintain

| Symptom | Test |
| --- | --- |
| Host absent or unreachable | Check from the affected client with `tailscale status` and `tailscale ping <host>`. Use the actual Tailscale name or address if the short name resolves to a local address. |
| Tailscale works, port 22 refuses | Verify an approved SSH server on the target. Tailscale SSH requires explicit enablement on a supported target and matching tailnet policy. On macOS confirm the Tailscale variant before assuming inbound Tailscale SSH is available. [Tailscale SSH](https://tailscale.com/docs/features/tailscale-ssh) |
| Client shows unavailable | Test the remote endpoint from the affected client machine. If it responds, check desktop pairing or the initiating machine's directional link and its expiration. |
| Remote endpoint fails | Check the service status, loopback listener, and Tailscale Serve route in sequence. Check certificate provisioning when a new Serve endpoint accepts the connection but stalls during HTTPS negotiation. |
| Worker absent from Auto | Check the client's connected environments, repository grouping and Git remote identity, provider availability, and the worker's weight. Running the service and linking it for agents are separate prerequisites from desktop pairing. |
| Desktop update did not update worker | Run `t3 update` on the worker when authorized, after active turns finish. Verify the running service version and the remote connection afterward. A Git push only updates the repository. |

If a desktop launcher won't pin on GNOME, check the running window's app identity against the installed desktop entries, including `NoDisplay`. T3 Code can regenerate its link-handler desktop entry on launch, so verification must cover an ordinary restart before calling a launcher fix persistent. If the session crashes, inspect the compositor and application logs before changing the launcher or extensions again.
