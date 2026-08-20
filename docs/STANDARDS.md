# Adlor MCP CAD: Engineering Standards & Citation Reference

This document catalogs the engineering compliance formulas, standards tables, and regulatory citations implemented across all `adlor-mcp-cad` tools.

---

## 📐 Supported Engineering Standards & Tools

| Standard | Description | Primary Citation | Key Formulas / Tables |
|---|---|---|---|
| **ASME B31.3-2022** | Process Piping Design & Wall Thickness | ASME B31.3 §304.1.2 | $t_m = \frac{P \cdot D}{2(S \cdot E + P \cdot Y)} + c$ |
| **UK HSE ACoP L8 / HSG274** | Legionella Risk Control in Water Systems | HSG274 Part 2 §2.10, §2.14, §2.16 | Calorifier $\ge 60^\circ\text{C}$, Flow $\ge 50^\circ\text{C}$, Return $\ge 50^\circ\text{C}$, Cold $< 20^\circ\text{C}$ |
| **BS EN 12056-2:2000** | Gravity Drainage Systems Inside Buildings | BS EN 12056-2 §6.3.2 & Table 6 | $Q_{ww} = K \sqrt{\sum DU}$ |
| **BS 8558:2015 & Part G3** | Hot Water Supply & Scald Prevention | BS 8558:2015 Table 1, Part G §3.6 | Washbasin $\le 41^\circ\text{C}$, Shower $\le 41^\circ\text{C}$, Bath $\le 44^\circ\text{C}$ |
| **CIBSE Guide B / BS EN 12828** | Hydronic Heating & Chilled Water Pipe Sizing | CIBSE Guide B1 §3.4 | $\dot{m} = \frac{Q}{c_p \Delta T}$, $\Delta P/L = \frac{f \rho v^2}{2 D}$ |

---

## 🛠️ FastMCP Integration with AI Clients

Add the following to your `claude_desktop_config.json` or Cursor MCP settings:

```json
{
  "mcpServers": {
    "adlor-mcp-cad": {
      "command": "uvx",
      "args": ["adlor-mcp-cad"]
    }
  }
}
```
