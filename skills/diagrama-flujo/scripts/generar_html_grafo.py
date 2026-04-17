"""
generar_html_grafo.py  v3
Modelo: grid 2D libre — cada nodo define su (col, fila) explícitamente.
Color identifica al actor (con leyenda en footer). Sin swimlane columns.
Conectores ortogonales con esquinas redondeadas.

Cambios vs v2:
- Eliminadas cabeceras de swimlane
- Cada nodo lleva col/fila absolutos (Claude los asigna al generar el JSON)
- roles = [{nombre, color}] — paleta personalizable
- Leyenda al pie del diagrama
- Cabecera estilo Lucidchart: logo | título | cód/versión/fecha
- Grid se expande al máximo de col/fila declarados

Uso:
    python3 generar_html_grafo.py diagrama.json [output.html]
    o desde código: generar_html(data_dict, output_path?) → html_path
"""
import json
import sys
import os
from datetime import datetime

# Paleta por defecto si el usuario no especifica colores
DEFAULT_COLORS = [
    "#C0392B",  # rojo       (Vendedor)
    "#2980B9",  # azul       (Compras)
    "#8E44AD",  # morado     (Crédito y Cobranza)
    "#27AE60",  # verde      (Facturación)
    "#D68910",  # ámbar      (Almacén)
    "#16A085",  # teal
    "#2C3E50",  # gris oscuro
    "#1A5276",  # azul marino
]

# ── Dimensiones ────────────────────────────────────────────────────────────────
COL_W   = 175   # ancho de celda de grid  (era 160)
ROW_H   = 115   # alto de celda de grid   (era 110)
NODE_W  = 152   # ancho nodo proceso/externo (era 140)
NODE_H  = 52    # alto nodo proceso/externo
DIAM_W  = 130   # ancho rombo
DIAM_H  = 70    # alto rombo
TERM_W  = 100   # ancho terminal (inicio/fin)
TERM_H  = 36    # alto terminal


def _hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _lighten(hex_color, factor=0.85):
    """Devuelve una versión más clara del color para fondos."""
    r, g, b = _hex_to_rgb(hex_color)
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return f"#{r:02X}{g:02X}{b:02X}"


def build_html(data: dict) -> str:
    # ── Metadatos ──────────────────────────────────────────────────────────────
    titulo   = data.get("titulo", "Proceso")
    cliente  = data.get("cliente", "")
    fecha    = data.get("fecha", datetime.now().strftime("%d/%m/%Y"))
    codigo   = data.get("codigo", "")       # ej. "DIA01008"
    version  = data.get("version", "1")
    nodos    = data["nodos"]

    # ── Roles / colores ────────────────────────────────────────────────────────
    roles_raw = data.get("roles", [])
    role_color = {}
    for i, r in enumerate(roles_raw):
        if isinstance(r, dict):
            role_color[r["nombre"]] = r.get("color", DEFAULT_COLORS[i % len(DEFAULT_COLORS)])
        else:
            role_color[r] = DEFAULT_COLORS[i % len(DEFAULT_COLORS)]

    def get_color(rol):
        if rol in role_color:
            return role_color[rol]
        # auto-asignar color si el rol no estaba declarado
        idx = len(role_color)
        c = DEFAULT_COLORS[idx % len(DEFAULT_COLORS)]
        role_color[rol] = c
        return c

    # ── Dimensiones del grid ───────────────────────────────────────────────────
    max_col  = max(n.get("col", 1) for n in nodos)
    max_fila = max(n.get("fila", 1) for n in nodos)
    grid_w   = max_col * COL_W + 20
    grid_h   = max_fila * ROW_H + 40

    # ── Cabecera (estilo Lucidchart) ───────────────────────────────────────────
    meta_html = ""
    if codigo:
        meta_html += f'<div style="font-weight:bold;font-size:13px">{codigo}</div>'
    if version:
        meta_html += f'<div style="font-size:11px">Versión {version}</div>'
    if fecha:
        meta_html += f'<div style="font-size:11px">{fecha}</div>'

    header_html = f"""
<div class="doc-header">
  <div class="doc-logo">{cliente or "DETA"}</div>
  <div class="doc-title">{titulo}</div>
  <div class="doc-meta">{meta_html}</div>
</div>"""

    # ── Nodos HTML ─────────────────────────────────────────────────────────────
    nodes_html    = ""
    conexiones_js = []

    for nodo in nodos:
        nid   = nodo["id"]
        tipo  = nodo.get("tipo", "proceso")
        rol   = nodo.get("rol", "")
        texto = nodo.get("texto", "").replace("\n", "<br>")
        col   = nodo.get("col", 1)
        fila  = nodo.get("fila", 1)
        conns = nodo.get("conexiones", [])

        color = get_color(rol)
        light = _lighten(color, 0.78)

        # Centro de la celda
        cx = (col - 1) * COL_W + COL_W // 2
        cy = (fila - 1) * ROW_H + ROW_H // 2

        if tipo == "decision":
            w, h = DIAM_W, DIAM_H
            style = (
                f"left:{cx-w//2}px;top:{cy-h//2}px;width:{w}px;height:{h}px;"
                f"clip-path:polygon(50% 0%,100% 50%,50% 100%,0% 50%);"
                f"background:#F4D03F;color:#2C3E50;font-weight:bold;"
                f"display:flex;align-items:center;justify-content:center;"
                f"text-align:center;"
            )
            extra_css = "node-decision"
        elif tipo in ("inicio", "fin"):
            w, h = TERM_W, TERM_H
            bg = "#0B2F4E" if tipo == "fin" else "#555"
            style = (
                f"left:{cx-w//2}px;top:{cy-h//2}px;width:{w}px;height:{h}px;"
                f"border-radius:20px;background:{bg};color:white;font-weight:bold;"
                f"display:flex;align-items:center;justify-content:center;"
                f"text-align:center;"
            )
            extra_css = "node-terminal"
        elif tipo == "externo":
            w, h = NODE_W, NODE_H
            style = (
                f"left:{cx-w//2}px;top:{cy-h//2}px;width:{w}px;height:{h}px;"
                f"background:#BDC3C7;color:#2C3E50;border-radius:4px;"
                f"border:2px dashed #95A5A6;"
                f"display:flex;align-items:center;justify-content:center;"
                f"text-align:center;"
            )
            extra_css = "node-externo"
        elif tipo == "proceso_especial":
            # Hito destacado — navy oscuro para máxima prominencia
            w, h = NODE_W, NODE_H
            style = (
                f"left:{cx-w//2}px;top:{cy-h//2}px;width:{w}px;height:{h}px;"
                f"background:#154360;color:white;border-radius:4px;"
                f"border:2px solid #0B2F4E;"
                f"display:flex;align-items:center;justify-content:center;"
                f"text-align:center;font-weight:bold;"
                f"box-shadow:0 3px 7px rgba(0,0,0,.35);"
            )
            extra_css = "node-especial"
        else:  # proceso normal
            w, h = NODE_W, NODE_H
            style = (
                f"left:{cx-w//2}px;top:{cy-h//2}px;width:{w}px;height:{h}px;"
                f"background:{color};color:white;border-radius:4px;"
                f"border:2px solid {color};"
                f"display:flex;align-items:center;justify-content:center;"
                f"text-align:center;"
                f"box-shadow:0 2px 4px rgba(0,0,0,.2);"
            )
            extra_css = "node-proceso"

        nodes_html += (
            f'<div id="{nid}" class="node {extra_css}" '
            f'style="position:absolute;z-index:2;{style}">'
            f'<span style="font-size:10px;line-height:1.35;padding:3px 7px;">{texto}</span>'
            f'</div>\n'
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

    # ── Leyenda de roles ───────────────────────────────────────────────────────
    leyenda_html = '<div class="legend"><span class="legend-title">Actores:</span>'
    for nombre, color in role_color.items():
        leyenda_html += (
            f'<span class="legend-item" style="background:{color}">{nombre}</span>'
        )
    leyenda_html += "</div>"

    # ── HTML completo ──────────────────────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>{titulo}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:'Arial',Helvetica,sans-serif;background:#fff;}}

/* Cabecera tipo Lucidchart */
.doc-header{{
  display:grid;
  grid-template-columns:130px 1fr 180px;
  border:2px solid #2C3E50;
  background:white;
}}
.doc-logo{{
  border-right:2px solid #2C3E50;
  display:flex;align-items:center;justify-content:center;
  font-size:22px;font-weight:900;color:#0B2F4E;
  padding:10px;letter-spacing:2px;
}}
.doc-title{{
  display:flex;align-items:center;justify-content:center;
  font-size:16px;font-weight:bold;color:#2C3E50;
  padding:10px;border-right:2px solid #2C3E50;
  text-align:center;
}}
.doc-meta{{
  display:flex;flex-direction:column;justify-content:center;
  padding:8px 14px;font-size:12px;color:#2C3E50;
  line-height:1.8;text-align:right;
}}

/* Área diagrama */
.diagram-wrapper{{
  position:relative;
  width:{grid_w}px;
  min-height:{grid_h}px;
  background:white;
  overflow:visible;
}}

/* Capa SVG de flechas */
#arrow-svg{{
  position:absolute;top:0;left:0;
  width:{grid_w}px;height:{grid_h}px;
  pointer-events:none;overflow:visible;z-index:1;
}}

/* Leyenda */
.legend{{
  display:flex;flex-wrap:wrap;align-items:center;
  gap:10px;padding:12px 16px;
  border-top:1px solid #ddd;background:#FAFAFA;
  font-size:11px;
}}
.legend-title{{font-weight:bold;color:#555;margin-right:4px;}}
.legend-item{{
  padding:4px 12px;border-radius:3px;color:white;
  font-size:10px;font-weight:bold;
}}
</style>
</head>
<body>

{header_html}

<div class="diagram-wrapper" id="dw">
  <svg id="arrow-svg" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <marker id="ah-normal" markerWidth="8" markerHeight="8" refX="6" refY="3.5" orient="auto">
        <path d="M0,0 L0,7 L8,3.5 z" fill="#555"/>
      </marker>
      <marker id="ah-si" markerWidth="8" markerHeight="8" refX="6" refY="3.5" orient="auto">
        <path d="M0,0 L0,7 L8,3.5 z" fill="#1E8449"/>
      </marker>
      <marker id="ah-no" markerWidth="8" markerHeight="8" refX="6" refY="3.5" orient="auto">
        <path d="M0,0 L0,7 L8,3.5 z" fill="#C0392B"/>
      </marker>
    </defs>
  </svg>
  {nodes_html}
</div>

{leyenda_html}

<script>
(function(){{
  var CONNS  = {conn_json};
  var COLORS = {{normal:"#666", si:"#1E8449", no:"#C0392B"}};
  var R = 7;

  function box(id){{
    var dw = document.getElementById("dw");
    var el = document.getElementById(id);
    if(!el) return null;
    var er = el.getBoundingClientRect();
    var wr = dw.getBoundingClientRect();
    return {{
      l: er.left-wr.left, t: er.top-wr.top,
      r: er.right-wr.left, b: er.bottom-wr.top,
      cx: er.left-wr.left+er.width/2,
      cy: er.top-wr.top+er.height/2
    }};
  }}

  /* Conector ortogonal con esquinas redondeadas */
  function orth(x1,y1,x2,y2){{
    var dx=x2-x1, dy=y2-y1;
    if(Math.abs(dx)<5) return "M "+x1+" "+y1+" L "+x2+" "+y2;
    if(dy>10){{
      /* hacia abajo: codo en la mitad vertical */
      var by=y1+dy*0.5, sx=dx>0?1:-1;
      return (
        "M "+x1+" "+y1+
        " L "+x1+" "+(by-R)+
        " Q "+x1+" "+by+" "+(x1+sx*R)+" "+by+
        " L "+(x2-sx*R)+" "+by+
        " Q "+x2+" "+by+" "+x2+" "+(by+R)+
        " L "+x2+" "+y2
      );
    }}
    /* retroalimentación (sube) o misma fila: bypass lateral */
    var bx = x1<x2 ? Math.min(x1,x2)-45 : Math.max(x1,x2)+45;
    var sign = y1>y2?-1:1;
    return (
      "M "+x1+" "+y1+
      " L "+(x1+(bx>x1?R:-R))+" "+y1+
      " Q "+bx+" "+y1+" "+bx+" "+(y1+sign*R)+
      " L "+bx+" "+(y2-sign*R)+
      " Q "+bx+" "+y2+" "+(bx+(bx>x2?-R:R))+" "+y2+
      " L "+x2+" "+y2
    );
  }}

  function addLabel(svg, txt, lx, ly, color){{
    var w=txt.length*6.5+10;
    var bg=document.createElementNS("http://www.w3.org/2000/svg","rect");
    bg.setAttribute("x",lx-w/2); bg.setAttribute("y",ly-11);
    bg.setAttribute("width",w); bg.setAttribute("height",15);
    bg.setAttribute("fill","white"); bg.setAttribute("rx","2");
    bg.setAttribute("opacity","0.9");
    svg.appendChild(bg);
    var t=document.createElementNS("http://www.w3.org/2000/svg","text");
    t.setAttribute("x",lx); t.setAttribute("y",ly);
    t.setAttribute("text-anchor","middle");
    t.setAttribute("font-size","10"); t.setAttribute("font-family","Arial,sans-serif");
    t.setAttribute("font-weight","bold"); t.setAttribute("fill",color);
    t.textContent=txt;
    svg.appendChild(t);
  }}

  function drawAll(){{
    var svg=document.getElementById("arrow-svg");
    var dw =document.getElementById("dw");
    svg.setAttribute("height", dw.scrollHeight+50);

    /* ── Fan-in offset: contar cuántas flechas entran por la parte superior de cada nodo ── */
    var topCount={{}}, topIdx={{}};
    CONNS.forEach(function(c){{
      var s=box(c.from), t=box(c.to);
      if(!s||!t) return;
      var isDec=(c.srcTipo==="decision");
      var goR=t.cx>s.cx+5, goL=t.cx<s.cx-5;
      /* Esta conexión entra por el tope si: no es decision lateral y va hacia abajo */
      var entraTop = !(isDec&&(goR||goL)) && (t.cy > s.cy+5);
      if(entraTop){{
        topCount[c.to]=(topCount[c.to]||0)+1;
        if(topIdx[c.to]===undefined) topIdx[c.to]=0;
      }}
    }});
    /* resetear índices para el loop de dibujo */
    var topCur={{}};
    Object.keys(topIdx).forEach(function(k){{topCur[k]=0;}});

    CONNS.forEach(function(c){{
      var s=box(c.from), t=box(c.to);
      if(!s||!t) return;
      var tipo=c.tipo||"normal";
      var color=COLORS[tipo]||COLORS.normal;
      var isDec=(c.srcTipo==="decision");

      var x1,y1,x2=t.cx,y2=t.t;
      var goR=t.cx>s.cx+5, goL=t.cx<s.cx-5;

      if(isDec){{
        if(goR)       {{x1=s.r; y1=s.cy;}}
        else if(goL)  {{x1=s.l; y1=s.cy;}}
        else          {{x1=s.cx; y1=s.b;}}
        /* entrada lateral cuando viene desde el costado */
        if(goR) {{x2=t.l; y2=t.cy;}}
        else if(goL) {{x2=t.r; y2=t.cy;}}
      }} else {{
        /* Feedback (sube): salir por el tope del nodo fuente */
        if(t.cy < s.cy - 5){{
          x1=s.cx; y1=s.t;
          /* entrar por el tope del nodo destino */
          x2=t.cx; y2=t.t;
        }} else {{
          x1=s.cx; y1=s.b;
        }}
      }}

      /* Fan-in: distribuir entradas por el tope */
      var entraTop = !(isDec&&(goR||goL)) && (t.cy > s.cy+5);
      if(entraTop && topCount[c.to]>1){{
        var cnt=topCount[c.to];
        var idx=(topCur[c.to]||0);
        topCur[c.to]=idx+1;
        var spread=(cnt-1)*7;
        x2 = t.cx - spread/2 + idx*7;
      }}

      var d=orth(x1,y1,x2,y2);
      var path=document.createElementNS("http://www.w3.org/2000/svg","path");
      path.setAttribute("d",d);
      path.setAttribute("stroke",color);
      path.setAttribute("stroke-width","1.8");
      path.setAttribute("fill","none");
      path.setAttribute("marker-end","url(#ah-"+tipo+")");
      svg.appendChild(path);

      if(c.label){{
        var lx,ly;
        if(isDec){{
          /* Etiqueta junto a la punta del rombo de donde sale, no a la altura del nodo destino */
          if(goR)       {{lx=s.r+22; ly=s.cy-9;}}
          else if(goL)  {{lx=s.l-22; ly=s.cy-9;}}
          else          {{lx=s.cx+10; ly=s.b+14;}}
        }}else{{
          lx=(x1+x2)/2+5; ly=(y1+y2)/2;
        }}
        addLabel(svg,c.label,lx,ly,color);
      }}
    }});
  }}

  if(document.readyState==="loading")
    document.addEventListener("DOMContentLoaded",drawAll);
  else drawAll();
}})();
</script>
</body>
</html>
"""
    return html


def generar_html(data: dict, output_path: str = None) -> str:
    html = build_html(data)
    if not output_path:
        nombre = data.get("titulo","diagrama").replace(" ","_").replace("/","-")
        output_path = f"/tmp/{nombre}_diagrama.html"
    with open(output_path,"w",encoding="utf-8") as f:
        f.write(html)
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 generar_html_grafo.py diagrama.json [output.html]")
        sys.exit(1)
    with open(sys.argv[1],encoding="utf-8") as f:
        data = json.load(f)
    out = sys.argv[2] if len(sys.argv) > 2 else None
    path = generar_html(data, out)
    print(f"HTML generado: {path}")
