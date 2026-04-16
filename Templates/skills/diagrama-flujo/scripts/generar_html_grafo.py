"""
generar_html_grafo.py  v2
Convierte el JSON de diagrama DETA en HTML listo para Playwright.

Mejoras v2:
- Conectores ortogonales (codos en ángulo recto, estilo Lucidchart)
- Detección y corrección automática de colisiones fila+columna
- Grid ajustado al número real de roles (sin columna vacía)
- Nodos más grandes y mejor proporcionados
- Etiquetas de flecha con fondo blanco (no se superponen al conector)
- Salidas de rombo: Sí → derecha, No → izquierda (cuando hay destino lateral)

Uso:
    python3 generar_html_grafo.py diagrama.json [output.html]
    o desde código: generar_html(data_dict, output_path?) → html_path
"""
import json
import sys
import os
from collections import defaultdict
from datetime import datetime

# ── Paleta de roles ────────────────────────────────────────────────────────────
# (color_cabecera_hex, color_fondo_claro_hex)
ROLE_PALETTE = [
    ("#0B2F4E", "#D6E4F0"),   # NAVY DETA
    ("#1A7A96", "#D1EEF5"),   # CYAN DETA
    ("#1E8449", "#D5F5E3"),   # Verde
    ("#7D3C98", "#EDE2F5"),   # Morado
    ("#B7770D", "#FDF2D0"),   # Ámbar
    ("#C0392B", "#FDDEDE"),   # Rojo
    ("#16A085", "#D1F2EB"),   # Teal
    ("#2C3E50", "#EAECEE"),   # Gris oscuro
]

# ── Dimensiones ────────────────────────────────────────────────────────────────
COL_W    = 210   # ancho de columna (swimlane)
ROW_H    = 100   # alto de fila
NODE_W   = 170   # ancho de nodo proceso/externo
NODE_H   = 56    # alto de nodo proceso/externo
DIAM_W   = 155   # ancho de rombo
DIAM_H   = 75    # alto de rombo
TERM_W   = 110   # ancho terminal (inicio/fin)
TERM_H   = 38    # alto terminal
HDR_H    = 46    # alto cabecera swimlane
DOC_H    = 46    # alto cabecera documento


def _resolve_collisions(nodos: list, role_idx: dict) -> list:
    """
    Si dos nodos comparten (columna, fila), desplaza el segundo hacia abajo
    hasta encontrar una fila libre. Modifica 'fila' in-place y retorna la lista.
    """
    occupied: set = set()
    for n in nodos:
        col = role_idx.get(n.get("rol", ""), 0)
        row = n.get("fila", 1)
        while (col, row) in occupied:
            row += 1
        n["fila"] = row
        occupied.add((col, row))
    return nodos


def build_html(data: dict) -> str:
    roles   = data["roles"]
    nodos   = data["nodos"]
    titulo  = data.get("titulo", "Proceso")
    cliente = data.get("cliente", "")
    fecha   = data.get("fecha", datetime.now().strftime("%d/%m/%Y"))

    role_idx    = {r: i for i, r in enumerate(roles)}
    role_colors = {r: ROLE_PALETTE[i % len(ROLE_PALETTE)] for i, r in enumerate(roles)}

    # ── 1. Resolver colisiones ─────────────────────────────────────────────────
    nodos = _resolve_collisions(list(nodos), role_idx)

    n_cols = len(roles)
    n_rows = max(n.get("fila", 1) for n in nodos)

    grid_w = n_cols * COL_W
    grid_h = n_rows * ROW_H + 30

    # ── 2. CSS dinámico por rol ────────────────────────────────────────────────
    role_css = ""
    for role, (hdr, _bg) in role_colors.items():
        safe = _safe(role)
        role_css += f".node-{safe} {{ background:{hdr}; color:white; border-color:{hdr}; }}\n"
        role_css += f".swlane-hdr-{safe} {{ background:{hdr}; }}\n"

    # ── 3. Cabeceras de swimlane ───────────────────────────────────────────────
    swlane_hdrs = ""
    for role in roles:
        safe = _safe(role)
        swlane_hdrs += f'<div class="swlane-hdr swlane-hdr-{safe}">{role}</div>\n'

    # ── 4. Bandas de fondo por columna ────────────────────────────────────────
    stripes = ""
    for i, role in enumerate(roles):
        _, bg = role_colors[role]
        x = i * COL_W
        stripes += (
            f'<div style="position:absolute;left:{x}px;top:0;width:{COL_W}px;height:100%;'
            f'background:{bg}18;border-right:1px solid #d8dde6;box-sizing:border-box;"></div>\n'
        )

    # ── 5. Nodos HTML ──────────────────────────────────────────────────────────
    nodes_html   = ""
    conexiones_js = []

    for nodo in nodos:
        nid  = nodo["id"]
        tipo = nodo.get("tipo", "proceso")
        rol  = nodo.get("rol", roles[0])
        text = nodo.get("texto", "").replace("\n", "<br>")
        row  = nodo.get("fila", 1)
        conns = nodo.get("conexiones", [])

        col_i = role_idx.get(rol, 0)
        cx = col_i * COL_W + COL_W // 2
        cy = (row - 1) * ROW_H + ROW_H // 2

        if tipo == "decision":
            w, h = DIAM_W, DIAM_H
            css_extra = "node-decision"
        elif tipo in ("inicio", "fin"):
            w, h = TERM_W, TERM_H
            css_extra = "node-terminal"
        elif tipo == "externo":
            w, h = NODE_W, NODE_H
            css_extra = "node-externo"
        else:
            w, h = NODE_W, NODE_H
            safe = _safe(rol)
            css_extra = f"node-proceso node-{safe}"

        x, y = cx - w // 2, cy - h // 2
        nodes_html += (
            f'<div id="{nid}" class="node {css_extra}" '
            f'style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;"'
            f'data-cx="{cx}" data-cy="{cy}">'
            f'<span class="node-text">{text}</span></div>\n'
        )

        for c in conns:
            conexiones_js.append({
                "from":    nid,
                "to":      c["a"],
                "tipo":    c.get("tipo", "normal"),
                "label":   c.get("etiqueta"),
                "srcTipo": tipo,
            })

    conn_json = json.dumps(conexiones_js, ensure_ascii=False)

    # ── 6. HTML completo ───────────────────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>{titulo}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:'Arial',Helvetica,sans-serif;background:#fff;}}

/* ── Cabecera documento ── */
.doc-header{{
  display:grid;
  grid-template-columns:110px 1fr 160px;
  background:#0B2F4E;color:white;
  padding:10px 20px;align-items:center;gap:12px;
  height:{DOC_H}px;
}}
.doc-logo{{font-weight:900;font-size:22px;letter-spacing:3px;color:#C8A84B;}}
.doc-title{{text-align:center;font-size:13px;font-weight:bold;line-height:1.3;}}
.doc-meta{{text-align:right;font-size:11px;line-height:1.6;opacity:.9;}}

/* ── Cabeceras swimlane ── */
.swlane-headers{{
  display:grid;
  grid-template-columns:repeat({n_cols},{COL_W}px);
  width:{grid_w}px;
  border-bottom:3px solid #0B2F4E;
}}
.swlane-hdr{{
  color:white;font-weight:bold;text-align:center;
  padding:8px 6px;font-size:12px;
  height:{HDR_H}px;display:flex;align-items:center;justify-content:center;
}}

/* ── Área de diagrama ── */
.diagram-wrapper{{
  position:relative;
  width:{grid_w}px;
  min-height:{grid_h}px;
  overflow:visible;
}}

/* ── Nodos ── */
.node{{
  position:absolute;
  display:flex;align-items:center;justify-content:center;
  text-align:center;z-index:2;
}}
.node-text{{font-size:11px;line-height:1.4;padding:4px 8px;display:block;}}
.node-proceso{{
  border-radius:5px;border:2px solid transparent;
  box-shadow:0 2px 4px rgba(0,0,0,.18);
}}
.node-decision{{
  clip-path:polygon(50% 0%,100% 50%,50% 100%,0% 50%);
  background:#F4D03F;color:#2C3E50;font-weight:bold;
  box-shadow:0 2px 4px rgba(0,0,0,.15);
}}
.node-decision .node-text{{font-size:10px;padding:8px 18px;font-weight:bold;}}
.node-terminal{{
  border-radius:20px;background:#0B2F4E;color:white;
  font-weight:bold;font-size:12px;
  box-shadow:0 2px 4px rgba(0,0,0,.25);
}}
.node-externo{{
  background:#95A5A6;color:white;border-radius:5px;
  border:2px dashed #7F8C8D;font-style:italic;
  box-shadow:0 1px 3px rgba(0,0,0,.15);
}}

/* ── Capa de flechas ── */
#arrow-svg{{
  position:absolute;top:0;left:0;
  width:{grid_w}px;height:100%;
  pointer-events:none;overflow:visible;z-index:1;
}}

{role_css}
</style>
</head>
<body>

<div class="doc-header">
  <div class="doc-logo">DETA</div>
  <div class="doc-title">{titulo}</div>
  <div class="doc-meta">{cliente}<br><span style="font-size:10px">{fecha}</span></div>
</div>

<div class="swlane-headers">{swlane_hdrs}</div>

<div class="diagram-wrapper" id="dw">
  {stripes}
  <svg id="arrow-svg" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <marker id="ah-normal" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto">
        <path d="M0,0 L0,8 L9,4 z" fill="#555"/>
      </marker>
      <marker id="ah-si" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto">
        <path d="M0,0 L0,8 L9,4 z" fill="#1E8449"/>
      </marker>
      <marker id="ah-no" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto">
        <path d="M0,0 L0,8 L9,4 z" fill="#C0392B"/>
      </marker>
    </defs>
  </svg>
  {nodes_html}
</div>

<script>
(function(){{
  var CONNS = {conn_json};
  var COLORS = {{normal:"#555555", si:"#1E8449", no:"#C0392B"}};
  var R = 6; // radio de esquina redondeada

  function rect(id){{
    var dw = document.getElementById("dw");
    var el = document.getElementById(id);
    if(!el) return null;
    var er = el.getBoundingClientRect();
    var wr = dw.getBoundingClientRect();
    return {{
      left:   er.left - wr.left,
      top:    er.top  - wr.top,
      right:  er.right - wr.left,
      bottom: er.bottom - wr.top,
      cx:     er.left - wr.left + er.width/2,
      cy:     er.top  - wr.top  + er.height/2,
      w:      er.width,
      h:      er.height
    }};
  }}

  /* Conector ortogonal con esquinas redondeadas */
  function orthPath(x1,y1,x2,y2){{
    var dx = x2-x1, dy = y2-y1;

    /* ── mismo eje vertical: línea recta ── */
    if(Math.abs(dx) < 6){{
      return "M "+x1+" "+y1+" L "+x2+" "+y2;
    }}

    /* ── hacia abajo: codo en la mitad vertical ── */
    if(dy >= 0){{
      var by = y1 + dy*0.5;
      var sx = dx > 0 ? 1 : -1;
      /* esquinas redondeadas */
      return (
        "M "+x1+" "+y1+
        " L "+x1+" "+(by-R)+
        " Q "+x1+" "+by+" "+(x1+sx*R)+" "+by+
        " L "+(x2-sx*R)+" "+by+
        " Q "+x2+" "+by+" "+x2+" "+(by+R)+
        " L "+x2+" "+y2
      );
    }}

    /* ── retroalimentación (sube): bypass por el costado izquierdo ── */
    var bx = Math.min(x1,x2) - 50;
    var sy1 = y1 > y2 ? -1 : 1;
    return (
      "M "+x1+" "+y1+
      " L "+(x1-R*2)+" "+y1+
      " Q "+bx+" "+y1+" "+bx+" "+(y1+R*sy1)+
      " L "+bx+" "+(y2-R*sy1)+
      " Q "+bx+" "+y2+" "+(bx+R*2)+" "+y2+
      " L "+x2+" "+y2
    );
  }}

  function label(svg, txt, x, y, color){{
    var bg = document.createElementNS("http://www.w3.org/2000/svg","rect");
    var tw = txt.length*6+8;
    bg.setAttribute("x", x-tw/2); bg.setAttribute("y", y-10);
    bg.setAttribute("width", tw); bg.setAttribute("height", 14);
    bg.setAttribute("fill", "white"); bg.setAttribute("rx", "2");
    bg.setAttribute("opacity","0.85");
    svg.appendChild(bg);
    var t = document.createElementNS("http://www.w3.org/2000/svg","text");
    t.setAttribute("x",x); t.setAttribute("y",y);
    t.setAttribute("text-anchor","middle");
    t.setAttribute("font-size","10"); t.setAttribute("font-family","Arial,sans-serif");
    t.setAttribute("font-weight","bold"); t.setAttribute("fill",color);
    t.textContent = txt;
    svg.appendChild(t);
  }}

  function draw(){{
    var svg = document.getElementById("arrow-svg");
    var dw  = document.getElementById("dw");
    /* ajustar alto del SVG al contenido real */
    svg.setAttribute("height", dw.offsetHeight + 40);

    CONNS.forEach(function(c){{
      var sr = rect(c.from), tr = rect(c.to);
      if(!sr || !tr) return;

      var tipo  = c.tipo || "normal";
      var color = COLORS[tipo] || COLORS.normal;
      var isDec = c.srcTipo === "decision";

      /* ── puntos de salida / entrada ── */
      var x1,y1,x2,y2;
      x2 = tr.cx; y2 = tr.top;   /* entrada siempre por arriba del destino */

      if(isDec){{
        var goRight = tr.cx > sr.cx + 5;
        var goLeft  = tr.cx < sr.cx - 5;
        if(tipo==="si" && goRight)  {{ x1=sr.right; y1=sr.cy; x2=tr.cx; y2=tr.top; }}
        else if(tipo==="no" && goLeft)  {{ x1=sr.left;  y1=sr.cy; x2=tr.cx; y2=tr.top; }}
        else if(tipo==="si" && goLeft)  {{ x1=sr.left;  y1=sr.cy; x2=tr.cx; y2=tr.top; }}
        else if(tipo==="no" && goRight) {{ x1=sr.right; y1=sr.cy; x2=tr.cx; y2=tr.top; }}
        else {{ x1=sr.cx; y1=sr.bottom; }}  /* mismo column: sale abajo */
      }} else {{
        x1 = sr.cx;
        y1 = sr.bottom;
      }}

      var d = orthPath(x1,y1,x2,y2);
      var path = document.createElementNS("http://www.w3.org/2000/svg","path");
      path.setAttribute("d",d);
      path.setAttribute("stroke",color);
      path.setAttribute("stroke-width","2");
      path.setAttribute("fill","none");
      path.setAttribute("marker-end","url(#ah-"+tipo+")");
      svg.appendChild(path);

      /* etiqueta en el punto de quiebre horizontal */
      if(c.label){{
        var lx = (x1+x2)/2;
        var ly = y1 + (y2-y1)*0.5;
        /* para salidas de rombo: mover la etiqueta cerca del punto de salida */
        if(isDec){{
          lx = x1 + (x2>x1 ? 18 : -18);
          ly = y1;
        }}
        label(svg, c.label, lx, ly, color);
      }}
    }});
  }}

  if(document.readyState==="loading"){{
    document.addEventListener("DOMContentLoaded",draw);
  }}else{{
    draw();
  }}
}})();
</script>

</body>
</html>
"""
    return html


def generar_html(data: dict, output_path: str = None) -> str:
    html = build_html(data)
    if output_path is None:
        nombre = data.get("titulo","diagrama").replace(" ","_").replace("/","-")
        output_path = f"/tmp/{nombre}_diagrama.html"
    with open(output_path,"w",encoding="utf-8") as f:
        f.write(html)
    return output_path


def _safe(s: str) -> str:
    return s.replace(" ","_").replace("&","and").replace("/","_").replace("+","_")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 generar_html_grafo.py diagrama.json [output.html]")
        sys.exit(1)
    with open(sys.argv[1],encoding="utf-8") as f:
        data = json.load(f)
    out = sys.argv[2] if len(sys.argv) > 2 else None
    path = generar_html(data, out)
    print(f"HTML generado: {path}")
