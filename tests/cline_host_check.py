# SpinDoctor Qwerty 1.1.0 - Cline host check
# Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version. It is distributed WITHOUT ANY WARRANTY; see the LICENSE file for details.
"""Cline host check. Standard library only (Python 3.8+); no Cline account, no sign-in, no API key, no model calls.

1. Static: package.json (cline.plugins entry, capabilities tools/rules/commands, @cline/sdk only as an optional peer, no runtime
   dependencies, GPL-3.0-or-later, author), the rule file, the VS Code MCP example, no hooks, tool schemas == engine schemas.
2. Plain Node (18+): the plugin's setup() with a minimal api registers 6 tools, 1 rule, 3 commands; a missing Python gives a
   clear error.
3. REAL Cline CLI (CLINE_BIN=<path to the cline binary>, or `cline` on PATH), in a throw-away HOME: `cline plugin install
   <repo> --json` (global and --cwd project), `cline config --json` shows the plugin loaded without a load error and lists its
   six tools, `cline plugin uninstall`.
4. Cline's own loader (CLINE_CORE=<@cline/core dist/index.js>, CLINE_NODE=<node 22+>): tests/cline_host_bridge.mjs loads the
   INSTALLED copy with loadAgentPluginsFromPathsWithDiagnostics + createContributionRegistry, checks the registered rule and
   commands, and tests/e2e_mcp.py drives the registered tools' execute(). Calling a model is not needed.
5. VS Code extension route: tests/e2e_mcp.py against engine/scripts/spindoctor_mcp.py (the server examples/cline_mcp_settings.json starts).

usage: python3 tests/cline_host_check.py [REPO_DIR]"""
import glob, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = ["spindoctor_run_script", "spindoctor_run_preset", "spindoctor_list_presets", "spindoctor_report", "spindoctor_functions", "spindoctor_test_theory"]
COMMANDS = ["spindoctor-functions", "spindoctor-preset", "spindoctor-theory"]

UNIT = r"""
const mod = await import(process.argv[1]);
const reg = { tools: [], rules: [], commands: [] };
mod.default.setup({ registerTool: (t) => reg.tools.push(t), registerRule: (r) => reg.rules.push(r), registerCommand: (c) => reg.commands.push(c) }, { workspaceInfo: { rootPath: process.cwd() } });
const rule = await reg.rules[0].content();
const fn = await reg.commands.find((c) => c.name === "spindoctor-functions").handler("presets ghz");
process.env.SPINDOCTOR_PYTHON = "no-such-python-sdq";
const mod2 = await import(process.argv[1] + "?nopython");
const missing = await mod2.callEngine("spindoctor_functions", {});
const bad = await mod.callEngine("not_a_tool", {});
console.log(JSON.stringify({ tools: reg.tools.map((t) => t.name), fields: reg.tools.every((t) => t.description && t.inputSchema && t.inputSchema.type === "object" && typeof t.execute === "function"),
  rules: reg.rules.map((r) => r.id), ruleHonest: /not a\s+quantum computer/.test(rule), commands: reg.commands.map((c) => c.name), presetsTable: fn.reply.includes("qc-") && fn.reply.includes("|"),
  missing: missing.ok === false && /not found|required/i.test(missing.error), bad: bad.ok === false, caps: mod.default.manifest.capabilities, hooks: mod.default.hooks || null, version: mod.VERSION }));
"""


def main():
    repo = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(HERE)
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    ok = True; mode = "host-simulated"

    def T(name, cond, detail=""):
        nonlocal ok
        ok = ok and bool(cond); print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  -- " + str(detail)[:900])); sys.stdout.flush()

    pj = json.load(open(os.path.join(repo, "package.json"), encoding="utf-8"))
    pl = pj["cline"]["plugins"]
    T("package.json: cline.plugins -> ./index.js (tools, rules, commands), version 1.1.0, GPL-3.0-or-later, author, ESM",
      pl == [{"paths": ["./index.js"], "capabilities": ["tools", "rules", "commands"]}] and pj["version"] == "1.1.0" and pj["license"] == "GPL-3.0-or-later"
      and pj["author"]["name"] == "RUSSELL PHILIP SMITHSON" and pj["type"] == "module" and os.path.isfile(os.path.join(repo, "index.js")), pj)
    T("package.json: no runtime dependencies; @cline/sdk only as an optional peer (the host provides it)",
      "dependencies" not in pj and pj["peerDependencies"] == {"@cline/sdk": "*"} and pj["peerDependenciesMeta"]["@cline/sdk"]["optional"] is True, pj)
    T("package.json files[] exist", all(os.path.exists(os.path.join(repo, f.rstrip("/"))) for f in pj["files"]), pj["files"])
    rule = open(os.path.join(repo, "rules", "spindoctor-qwerty.md"), encoding="utf-8").read()
    T("rules/spindoctor-qwerty.md: honest limits (classical, 298/59 qubits), function table and chat-theory confirmation",
      "not a\nquantum computer" in rule or "not a quantum computer" in rule and "298" in rule and "59" in rule and "confirm" in rule and "spindoctor_functions" in rule)
    ex = json.load(open(os.path.join(repo, "examples", "cline_mcp_settings.json"), encoding="utf-8"))["mcpServers"]["spindoctor-qwerty"]
    T("examples/cline_mcp_settings.json: stdio server engine/scripts/spindoctor_mcp.py, only read-only tools auto-approved",
      ex["args"][0].endswith("/engine/scripts/spindoctor_mcp.py") and os.path.isfile(os.path.join(repo, "engine", "scripts", "spindoctor_mcp.py"))
      and set(ex["autoApprove"]) <= {"spindoctor_functions", "spindoctor_list_presets", "spindoctor_report"}, ex)
    T("no hooks directory or hook files", not glob.glob(os.path.join(repo, "hooks*")) and "hooks:" not in open(os.path.join(repo, "index.js"), encoding="utf-8").read())
    sys.path.insert(0, os.path.join(repo, "engine")); sys.dont_write_bytecode = True
    from spindoctor import api  # noqa: E402
    node = shutil.which("node")
    r = subprocess.run([node, "--input-type=module", "-e", "const m = await import(process.argv[1]); console.log(JSON.stringify(m.TOOL_DEFS))", "file://" + os.path.join(repo, "index.js")],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=repo)
    defs = json.loads(r.stdout) if r.returncode == 0 else []
    T("index.js TOOL_DEFS == engine tool names and input schemas (plus additionalProperties: false)", [d["name"] for d in defs] == [t["name"] for t in api.TOOLS] == TOOLS
      and all({k: v for k, v in d["parameters"].items() if k != "additionalProperties"} == t["parameters"] and d["parameters"].get("additionalProperties") is False for d, t in zip(defs, api.TOOLS)), r.stderr[-400:])

    r = subprocess.run([node, "--input-type=module", "-e", UNIT, "file://" + os.path.join(repo, "index.js")], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=repo, timeout=300)
    try: u = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception: u = {}
    T("plain Node %s: setup() registers 6 tools, rule spindoctor-qwerty, 3 commands; /spindoctor-functions presets table; missing Python -> clear error" % subprocess.run([node, "--version"], stdout=subprocess.PIPE, text=True).stdout.strip(),
      u.get("tools") == TOOLS and u.get("fields") and u.get("rules") == ["spindoctor-qwerty"] and u.get("ruleHonest") and u.get("commands") == COMMANDS
      and u.get("presetsTable") and u.get("missing") and u.get("bad") and u.get("caps") == ["tools", "rules", "commands"] and u.get("hooks") is None and u.get("version") == "1.1.0", r.stdout[-500:] + r.stderr[-500:])

    installed = None
    cline = os.environ.get("CLINE_BIN") or shutil.which("cline")
    if cline:
        mode = "real Cline CLI"
        home = tempfile.mkdtemp(prefix="sdq_cline_home_"); proj = os.path.join(home, "proj"); os.makedirs(proj)
        env = dict(os.environ, HOME=home)
        run = lambda *a, cwd=home: subprocess.run([cline] + list(a), env=env, cwd=cwd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=300)
        ver = run("--version").stdout.strip().splitlines()[-1]
        r = run("plugin", "install", repo, "--json")
        try: res = json.loads(r.stdout.strip().splitlines()[-1])
        except Exception: res = {}
        installed = (res.get("entryPaths") or [None])[0]
        T("Cline CLI %s: cline plugin install <repo> --json (global) -> entry index.js, no sync failures" % ver,
          r.returncode == 0 and installed and installed.endswith(os.path.join("package", "index.js")) and os.path.isfile(installed) and not res.get("mcpSyncFailures"), r.stdout[-800:] + r.stderr[-400:])
        r = run("config", "--json")
        try: cfg = json.loads(r.stdout)
        except Exception: cfg = {}
        p = [x for x in cfg.get("plugins", []) if x.get("name") == "spindoctor-qwerty-cline"]
        tl = [t["name"] for t in cfg.get("tools", []) if t["name"].startswith("spindoctor_")]
        T("cline config --json: plugin enabled with no load error, its 6 tools listed", p and p[0].get("enabled") and "loadError" not in p[0] and sorted(tl) == sorted(TOOLS), (p, tl, r.stderr[-400:]))
        r = run("plugin", "install", repo, "--cwd", proj, "--json")
        try: res2 = json.loads(r.stdout.strip().splitlines()[-1])
        except Exception: res2 = {}
        e2 = (res2.get("entryPaths") or [""])[0]
        T("cline plugin install <repo> --cwd <project> -> <project>/.cline/plugins", r.returncode == 0 and e2.startswith(os.path.join(proj, ".cline", "plugins")) and os.path.isfile(e2), r.stdout[-600:])
        r = run("plugin", "uninstall", os.path.dirname(os.path.dirname(e2)) if e2 else "x", "--cwd", proj)
        T("cline plugin uninstall <install path> --cwd <project> (project copy)", r.returncode == 0 and not os.path.exists(e2), r.stdout[-400:] + r.stderr[-400:])
        g = os.path.join(home, "global-copy"); shutil.copytree(os.path.dirname(os.path.dirname(installed)), g)  # keep a copy for the loader checks
        r = run("plugin", "uninstall", "spindoctor-qwerty-cline")
        T("cline plugin uninstall spindoctor-qwerty-cline (global copy, by name)", r.returncode == 0 and not os.path.exists(installed), r.stdout[-400:] + r.stderr[-400:])
        installed = os.path.join(g, "package", "index.js")
    else:
        print("SKIP real Cline CLI not found (set CLINE_BIN)")

    core, node22 = os.environ.get("CLINE_CORE"), os.environ.get("CLINE_NODE")
    target = installed or os.path.join(repo, "index.js")
    ws = tempfile.mkdtemp(prefix="sdq_cline_ws_")
    if core and node22:
        bridge = [node22, os.path.join(HERE, "cline_host_bridge.mjs"), "--core", core, "--plugin", target, "--cwd", ws]
        r = subprocess.run(bridge + ["--describe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=300)
        try: d = json.loads(r.stdout.strip().splitlines()[-1])
        except Exception: d = {}
        cm = d.get("commands", {})
        T("@cline/core loader + contribution registry (%s copy): 6 tools, rule (whenToolAvailable spindoctor_run_script), 3 commands, no hooks"
          % ("installed" if installed else "repo"), d.get("tools") == TOOLS and d.get("rules", [{}])[0].get("whenToolAvailable") == "spindoctor_run_script" and d["rules"][0].get("honest")
          and sorted(cm) == sorted(COMMANDS) and cm["spindoctor-functions"]["replyLength"] > 500 and "qc-001" in cm["spindoctor-preset"]["submitPrompt"]
          and "confirm" in cm["spindoctor-theory"]["submitPrompt"] and d.get("hooks") == [] and not d.get("warnings"), r.stdout[-800:] + r.stderr[-800:])
        r = subprocess.run([sys.executable, os.path.join(HERE, "e2e_mcp.py"), "--server"] + bridge + ["--examples", os.path.join(os.path.dirname(target), "engine", "examples", "theory"),
                            "--out", os.path.join(ws, "e2e_bridge.json")], env=dict(os.environ, SPINDOCTOR_WORKSPACE=os.path.join(ws, "workspace")))
        T("end-to-end through the tools registered by Cline's loader (execute() of each tool)", r.returncode == 0)
    else:
        print("SKIP @cline/core bridge (set CLINE_CORE and CLINE_NODE)")

    srv = [sys.executable, os.path.join(repo, "engine", "scripts", "spindoctor_mcp.py")]
    r = subprocess.run([sys.executable, os.path.join(HERE, "e2e_mcp.py"), "--server"] + srv + ["--examples", os.path.join(repo, "engine", "examples", "theory"), "--out", os.path.join(ws, "e2e_mcp.json")],
                       env=dict(os.environ, SPINDOCTOR_WORKSPACE=os.path.join(ws, "workspace_mcp")))
    T("VS Code extension route: end-to-end through engine/scripts/spindoctor_mcp.py", r.returncode == 0)
    print("HOST-CHECK (%s)" % mode, "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
