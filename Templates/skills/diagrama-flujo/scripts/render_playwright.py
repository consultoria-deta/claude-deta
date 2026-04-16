"""
render_playwright.py
Renderiza un HTML de diagrama a PNG usando Playwright (headless).

Uso:
    python3 render_playwright.py diagrama.html [output.png]
    O desde código: render_png(html_path) → png_path

Dependencias:
    pip install playwright
    playwright install chromium
"""
import sys
import os


def render_png(html_path: str, png_path: str = None, wait_ms: int = 600) -> str:
    """
    Renderiza el HTML a PNG full-page.
    wait_ms: milisegundos de espera después del load para que corra el JS de flechas.
    Retorna la ruta del PNG generado.
    """
    from playwright.sync_api import sync_playwright

    if png_path is None:
        base = os.path.splitext(html_path)[0]
        png_path = base + ".png"

    abs_html = os.path.abspath(html_path)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"file://{abs_html}", wait_until="load")
        page.wait_for_timeout(wait_ms)  # espera que el JS de flechas termine
        page.screenshot(path=png_path, full_page=True)
        browser.close()

    return png_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 render_playwright.py diagrama.html [output.png]")
        sys.exit(1)

    html = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    path = render_png(html, out)
    size_kb = os.path.getsize(path) // 1024
    print(f"PNG generado: {path} ({size_kb} KB)")
