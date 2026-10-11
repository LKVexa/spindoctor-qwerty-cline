# SpinDoctor Qwerty for Cline

**Cline plugin for the SpinDoctor 3.1.2 quantum-circuit simulator.** It adds six tools, a prompt rule and three slash commands to
the [Cline](https://cline.bot) CLI, SDK and Kanban: build and run `q.*` circuits (1-298 logical qubits), run the 241 built-in
presets, process folders of command files with `q.folder`, test theories from files, pasted text or the conversation itself, and
get TXT, PDF, JSON and CSV reports. Everything runs locally in a bundled, standard-library-only Python engine.

> **Honest limits:** SpinDoctor is a **classical** FP64 simulator running on your computer. It is not a quantum computer, does not
> connect to quantum hardware and gives no quantum speed-up or advantage. Registers hold 1-298 logical qubits, but one entangled
> group (factor) is limited to 59 qubits and dense factors to the memory budget (2^n x 16 bytes); registers wider than 29 qubits
> sample in basis Z only. Histograms come from seeded Born sampling. Requires **Python 3.8+** (no packages) and Node.js 18+ for the
> plugin (the Cline SDK itself needs Node.js 22+).

Version **1.1.0** (engine 1.1.0, "SpinDoctor 3.1.2 parity"). Author: RUSSELL PHILIP SMITHSON. License: GPL-3.0-or-later.

## Which Cline?

| You use | Install | What you get |
|---|---|---|
| **Cline CLI, SDK or Kanban** | `cline plugin install https://github.com/LKVexa/spindoctor-qwerty-cline.git` | 6 tools + the SpinDoctor rule + 3 slash commands (this plugin) |
| **Cline for VS Code / JetBrains** | Add the MCP server from [`examples/cline_mcp_settings.json`](examples/cline_mcp_settings.json) | The same 6 tools over MCP (Cline plugins don't apply to the IDE extensions yet) |

Other hosts: see the other `spindoctor-qwerty-*` repositories on [LKVexa](https://github.com/LKVexa?tab=repositories&q=spindoctor-qwerty).

## Install (Cline CLI / SDK / Kanban)

1. Install Python 3.8 or newer and check it runs as `python3` (macOS, Linux) or `python` / `py` (Windows).
2. Install the plugin globally, or for one project only:

   ```bash
   cline plugin install https://github.com/LKVexa/spindoctor-qwerty-cline.git            # global: ~/.cline/plugins
   cline plugin install https://github.com/LKVexa/spindoctor-qwerty-cline.git --cwd .    # this project: .cline/plugins
   # or from a downloaded copy:
   cline plugin install ./spindoctor-qwerty-cline
   ```

   The installer copies or clones the repo into the plugin store. There are no npm dependencies to download (`@cline/sdk` is an
   optional peer that Cline provides).
3. Check it loaded: `cline config` (plugin tab), or `cline config --json` lists `spindoctor-qwerty-cline` and the six
   `spindoctor_*` tools.
4. Ask Cline: *"show the SpinDoctor functions"* or type `/spindoctor-functions`.

To remove it: `cline plugin uninstall spindoctor-qwerty-cline`. If it is installed both globally and in a project, the name matches both, so pass the install path that `cline plugin install --json` printed (with `--cwd .` for the project copy).

**SDK apps:** pass the entry file in `pluginPaths` (for example `pluginPaths: ["<path to this repo>/index.js"]`) or import it and
add the default export (the `AgentPlugin`) to `extensions`.

**Settings (environment variables, all optional):** `SPINDOCTOR_WORKSPACE` (where state and reports go; default
`~/spindoctor-workspace`), `SPINDOCTOR_PYTHON` (Python command; default `python3` then `python`, or `python` then `py` on
Windows), `SPINDOCTOR_TIMEOUT_MS` (default 600000).

## Install (Cline for VS Code / JetBrains: MCP)

Open Cline's MCP servers panel -> Configure, and add the `spindoctor-qwerty` entry from
[`examples/cline_mcp_settings.json`](examples/cline_mcp_settings.json) to `cline_mcp_settings.json`. Replace the placeholders with
the absolute path of this repo and your workspace folder; on Windows use `"command": "python"` (or `"py"`). Only the read-only
tools are auto-approved in the example.

## What the plugin adds

- **Tools:** `spindoctor_run_script`, `spindoctor_run_preset`, `spindoctor_list_presets`, `spindoctor_report`,
  `spindoctor_functions`, `spindoctor_test_theory`. Each call starts the bundled engine (`engine/scripts/spindoctor_cli.py tool
  <name>`); results longer than 60000 characters are shortened for the model and the full output stays in the report files.
- **Rule** (`rules/spindoctor-qwerty.md`): honesty rules, the command grammar, how to show the function table and how to test a
  theory from the chat. It's only added to the system prompt while the SpinDoctor tools are available.
- **Slash commands:** `/spindoctor-functions [section] [filter]` (replies with the table, no model call), `/spindoctor-preset
  <id> [name=value ...]` and `/spindoctor-theory [file, text or "the theory we discussed"]` (both hand a prompt to the agent).
- **No hooks**, no network access, no telemetry. Nothing runs until a tool or command is used.

## SpinDoctor Qwerty - plugin tools

| Function | What it does | Command to type |
|---|---|---|
| Function table (spindoctor_functions) | Show this table in chat | Ask: "show the SpinDoctor functions" or type `/spindoctor-functions` |
| Run a script (spindoctor_run_script) | Run any q.* lines above; returns results + TXT/JSON/CSV/PDF report paths | Ask: "run q.circuit new bell 2 / q.circuit add h 0 / ..." |
| Run a preset (spindoctor_run_preset) | Run qc-001..qc-241 with overrides | Ask: "run preset qc-067 with shots=64" or type `/spindoctor-preset qc-067 shots=64` |
| List presets (spindoctor_list_presets) | Search the 241 presets | Ask: "list presets about Grover" |
| Read a report (spindoctor_report) | List/read TXT reports (PDF/JSON paths alongside) | Ask: "show the newest SpinDoctor report" |
| Test a theory from a file (spindoctor_test_theory source=file) | Read a .txt/.md/.pdf/.py/.json/.csv/.q attachment, then hypothesis -> prediction -> q.* script -> run -> verdict + TXT/PDF theory report | Ask: "test the theory in C:/notes/theory.md" (the host must pass the file path/content) |
| Test a theory from text (spindoctor_test_theory source=text) | Same pipeline for pasted text | Ask: "test this theory: a Hadamard on \|0> gives 50/50" |
| Test the theory we discussed (spindoctor_test_theory source=chat) | The AI summarises the theory from the conversation (claims, assumptions, variables, prediction), you confirm, then it is tested; quoted excerpts go in the report under 'Source: chat history'. An exported chat transcript (.txt/.md/.json/.html) also works | Ask: "test the theory we discussed" (or `/spindoctor-theory`) or "test the theory in my exported chat C:/chats/conversation.json" |

Every command family is listed with a runnable example in **[FUNCTIONS.md](FUNCTIONS.md)** (the exact table the tool shows):
circuits (`q.circuit`, including 298-qubit wide registers and the `mcx7` gate), queries (`q.query`), the tranche register
(`q.tranche`), the procedural grid, presets and sequences, resource planning, math calculators, physics models, lessons, noise, error
correction, compilation, algorithms, inputs/folders/history (`q.input`, `q.folder`, `q.history`) and the cartridge commands.

## Theory testing

`spindoctor_test_theory` turns a claim into a test: hypothesis -> measurable prediction -> `q.*` script -> run -> compare -> a TXT +
JSON + PDF **theory test report** with the hypothesis, script, raw results, verdict (*supported*, *not supported* or *inconclusive*)
and limits.

- **From a file:** .txt, .md, .pdf, .py, .json, .csv or .q. In Cline, @-mention the file or give its path; relative paths are resolved against the Cline workspace root.
- **From pasted text.**
- **From the chat history:** say *"test the theory we discussed"*. The model writes a short summary (claims, assumptions, variables,
  measurable prediction), shows it to you to confirm or correct, then passes it with optional quoted excerpts; the report records them
  under *Source: chat history*. Exported chat transcripts (.txt/.md/.json/.html from ChatGPT, Claude and others) also work.
- The plugin cannot read your conversation or attachments by itself: only the model sees them, and very long conversations may already
  be truncated by the context window.

Sample theory files and chat transcripts are in `engine/examples/theory/`. The two sample
PDFs are stored as text; run `python3 engine/examples/theory/make_sample_pdfs.py` to
recreate them.

## Folder ingestion (`q.folder`)

`q.folder run path="<folder>"` runs every supported file at the top level of a folder (.txt, .csv, .json, .qasm, .qasm2, .circuit,
.pdf) in ordinal name order: 1-128 supported files, at most 4 MiB per file, 1-128 commands per file and 4096 characters per command,
strict UTF-8. Other files (for example .md) are skipped and listed. The first failing file stops the job.

## Testing

| Test | Command | Result for 1.1.0 |
|---|---|---|
| Host check, real Cline CLI + Cline's own loader | `CLINE_BIN=<cline binary> CLINE_CORE=<@cline/core dist/index.js> CLINE_NODE=<node 22> python3 tests/cline_host_check.py` | 16/16 checks, end-to-end 12/12 twice |
| Same without Cline | `python3 tests/cline_host_check.py` | 9/9 checks, end-to-end 12/12 (MCP route) |

**Real host:** the Cline CLI 3.0.70 (`npm i cline`, no account, no sign-in, no API key, no model calls) installed the plugin
globally and per project, `cline config --json` showed it enabled with no load error and listed its six tools, and `cline plugin
uninstall` removed it. Cline's own plugin loader and contribution registry from `@cline/core` 0.0.92 then loaded the installed copy,
and `tests/e2e_mcp.py` drove every registered tool's `execute()`: the function table, one script per command family, a preset,
`q.folder` on a mixed folder, theory tests from a file and from a chat summary/transcript, TXT+PDF reports, and a comparison with
the SpinDoctor 3.1.2 reference outputs. The VS Code MCP route was tested with the same suite; the VS Code extension itself was not
tested. Details in [E2E_RESULTS.md](E2E_RESULTS.md).

## Repository layout

```
package.json          Cline plugin manifest (cline.plugins -> index.js)
index.js              AgentPlugin: tools, rule, slash commands
rules/                the SpinDoctor prompt rule
engine/               bundled Python engine (spindoctor/, scripts/spindoctor_cli.py, scripts/spindoctor_mcp.py, examples/)
examples/             cline_mcp_settings.json for the VS Code / JetBrains extension
tests/                host check, Cline loader bridge, end-to-end suite, reference outputs
FUNCTIONS.md          the full function table
```

## Author and license

Author: **RUSSELL PHILIP SMITHSON** <russellsmithson77@outlook.com>

Copyright (C) 2026 RUSSELL PHILIP SMITHSON. Licensed under the GNU General Public License v3.0 or later (`GPL-3.0-or-later`): see
[LICENSE](LICENSE), [NOTICE](NOTICE) and [COPYRIGHT](COPYRIGHT). `package.json` carries the license and author. Cline is a trademark
of Cline Bot Inc.; this project is not affiliated with Cline Bot Inc.
