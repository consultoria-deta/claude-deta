#!/usr/bin/env node
/**
 * html_to_pdf.mjs — Convierte HTML a PDF usando Puppeteer (Chrome headless)
 *
 * Uso:
 *   node html_to_pdf.mjs <archivo.html> [archivo.pdf]
 *
 * Si no se pasa el segundo argumento, genera el PDF en la misma carpeta
 * con el mismo nombre pero extensión .pdf.
 *
 * Equivalente a wkhtmltopdf pero funcional en Apple Silicon.
 * Respeta @media print y @page del CSS.
 * Sin headers, sin footers, sin fecha ni URL.
 */

import { launch } from "puppeteer";
import { resolve, dirname, basename, extname } from "path";
import { existsSync } from "fs";

const htmlArg = process.argv[2];

if (!htmlArg) {
  console.error("Uso: node html_to_pdf.mjs <archivo.html> [archivo.pdf]");
  process.exit(1);
}

const htmlPath = resolve(htmlArg);

if (!existsSync(htmlPath)) {
  console.error(`No encontrado: ${htmlPath}`);
  process.exit(1);
}

const pdfPath = process.argv[3]
  ? resolve(process.argv[3])
  : resolve(dirname(htmlPath), basename(htmlPath, extname(htmlPath)) + ".pdf");

console.log("Convirtiendo...");

const browser = await launch({ headless: true });
const page = await browser.newPage();

await page.goto(`file://${htmlPath}`, { waitUntil: "networkidle0" });

await page.pdf({
  path: pdfPath,
  format: "A4",
  printBackground: true,
  displayHeaderFooter: false,
  preferCSSPageSize: true,
});

await browser.close();

console.log(`PDF generado: ${pdfPath}`);
