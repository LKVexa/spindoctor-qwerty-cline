#!/usr/bin/env node
// SpinDoctor Qwerty 1.1.0 - Cline host bridge
// Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>
// SPDX-License-Identifier: GPL-3.0-or-later
// This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
// Public License as published by the Free Software Foundation, either version 3 of the License, or (at your
// option) any later version. It is distributed WITHOUT ANY WARRANTY; see the LICENSE file for details.
// Cline host bridge: loads the plugin with Cline's OWN plugin loader and contribution registry (@cline/core:
// loadAgentPluginsFromPathsWithDiagnostics + createContributionRegistry, the code path the Cline CLI/SDK uses), then
// exposes the registered tools over a minimal stdio MCP (JSON-RPC 2.0) loop so tests/e2e_mcp.py can drive them.
// Tool calls go through each registered tool's execute(). Needs Node 22+ (as @cline/core does).
// usage: node tests/cline_host_bridge.mjs --core <@cline/core dist/index.js> --plugin <entry index.js> --cwd <workspace root> [--describe]
import path from "node:path";
import readline from "node:readline";
import { pathToFileURL } from "node:url";

const arg = (k) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : undefined; };
const corePath = arg("--core"), pluginPath = path.resolve(arg("--plugin")), cwd = path.resolve(arg("--cwd") || process.cwd());
const core = await import(pathToFileURL(corePath).href);
const { plugins, failures, warnings } = await core.loadAgentPluginsFromPathsWithDiagnostics([pluginPath], { cwd, workspaceInfo: { rootPath: cwd } });
if (failures.length || plugins.length !== 1) { console.error(JSON.stringify({ failures, plugins: plugins.length })); process.exit(2); }
const registry = core.createContributionRegistry({ extensions: plugins, setupContext: { workspaceInfo: { rootPath: cwd } } });
await registry.initialize();
const snap = registry.getRegistrySnapshot();
const tools = new Map(snap.tools.map((t) => [t.name, t]));
const mod = await import(pathToFileURL(pluginPath).href); // for VERSION
let lastResult;
globalThis[Symbol.for("spindoctor-qwerty.result-observer")] = (name, result) => { lastResult = { name, result }; };

if (process.argv.includes("--describe")) {
  const rules = [];
  for (const r of snap.rules) rules.push({ id: r.id, whenToolAvailable: r.whenToolAvailable, length: (typeof r.content === "function" ? await r.content() : r.content).length,
    honest: /not a\s+quantum computer/.test(typeof r.content === "function" ? await r.content() : r.content) });
  const cmds = {};
  for (const c of snap.commands) cmds[c.name] = await c.handler(c.name === "spindoctor-functions" ? "gates" : c.name === "spindoctor-preset" ? "qc-001 shots=10" : "theory.md");
  console.log(JSON.stringify({ plugin: plugins[0].name, capabilities: plugins[0].manifest.capabilities, warnings, tools: [...tools.keys()],
    toolFields: Object.keys(snap.tools[0]).sort(), rules, commands: Object.fromEntries(Object.entries(cmds).map(([k, v]) => [k, { reply: v.reply ? v.reply.slice(0, 200) : undefined, replyLength: v.reply ? v.reply.length : 0, submitPrompt: v.submitPrompt }])),
    hooks: plugins[0].hooks ? Object.keys(plugins[0].hooks) : [] }));
  process.exit(0);
}

const send = (o) => process.stdout.write(JSON.stringify(o) + "\n");
const rl = readline.createInterface({ input: process.stdin });
let queue = Promise.resolve();
rl.on("line", (line) => { queue = queue.then(() => handle(line)); });
async function handle(line) {
  if (!line.trim()) return;
  const msg = JSON.parse(line); const id = msg.id;
  if (id === undefined || id === null) return;
  try {
    if (msg.method === "initialize") send({ jsonrpc: "2.0", id, result: { protocolVersion: "2025-06-18", capabilities: { tools: {} }, serverInfo: { name: "spindoctor-qwerty (Cline plugin via @cline/core)", version: mod.VERSION } } });
    else if (msg.method === "tools/list") send({ jsonrpc: "2.0", id, result: { tools: [...tools.values()].map((t) => ({ name: t.name, description: t.description, inputSchema: t.inputSchema })) } });
    else if (msg.method === "tools/call") {
      const t = tools.get(msg.params.name); if (!t) throw new Error("unknown tool " + msg.params.name);
      const args = msg.params.arguments || {};
      lastResult = undefined;
      const text = await t.execute(args, { toolCallId: "e2e-" + id });
      // The model sees `text` (function table verbatim, else JSON, truncated past 60000 characters); the full structured
      // result of that same single call comes from the plugin's result observer.
      if (!lastResult || lastResult.name !== t.name) throw new Error("no structured result observed for " + t.name);
      const structured = lastResult.result;
      if (typeof text !== "string" || !text.length) throw new Error("execute() returned no text");
      send({ jsonrpc: "2.0", id, result: { content: [{ type: "text", text }], structuredContent: structured, isError: !structured.ok } });
    } else send({ jsonrpc: "2.0", id, error: { code: -32601, message: "Method not found" } });
  } catch (e) { send({ jsonrpc: "2.0", id, error: { code: -32603, message: String(e && e.message || e) } }); }
}
