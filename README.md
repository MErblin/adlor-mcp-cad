# 📐 Adlor MCP CAD

Open-Source **Model Context Protocol (MCP)** server bridging AI agents (Cursor, Claude Code, Windsurf) to Autodesk Revit, IFC geometry, and ASME/HSE design standards.

---

## ⚡ Features
- **ASME B31.3-2022 Verification**: Computes minimum required pipe wall thickness and schedule recommendations under §304.1.2.
- **UK HSE ACoP L8 Auditing**: Verifies thermal domestic water loops against Legionella growth parameters (calorifier >= 60°C, return >= 50°C, cold < 20°C).
- **3D BIM Property Inspector**: Returns element spatial coordinates, clearance deltas, and clash reports over standard JSON-RPC 2.0.

---

## 🚀 Quick Start

### Installation
```bash
pip install -e ./mcp/adlor-mcp-cad
```

### Configure in Claude Desktop / Cursor
Add to your `claude_desktop_config.json` or `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "adlor-mcp-cad": {
      "command": "adlor-mcp-cad",
      "args": []
    }
  }
}
```

---

## 🏛️ Enterprise Edition
For in-tenant Azure AI Search vector synchronization, live bi-directional Revit add-in synchronization, and multi-user RBAC model locks, visit [Adlor Labs](https://adlor-lab-platform.vercel.app/consulting).
