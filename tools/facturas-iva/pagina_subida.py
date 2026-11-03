#!/usr/bin/env python3
"""Genera una página (index.html) con los archivos DENTRO, para subirlos a Drive de un clic con el conector de Drive del usuario.
Sirve cuando los archivos pesan demasiado para pasarlos por las herramientas (más de unos pocos cientos de KB).

Uso:  python3 pagina_subida.py CARPETA_ARCHIVOS ID_CARPETA_DRIVE_DESTINO SALIDA/index.html "Título de la página"
Después se publica con la herramienta Artifact (capabilities: {"mcp": {"servers": [{"server": "Google Drive", "tools": ["create_file"]}]}})
y se le dice al usuario que la abra y pulse "Subir a Drive". Luego se comprueba en Drive con search_files que están todos.
"""
import sys, os, glob, base64, json
carpeta, destino, salida, titulo = sys.argv[1:5]
datos = {os.path.basename(f): base64.b64encode(open(f, 'rb').read()).decode() for f in sorted(glob.glob(os.path.join(carpeta, '*'))) if os.path.isfile(f)}
html = '''<title>__TITULO__</title>
<style>
:root{--bg:#f2f3f7;--ink:#1b2233;--muted:#5b6679;--line:#dbe0ea;--surface:#fff;--ok:#17775a;--mal:#b4423a}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#11141b;--ink:#eceff6;--muted:#9aa5b8;--line:#2b3345;--surface:#1a1f2b;--ok:#5fcfa6;--mal:#ff8b80}}
:root[data-theme="dark"]{--bg:#11141b;--ink:#eceff6;--muted:#9aa5b8;--line:#2b3345;--surface:#1a1f2b;--ok:#5fcfa6;--mal:#ff8b80}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,sans-serif;padding:24px 16px}
main{max-width:620px;margin:0 auto;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:20px;display:flex;flex-direction:column;gap:12px}
h1{font-size:1.4rem;margin:0}p{margin:0;color:var(--muted)}
button{font:inherit;font-weight:600;border-radius:8px;padding:10px 16px;border:0;background:var(--ink);color:var(--bg);cursor:pointer;align-self:flex-start}
button:disabled{opacity:.5}
ul{margin:0;padding-left:18px;overflow-wrap:anywhere}li{margin:2px 0}.ok{color:var(--ok)}.mal{color:var(--mal)}
#estado{min-height:1.4em}a{color:var(--ink)}
</style>
<main>
  <h1>__TITULO__</h1>
  <p>Con un clic se suben los archivos a la carpeta de Drive.</p>
  <button id="subir" type="button">Subir a Drive</button>
  <p id="estado" role="status" aria-live="polite"></p>
  <ul id="lista"></ul>
  <p id="enlace"></p>
</main>
<script>
const DESTINO = "__DESTINO__";
const ENLACE = "https://drive.google.com/drive/folders/" + DESTINO;
const DATOS = __DATOS__;
const $ = s => document.querySelector(s);
function msg(e){
  const c = e && e.code;
  if (c === "not_in_manifest" || c === "approval_required" || c === "consent_required" || c === "not_granted") return "Permite que la página use tu Drive cuando te lo pida y vuelve a pulsar el botón.";
  if (c === "server_not_connected" || c === "selection_required") return "Google Drive no está conectado en tu cuenta de Claude (Ajustes → Conectores).";
  if (c === "needs_reauth") return "La conexión con Google Drive ha caducado. Vuelve a conectarla en Ajustes → Conectores.";
  return "Drive no ha aceptado el archivo: " + (c ? "[" + c + "] " : "") + String((e && e.message) || "").slice(0, 200);
}
function aBlob(b64, tipo){ const bin = atob(b64); const u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i); return new Blob([u], {type: tipo}); }
const TIPOS = {pdf: "application/pdf", csv: "text/csv", zip: "application/zip", xlsx: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", txt: "text/plain"};
let mcp = null;
(async () => { try { mcp = await window.claude?.use("mcp"); } catch (e) { mcp = null; } if (!mcp){ $("#estado").textContent = "Abre esta página desde claude.ai con tu cuenta para poder subir los archivos."; $("#subir").disabled = true; } })();
$("#subir").onclick = async () => {
  if (!mcp) return; const b = $("#subir"); b.disabled = true; $("#lista").textContent = ""; $("#estado").className = "";
  let lt = null; try { lt = await mcp.listTools(); } catch (e) { lt = null; }
  let hechos = 0; const nombres = Object.keys(DATOS);
  for (const n of nombres){
    const li = document.createElement("li"); li.textContent = n + " …"; $("#lista").append(li);
    const tipo = TIPOS[n.split(".").pop().toLowerCase()] || "application/octet-stream";
    const base = {title: n, parentId: DESTINO, contentMimeType: tipo, disableConversionToGoogleType: true};
    try {
      if (lt && lt.fileArgs){
        try { await mcp.callTool("Google Drive", "create_file", Object.assign({}, base, {base64Content: {$file: {data: aBlob(DATOS[n], tipo), name: n, type: tipo}}})); }
        catch (e){ if (e && e.code === "bad_request") await mcp.callTool("Google Drive", "create_file", Object.assign({}, base, {base64Content: DATOS[n]})); else throw e; }
      } else await mcp.callTool("Google Drive", "create_file", Object.assign({}, base, {base64Content: DATOS[n]}));
      li.textContent = n + " ✓"; li.className = "ok"; hechos++;
    } catch (e){ li.textContent = n + " — " + msg(e); li.className = "mal"; if (e && ["not_granted", "approval_required", "needs_reauth", "server_not_connected"].includes(e.code)) break; }
    $("#estado").textContent = "Subidos " + hechos + " de " + nombres.length + "…";
  }
  $("#estado").className = hechos === nombres.length ? "ok" : "mal";
  $("#estado").textContent = hechos === nombres.length ? "Listo: los " + hechos + " archivos están en Drive." : "Se han subido " + hechos + " de " + nombres.length + ". Avisa a Claude para revisar cuáles faltan.";
  $("#enlace").textContent = ""; const a = document.createElement("a"); a.href = ENLACE; a.target = "_blank"; a.rel = "noopener"; a.textContent = "Abrir la carpeta en Drive"; $("#enlace").append(a);
  b.disabled = false;
};
</script>
'''.replace('__TITULO__', titulo).replace('__DESTINO__', destino).replace('__DATOS__', json.dumps(datos))
os.makedirs(os.path.dirname(os.path.abspath(salida)), exist_ok=True); open(salida, 'w').write(html)
print(len(datos), 'archivos,', len(html) // 1024, 'KB ->', salida)
