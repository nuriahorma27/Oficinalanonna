#!/usr/bin/env python3
"""Pone el desglose de IVA (subtotal, envío, descuento, base imponible, IVA y total) en las facturas
de WooCommerce (plugin PDF Invoices) que solo traen Subtotal, Envío y Total.

Uso:  python3 desglosar_iva.py CARPETA_PDFS CARPETA_SALIDA [--iva 21] [--numero-inicial 25001]

- Con --numero-inicial N, además numera las facturas: N, N+1, N+2... en el orden en que aparecen (los PDF se leen por orden
  de nombre, de enero a diciembre) y escribe "Factura nº N" en la cabecera de la primera página de cada factura.

- El IVA va INCLUIDO en el total: IVA = total * iva / (100 + iva), neto = total - IVA (redondeado a 2 decimales).
- Si subtotal + envío no coincide con el total, añade una línea "Descuento" con la diferencia.
- Quita el cuadro de totales original (también el texto, para que no quede duplicado) y dibuja el nuevo.
- Escribe también resumen-facturas.csv (una fila por factura) y comprueba que neto + IVA = total en todas.
Necesita: pip install pdfplumber pypdf reportlab
"""
import sys, io, os, glob, csv, argparse
import pdfplumber
from pypdf import PdfReader, PdfWriter
from pypdf.generic import ContentStream
from reportlab.pdfgen import canvas

W, H = 595.28, 841.89
XL, XR = 345.8, 538.6   # bordes de la tabla de totales de la factura original
XTXT_L, XTXT_R = 349.2, 535.2

def num(s): return float(s.replace('.', '').replace(',', '.').replace('€', '').strip())
def eur(x, neg=False):
    s = f"{abs(x):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    return ('-' if neg and x else '') + s + '€'

def quita_texto_original(pg, reader, lo, hi):
    cs = ContentStream(pg.get_contents(), reader)
    out, i, quitados = [], 0, 0
    ops = cs.operations
    while i < len(ops):
        if ops[i][1] == b'BT':
            j = i
            while j < len(ops) and ops[j][1] != b'ET': j += 1
            bloque = ops[i:j + 1]; x = y = None
            for oo, pp in bloque:
                if pp == b'Td': x, y = float(oo[0]), float(oo[1])
            if x is not None and x >= 340 and lo <= y <= hi: quitados += 1
            else: out.extend(bloque)
            i = j + 1
        else:
            out.append(ops[i]); i += 1
    cs.operations = out
    pg.replace_contents(cs)
    return quitados

def procesa(src, dst, iva_pct, filas_resumen, contador=None):
    reader = PdfReader(src); writer = PdfWriter(); n = 0; actual = ''
    with pdfplumber.open(src) as pl:
        for i, page in enumerate(pl.pages):
            words = page.extract_words()
            sub = [w for w in words if w['text'] == 'Subtotal' and w['x0'] > 300]
            inicio = any(w['text'] == 'BILLING' and w['top'] < 60 for w in words)
            pg = reader.pages[i]
            if inicio and contador is not None:
                actual = contador[0]; contador[0] += 1
            if not sub and not (inicio and contador is not None):
                writer.add_page(pg); continue
            buf = io.BytesIO(); c = canvas.Canvas(buf, pagesize=(W, H))
            if inicio and contador is not None:
                # número de factura en el hueco de la cabecera, debajo de "LA NONNA ATELIER" y encima de "Número de pedido"
                c.setFillColorRGB(0, 0, 0); c.setFont('Helvetica-Bold', 10.5)
                c.drawString(347.0, H - 232.0, f'Factura nº {actual}')
            if sub:
                s = sub[0]; y0 = s['top']
                def fila(lab):
                    l = [w for w in words if w['text'] == lab and w['x0'] > 300 and w['top'] >= y0 - 1]
                    if not l: return None
                    l = l[0]
                    val = [w for w in words if abs(w['top'] - l['top']) < 3 and w['x0'] > l['x1'] + 20 and '€' in w['text']]
                    return l, num(val[-1]['text'])
                fe, ft = fila('Envío'), fila('Total')
                sv = num([w for w in words if abs(w['top'] - s['top']) < 3 and '€' in w['text']][-1]['text'])
                env, tot = fe[1], ft[1]; ybot = ft[0]['bottom']
                iva = round(tot * iva_pct / (100 + iva_pct), 2); neto = round(tot - iva, 2)
                desc = round(tot - (sv + env), 2)
                filas = [('Subtotal', eur(sv)), ('Envío', eur(env))]
                if abs(desc) > 0.004: filas.append(('Descuento', eur(desc, True)))
                filas += [('Base imponible (neto)', eur(neto)), (f'IVA {iva_pct:g} %', eur(iva)), ('Total (IVA incluido)', eur(tot))]
                filas_resumen.append((os.path.basename(src), i + 1, actual, sv, env, desc, neto, iva, tot))
                q = quita_texto_original(pg, reader, H - (ybot + 11), H - (y0 - 12))
                assert q >= 6, (src, i, q)
                c.setFillColorRGB(1, 1, 1)
                c.rect(XL - 6, H - (ybot + 11), (XR - XL) + 12, (ybot + 11) - (y0 - 12), fill=1, stroke=0)
                y, rh, nf = y0 - 8.2, 21.0, len(filas)
                if y + nf * rh > H - 30: rh = max(15, (H - 30 - y) / nf)
                def linea(yy, gris=True, grosor=.6):
                    (c.setStrokeColorRGB(.87, .87, .87) if gris else c.setStrokeColorRGB(0, 0, 0))
                    c.setLineWidth(grosor); c.line(XL, H - yy, XR, H - yy)
                linea(y)
                for k, (lab, val) in enumerate(filas):
                    ult = k == nf - 1
                    ty = H - (y + k * rh + rh / 2 + 3.0)
                    c.setFillColorRGB(0, 0, 0)
                    c.setFont('Helvetica-Bold' if (ult or lab in ('Subtotal', 'Envío')) else 'Helvetica', 8.6)
                    c.drawString(XTXT_L, ty, lab)
                    c.setFont('Helvetica-Bold' if ult else 'Helvetica', 8.6)
                    c.drawRightString(XTXT_R, ty, val)
                    linea(y + (k + 1) * rh, gris=not ult, grosor=1.0 if ult else .6)
            c.save(); buf.seek(0)
            pg.merge_page(PdfReader(buf).pages[0]); writer.add_page(pg); n += 1
    with open(dst, 'wb') as f: writer.write(f)
    return n

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('entrada'); ap.add_argument('salida'); ap.add_argument('--iva', type=float, default=21.0); ap.add_argument('--numero-inicial', type=int, default=None)
    a = ap.parse_args(); os.makedirs(a.salida, exist_ok=True); resumen = []; contador = [a.numero_inicial] if a.numero_inicial is not None else None
    for src in sorted(glob.glob(os.path.join(a.entrada, '*.pdf'))):
        base = os.path.splitext(os.path.basename(src))[0]
        n = procesa(src, os.path.join(a.salida, base + '-con-IVA.pdf'), a.iva, resumen, contador)
        print(f'{base}: {n} facturas')
    mal = [r for r in resumen if abs(r[6] + r[7] - r[8]) > 0.005]
    with open(os.path.join(a.salida, 'resumen-facturas.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f, delimiter=';'); w.writerow(['archivo', 'pagina', 'numero de factura', 'subtotal', 'envio', 'descuento', 'base imponible (neto)', f'IVA {a.iva:g}%', 'total'])
        for r in resumen: w.writerow(list(r[:3]) + [f"{x:.2f}".replace('.', ',') for x in r[3:]])
    print((f'Numeradas de {resumen[0][2]} a {resumen[-1][2]}' if contador is not None and resumen else 'Sin numerar'))
    print(f'TOTAL {len(resumen)} facturas | neto {sum(r[6] for r in resumen):.2f} | IVA {sum(r[7] for r in resumen):.2f} | total {sum(r[8] for r in resumen):.2f} | con descuento {sum(1 for r in resumen if abs(r[5]) > 0.004)} | sumas que no cuadran {len(mal)}')

if __name__ == '__main__': main()
