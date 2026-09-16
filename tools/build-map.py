#!/usr/bin/env python3
"""Projects a world map to a plain SVG at BUILD TIME, so the page ships no d3,
no topojson and no CDN call. Output (assets/world.svg) is committed.
Re-run only to change the projection or the source:  python3 tools/build-map.py
Source: world-atlas countries-110m (Natural Earth, public domain).
"""
import json, math, pathlib, urllib.request

SRC = 'https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-110m.json'
W, H = 960, 470

def natural_earth(lon, lat):
    """d3.geoNaturalEarth1 raw projection."""
    l, p = math.radians(lon), math.radians(lat)
    l2 = p * p; l4 = l2 * l2
    x = l * (0.8707 - 0.131979 * l2 + l4 * (-0.013791 + l4 * (0.003971 * l2 - 0.001529 * l4)))
    y = p * (1.007226 + l2 * (0.015085 + l4 * (-0.044475 + 0.028874 * l2 - 0.005916 * l4)))
    return x, y

def decode_arcs(topo):
    scale, translate = topo['transform']['scale'], topo['transform']['translate']
    out = []
    for arc in topo['arcs']:
        x = y = 0; pts = []
        for dx, dy in arc:
            x += dx; y += dy
            pts.append((x * scale[0] + translate[0], y * scale[1] + translate[1]))
        out.append(pts)
    return out

def ring(arcs, idxs):
    pts = []
    for i in idxs:
        a = arcs[~i][::-1] if i < 0 else arcs[i]
        pts.extend(a[1:] if pts else a)
    return pts

print('fetching', SRC)
topo = json.loads(urllib.request.urlopen(SRC, timeout=60).read())
arcs = decode_arcs(topo)
feats = topo['objects']['countries']['geometries']

# Project everything once to find the extent, then fit to the viewBox.
projected = []
for f in feats:
    polys = f['arcs'] if f['type'] == 'MultiPolygon' else [f['arcs']]
    rings = [[natural_earth(*pt) for pt in ring(arcs, r)] for poly in polys for r in poly]
    projected.append((f.get('id', ''), f.get('properties', {}).get('name', ''), rings))

xs = [p[0] for _, _, rs in projected for r in rs for p in r]
ys = [p[1] for _, _, rs in projected for r in rs for p in r]
sx = W / (max(xs) - min(xs)); sy = H / (max(ys) - min(ys)); s = min(sx, sy)
ox = (W - (max(xs) - min(xs)) * s) / 2 - min(xs) * s
oy = (H - (max(ys) - min(ys)) * s) / 2 + max(ys) * s

def d_for(rings):
    parts = []
    for r in rings:
        if len(r) < 3: continue
        # drop consecutive duplicate points created by rounding
        pts = [f'{round(x*s+ox)},{round(oy-y*s)}' for x, y in r]
        ded = [q for i, q in enumerate(pts) if i == 0 or q != pts[i-1]]
        if len(ded) < 3: continue
        # A ring that crosses the antimeridian comes back projected as a line
        # straight across the map. Split wherever x jumps more than half the
        # width and emit each run as its own subpath.
        runs, cur = [], [ded[0]]
        for a, b in zip(ded, ded[1:]):
            if abs(float(b.split(',')[0]) - float(a.split(',')[0])) > W * 0.5:
                runs.append(cur); cur = [b]
            else:
                cur.append(b)
        runs.append(cur)
        for run in runs:
            if len(run) >= 3:
                parts.append('M' + 'L'.join(run) + 'Z')
    return ''.join(parts)

paths = []
for cid, name, rings in projected:
    d = d_for(rings)
    if not d: continue
    paths.append(f'<path data-c="{cid}" d="{d}"/>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'role="img" aria-label="World map. Countries dim as each answer narrows where you can work.">'
       f'<g fill="#9a929a" stroke="#0e0b10" stroke-width="0.6">'
       + ''.join(paths) + '</g></svg>')
pathlib.Path('assets/world.svg').write_text(svg, encoding='utf-8')
print(f'assets/world.svg · {len(svg):,} bytes · {len(paths)} countries')
