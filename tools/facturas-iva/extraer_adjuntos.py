#!/usr/bin/env python3
"""Saca los adjuntos de un correo guardado en formato RAW por la herramienta de Gmail (get_message con RAW).

Uso:  python3 extraer_adjuntos.py ARCHIVO_JSON_DEL_RESULTADO CARPETA_SALIDA
El archivo JSON es el que guarda la herramienta cuando el resultado es muy grande (campo "raw").
"""
import sys, json, base64, os, email
from email import policy
d = json.load(open(sys.argv[1])); os.makedirs(sys.argv[2], exist_ok=True)
raw = d['raw']; raw += '=' * (-len(raw) % 4)
m = email.message_from_bytes(base64.urlsafe_b64decode(raw), policy=policy.default); n = 0
for p in m.walk():
    fn = p.get_filename()
    if fn:
        open(os.path.join(sys.argv[2], fn), 'wb').write(p.get_payload(decode=True)); n += 1
print(n, 'adjuntos guardados en', sys.argv[2])
