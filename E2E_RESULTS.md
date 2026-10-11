# End-to-end results: spindoctor-qwerty-cline 1.1.0

Run on 2026-10-10 (PT) in a clean-room copy (empty folder, empty HOME, PATH=/usr/bin:/bin, no access to engine development
folders), following only this README: `cline plugin install <repo>`, then `tests/cline_host_check.py`.

**Mode:** real host. The **Cline CLI 3.0.70** was installed from npm (`npm i cline`) on a Linux test machine and used with no
account, no sign-in, no API key and no model calls. npm 9 on that machine didn't create the `node_modules/.bin/cline` link, so
the platform binary from `@cline/cli-linux-x64` was called directly (that's the binary the `cline` launcher runs). It installed the
plugin globally and per project, `cline config --json` showed `spindoctor-qwerty-cline` enabled with no load error and listed its
six tools, and `cline plugin uninstall` removed both copies. Driving the tools through a Cline agent needs a model provider, so tool
calls were made through **Cline's own plugin loader and contribution registry** (`@cline/core` 0.0.92 on Node.js 22:
`loadAgentPluginsFromPathsWithDiagnostics` + `createContributionRegistry`) on the installed copy, calling each registered tool's
`execute()`.

**Format check:** the Cline docs (`docs/customization/plugins.mdx`, `docs/sdk/plugins.mdx`, `docs/sdk/guides/writing-plugins.mdx` in
github.com/cline/cline, read 2026-10-10) still describe `package.json` -> `cline.plugins[].paths` and an `AgentPlugin` default export
with `setup(api, ctx)`. Cline 3.0.70 also loads Agent Plugins 1.0.0 folders (`plugin.json`), but a folder with a `plugin.json` is
not loaded as an SDK plugin, so this repo stays an SDK plugin only: it can register tools, a rule and slash commands, which the
Agent Plugins route can't.

**Parity target:** the updated SpinDoctor 3.1.2. Publishing was approved by Russell on the basis of the updated 3.1.2 passing its
own suite 18/18, with the three 29-qubit test checks adapted to the 298-qubit limit.

## Host check (clean room, real Cline CLI + @cline/core loader)

```
PASS package.json: cline.plugins -> ./index.js (tools, rules, commands), version 1.1.0, GPL-3.0-or-later, author, ESM
PASS package.json: no runtime dependencies; @cline/sdk only as an optional peer (the host provides it)
PASS package.json files[] exist
PASS rules/spindoctor-qwerty.md: honest limits (classical, 298/59 qubits), function table and chat-theory confirmation
PASS examples/cline_mcp_settings.json: stdio server engine/scripts/spindoctor_mcp.py, only read-only tools auto-approved
PASS no hooks directory or hook files
PASS index.js TOOL_DEFS == engine tool names and input schemas (plus additionalProperties: false)
PASS plain Node v20.19.2: setup() registers 6 tools, rule spindoctor-qwerty, 3 commands; /spindoctor-functions presets table; missing Python -> clear error
PASS Cline CLI 3.0.70: cline plugin install <repo> --json (global) -> entry index.js, no sync failures
PASS cline config --json: plugin enabled with no load error, its 6 tools listed
PASS cline plugin install <repo> --cwd <project> -> <project>/.cline/plugins
PASS cline plugin uninstall <install path> --cwd <project> (project copy)
PASS cline plugin uninstall spindoctor-qwerty-cline (global copy, by name)
PASS @cline/core loader + contribution registry (installed copy): 6 tools, rule (whenToolAvailable spindoctor_run_script), 3 commands, no hooks
PASS initialize (server spindoctor-qwerty (Cline plugin via @cline/core) 1.1.0)
PASS tools/list exposes the 6 tools
PASS function table (Markdown, 19 sections, 298-qubit limits listed)
PASS 241 presets listed
PASS one script per command family (16 families, every table example)
PASS 298-qubit circuit with mcx7 (prepared-factor-Born-Z)
PASS q.folder on mixed .txt/.csv/.json/.qasm folder (+ .md skipped)
PASS theory from a file -> supported, TXT+PDF report
PASS theory from a chat summary + quoted excerpts -> supported
PASS theory from an exported chat transcript -> supported
PASS presets qc-001..qc-025 match the updated 3.1.2 reference (20 identical, 5 documented differences)
PASS TXT+PDF reports valid (255 PDFs, 255 TXT twins)
SUMMARY 12/12 passed in 24.5s
PASS end-to-end through the tools registered by Cline's loader (execute() of each tool)
PASS initialize (server spindoctor-qwerty 1.1.0)
PASS tools/list exposes the 6 tools
PASS function table (Markdown, 19 sections, 298-qubit limits listed)
PASS 241 presets listed
PASS one script per command family (16 families, every table example)
PASS 298-qubit circuit with mcx7 (prepared-factor-Born-Z)
PASS q.folder on mixed .txt/.csv/.json/.qasm folder (+ .md skipped)
PASS theory from a file -> supported, TXT+PDF report
PASS theory from a chat summary + quoted excerpts -> supported
PASS theory from an exported chat transcript -> supported
PASS presets qc-001..qc-025 match the updated 3.1.2 reference (20 identical, 5 documented differences)
PASS TXT+PDF reports valid (255 PDFs, 255 TXT twins)
SUMMARY 12/12 passed in 13.2s
PASS VS Code extension route: end-to-end through engine/scripts/spindoctor_mcp.py
HOST-CHECK (real Cline CLI) PASS
```

The same check without Cline (`python3 tests/cline_host_check.py`): 9/9 checks, end-to-end 12/12 through the MCP route.

## Notes

- **Preset differences (5 of qc-001..qc-025):** CPU-only reference instead of OpenCL GPU fields, tranche checkpoint text, state
  file name. They're documented in `tests/e2e_mcp.py` and are the same in every spindoctor-qwerty repo.
- **Not tested:** Cline for VS Code / JetBrains itself (the MCP route it uses was tested with the same suite), Kanban, and any run
  that calls a model.
