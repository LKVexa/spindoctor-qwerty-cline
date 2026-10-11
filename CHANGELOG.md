# Changelog

## 1.1.0 - 2026-10-10

- Engine 1.1.0 at parity with the updated SpinDoctor 3.1.2: 1-298 logical qubits (59 per entangled factor), the `mcx7` gate,
  wide-register Born-Z sampling, `q.folder` with 3.1.2 semantics (.qasm2/.circuit, skipped-file listing, compact status, 128 files /
  4 MiB / 128 commands / 4096 characters), CSV report copies and measurement-CSV fitting equations. All 241 presets replayed.
- New tools `spindoctor_functions` (in-chat function table) and `spindoctor_test_theory` (theory testing from a file, pasted text or
  the chat history, with TXT+JSON+PDF theory reports).
- The repo root is now the Cline plugin, so `cline plugin install <git URL>` works. The engine is bundled.
- New prompt rule (only while the tools are available) and three slash commands (`/spindoctor-functions`, `/spindoctor-preset`,
  `/spindoctor-theory`). Capabilities `tools`, `rules`, `commands`; still no hooks.
- Tools run with the Cline workspace root as their working directory, so relative file paths resolve as the user expects.
- Python lookup falls back to `python` / `py` on Windows and `python` elsewhere, with a clear error when none is found. Timeout,
  64 MiB output cap and a strict tool allow-list.
- Tool input schemas reject unknown fields (`additionalProperties: false`).
- New `examples/cline_mcp_settings.json` for Cline in VS Code / JetBrains (MCP route).
- Tests: real Cline CLI install/config/uninstall, Cline's own loader and contribution registry, the full end-to-end suite.
- License changed from MIT to GPL-3.0-or-later. Author RUSSELL PHILIP SMITHSON. README, NOTICE, COPYRIGHT and SPDX headers added.

## 1.0.0

- First release: `spindoctor-qwerty/` folder with a `package.json` `cline.plugins` entry and `index.js` registering six tools.
