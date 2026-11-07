#!/usr/bin/env python3
"""Build the communication link diagrams for the wiki.

Reads the icons in media/ and writes self-contained SVGs to
docs/Multirotor/Flight_Stack/diagrams/. Run from anywhere:

    python3 media/build_comm_diagrams.py

The diagrams stay general (no topic names, ports or commands) because the
codebase is still changing. Optional parts carry the cd-optional class, which
docs/javascripts/comm-diagram.js toggles. Colours are CSS variables so the page
can theme them; the fallbacks below are the light theme, used when the SVG is
viewed on its own.
"""

import re
from html import escape
from pathlib import Path

MEDIA = Path(__file__).resolve().parent
OUT = MEDIA.parent / 'docs' / 'Multirotor' / 'Flight_Stack' / 'diagrams'

LINK_KINDS = {
    'rc': ('#d9480f', 'ELRS radio control'),
    'rfd': ('#7048e8', 'RFD900x telemetry radio'),
    'net': ('#1971c2', 'IP network (4G, tailnet, localhost)'),
    'wire': ('#5c6670', 'On-board wiring (USB, UART)'),
    'video': ('#c2255c', 'Video'),
    'ros': ('#2f9e44', 'ROS 2 / DDS'),
    'gz': ('#0c8599', 'Gazebo transport'),
}

STYLE = """
.cdg{font-family:var(--cd-font,Roboto,"Helvetica Neue",Arial,sans-serif)}
.cdg .bg{fill:var(--cd-bg,#fff)}
.cdg text{fill:var(--cd-ink,#20252b)}
.cdg .t-title{font-size:20px;font-weight:700}
.cdg .t-subtitle{font-size:12.5px;fill:var(--cd-muted,#5b6573)}
.cdg .t-lbl{font-size:13px;font-weight:600}
.cdg .t-sub{font-size:11px;fill:var(--cd-muted,#5b6573)}
.cdg .t-tag{font-size:9.5px;font-style:italic;fill:var(--cd-muted,#5b6573)}
.cdg .t-group{font-size:13px;font-weight:700;letter-spacing:.02em}
.cdg .t-region{font-size:15px;font-weight:700;letter-spacing:.06em;fill:var(--cd-muted,#5b6573)}
.cdg .t-credit{font-size:10px;fill:var(--cd-muted,#5b6573)}
.cdg .cd-region>rect{fill:var(--cd-region,#f3f5f8);stroke:var(--cd-region-line,#d5dbe3);stroke-width:1.2}
.cdg .cd-group>rect{fill:var(--cd-group,#fff);stroke:var(--cd-group-line,#9aa4b1);stroke-width:1.2}
.cdg .cd-group.g-ros>rect{fill:var(--cd-ros-bg,#f1faf3);stroke:var(--cd-ros,#2f9e44)}
.cdg .cd-node>rect.box{fill:var(--cd-paper,#fff);stroke:var(--cd-ink,#20252b);stroke-width:1.4}
.cdg .cd-node.cd-optional>rect.box{stroke-dasharray:5 4}
.cdg .cd-node.k-data>rect.box{fill:var(--cd-ros-bg,#f1faf3);stroke:var(--cd-ros,#2f9e44)}
.cdg .mi{fill:var(--cd-ink,#20252b)}
.cdg .icon [stroke="#20252b"]{stroke:var(--cd-ink,#20252b)}
.cdg .icon [fill="white"]{fill:var(--cd-paper,#fff)}
.cdg .cd-link path.ln{fill:none;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}
.cdg .cd-link.cd-optional path.ln{stroke-dasharray:7 5}
.cdg .cd-llabel{font-size:11px;font-weight:600;paint-order:stroke;stroke:var(--cd-bg,#fff);stroke-width:4px;stroke-linejoin:round}
.cdg .legend .t-sub{font-size:11.5px}
""" + ''.join(
    f'.cdg .l-{k} path.ln{{stroke:var(--cd-{k},{c})}}'
    f'.cdg .l-{k} .cd-llabel{{fill:var(--cd-{k},{c})}}'
    f'.cdg .mk-{k}{{fill:var(--cd-{k},{c})}}\n'
    for k, (c, _) in LINK_KINDS.items()
)


def fmt(v):
    return f'{v:.2f}'.rstrip('0').rstrip('.')


# Icons -----------------------------------------------------------------------

# Diagram role -> Material Symbols icon in media/icons/ (see media/icons/README.md).
ICONS = {
    'flight_controller': 'memory',
    'jetson': 'developer_board',
    'rc_transmitter': 'sports_esports',
    'laptop': 'laptop_windows',
    'radio_modem': 'router',
    'modem_4g': 'cell_tower',
    'tailnet': 'vpn_lock',
    'fpv_camera': 'videocam',
    'fpv_monitor': 'connected_tv',
    'capture_card': 'settings_input_hdmi',
    'depth_camera': 'photo_camera',
    'elrs_receiver': 'settings_input_antenna',
    'sim_pc': 'desktop_windows',
    'gazebo': 'view_in_ar',
    'px4_sitl': 'terminal',
    'browser': 'web',
    'ros_graph': 'hub',
}
CREDIT = 'Icons: Material Symbols by Google, Apache License 2.0'

_icon_cache = {}


def load_icon(name):
    if name not in _icon_cache:
        path = MEDIA / 'drone.svg' if name == 'drone' else MEDIA / 'icons' / f'{ICONS[name]}.svg'
        src = path.read_text()
        vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', src).group(1).split()]
        inner = re.sub(r'^.*?<svg[^>]*>', '', src, count=1, flags=re.S)
        inner = re.sub(r'</svg>\s*$', '', inner)
        inner = re.sub(r'<(title|desc)>.*?</\1>', '', inner, flags=re.S)
        inner = re.sub(r'<!--.*?-->', '', inner, flags=re.S)
        inner = re.sub(r'\s*\n\s*', '', inner)
        _icon_cache[name] = (vb, inner)
    return _icon_cache[name]


def icon(name, x, y, w, h, stroke_px=1.6):
    vb, inner = load_icon(name)
    box = f'x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" viewBox="{" ".join(fmt(v) for v in vb)}"'
    if name != 'drone':
        # Material Symbols are filled paths; the .mi rule colours them.
        return f'<svg class="icon mi" {box} aria-hidden="true">{inner}</svg>'
    # drone.svg is line art with a 3.2 main stroke; keep it at stroke_px on screen.
    k = stroke_px / 3.2 / min(w / vb[2], h / vb[3])
    body = re.sub(r'stroke-width="([\d.]+)"', lambda m: f'stroke-width="{fmt(float(m.group(1)) * k)}"', inner)
    return f'<svg class="icon" {box} overflow="visible" aria-hidden="true">{body}</svg>'


# Diagram model -----------------------------------------------------------------


class Box:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h

    @property
    def cx(self):
        return self.x + self.w / 2

    @property
    def cy(self):
        return self.y + self.h / 2

    def l(self, dy=0):
        return (self.x, self.cy + dy)

    def r(self, dy=0):
        return (self.x + self.w, self.cy + dy)

    def t(self, dx=0):
        return (self.cx + dx, self.y)

    def b(self, dx=0):
        return (self.cx + dx, self.y + self.h)


def text_el(x, y, s, cls, anchor='start'):
    return f'<text x="{fmt(x)}" y="{fmt(y)}" class="{cls}" text-anchor="{anchor}">{escape(s)}</text>'


def rounded_path(pts, r=8):
    if len(pts) == 2:
        (x0, y0), (x1, y1) = pts
        return f'M {fmt(x0)},{fmt(y0)} L {fmt(x1)},{fmt(y1)}'
    d = [f'M {fmt(pts[0][0])},{fmt(pts[0][1])}']
    for i in range(1, len(pts) - 1):
        (xa, ya), (xb, yb), (xc, yc) = pts[i - 1], pts[i], pts[i + 1]
        la = max(abs(xb - xa), abs(yb - ya))
        lc = max(abs(xc - xb), abs(yc - yb))
        rr = min(r, la / 2, lc / 2)

        def towards(px, py, qx, qy, dist, length):
            return (qx + (px - qx) * dist / length, qy + (py - qy) * dist / length) if length else (qx, qy)

        p1 = towards(xa, ya, xb, yb, rr, la)
        p2 = towards(xc, yc, xb, yb, rr, lc)
        d.append(f'L {fmt(p1[0])},{fmt(p1[1])} Q {fmt(xb)},{fmt(yb)} {fmt(p2[0])},{fmt(p2[1])}')
    d.append(f'L {fmt(pts[-1][0])},{fmt(pts[-1][1])}')
    return ' '.join(d)


class Diagram:
    def __init__(self, key, w, h, title, subtitle):
        self.key, self.w, self.h = key, w, h
        self.title, self.subtitle = title, subtitle
        self.back, self.links, self.nodes = [], [], []
        self.n = {}
        self.kinds = set()
        self.has_optional = False

    # Regions are the large air/ground/host backgrounds; groups are hosts.
    def region(self, x, y, w, h, title):
        self.back.append(
            f'<g class="cd-region"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18"/>'
            + text_el(x + 18, y + 26, title.upper(), 't-region')
            + '</g>'
        )

    def group(self, x, y, w, h, title, sub=None, kind='', icon_name=None):
        cls = 'cd-group' + (f' g-{kind}' if kind else '')
        tx = x + 14
        parts = [f'<g class="{cls}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12"/>']
        if icon_name:
            parts.append(icon(icon_name, x + 10, y + 7, 24, 24))
            tx = x + 40
        parts.append(text_el(tx, y + 24, title, 't-group'))
        if sub:
            parts.append(text_el(x + w - 14, y + 24, sub, 't-sub', 'end'))
        parts.append('</g>')
        self.back.append(''.join(parts))

    def deco(self, name, x, y, w, h):
        self.back.append(icon(name, x, y, w, h, 1.4))

    def node(self, id, x, y, w, h, label, sub=(), icon_name=None, layout='h',
             isz=40, optional=False, kind='device'):
        """A box with a bold label and muted sub-lines; id is only for placing links."""
        b = Box(x, y, w, h)
        self.n[id] = b
        self.has_optional |= optional
        lines = [(label, 't-lbl', 13)] + [(s, 't-sub', 11) for s in ([sub] if isinstance(sub, str) else sub)]
        cls = f'cd-node k-{kind}' + (' cd-optional' if optional else '')
        rx = min(h / 2, 16) if kind == 'data' else 8
        out = [
            f'<g class="{cls}">',
            f'<rect class="box" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/>',
        ]
        gap = 3
        block = sum(sz + gap for _, _, sz in lines) - gap
        if icon_name and layout == 'v':
            out.append(icon(icon_name, x + (w - isz) / 2, y + 10, isz, isz))
            ty, tx, anchor = y + 10 + isz + 8, x + w / 2, 'middle'
            ty += (y + h - 8 - ty - block) / 2
        elif icon_name:
            out.append(icon(icon_name, x + 10, y + (h - isz) / 2, isz, isz))
            ty, tx, anchor = y + (h - block) / 2, x + isz + 20, 'start'
        else:
            anchor = 'middle' if kind == 'data' else 'start'
            tx = x + w / 2 if anchor == 'middle' else x + 12
            ty = y + (h - block) / 2
        for s, c, sz in lines:
            out.append(text_el(tx, ty + sz * 0.8, s, c, anchor))
            ty += sz + gap
        if optional:
            out.append(text_el(x + w - 7, y + 11, 'optional', 't-tag', 'end'))
        out.append('</g>')
        self.nodes.append(''.join(out))
        return b

    def link(self, kind, pts, label=None, lpos=None, anchor='middle',
             optional=False, ends='both', ldy=-6):
        """pts: list of points; the label goes at lpos, or above the middle of the longest segment."""
        self.kinds.add(kind)
        self.has_optional |= optional
        cls = f'cd-link l-{kind}' + (' cd-optional' if optional else '')
        d = rounded_path(pts)
        m_start = f' marker-start="url(#{self.key}-ah-{kind})"' if ends == 'both' else ''
        m_end = f' marker-end="url(#{self.key}-ah-{kind})"' if ends in ('both', 'end') else ''
        out = [
            f'<g class="{cls}">',
            f'<path class="ln" d="{d}"{m_start}{m_end}/>',
        ]
        if label:
            if lpos is None:
                segs = list(zip(pts, pts[1:]))
                (xa, ya), (xb, yb) = max(segs, key=lambda s: abs(s[1][0] - s[0][0]) + abs(s[1][1] - s[0][1]))
                lpos = ((xa + xb) / 2, (ya + yb) / 2 + ldy)
            out.append(text_el(lpos[0], lpos[1], label, 'cd-llabel', anchor))
        out.append('</g>')
        self.links.append(''.join(out))

    def legend(self, x, y):
        parts = ['<g class="legend">', text_el(x, y, 'LINKS', 't-tag')]
        cx = x + 46
        for k in [k for k in LINK_KINDS if k in self.kinds]:
            parts.append(f'<g class="l-{k}"><path class="ln" d="M {cx},{y - 4} h 28" style="fill:none;stroke-width:2.6"/></g>')
            parts.append(text_el(cx + 34, y, LINK_KINDS[k][1], 't-sub'))
            cx += 34 + len(LINK_KINDS[k][1]) * 5.7 + 22
        if self.has_optional:
            parts.append(f'<path d="M {cx},{y - 4} h 28" style="fill:none;stroke:var(--cd-muted,#5b6573);stroke-width:2.2;stroke-dasharray:7 5"/>')
            parts.append(text_el(cx + 34, y, 'Optional link or component (dashed)', 't-sub'))
        parts.append('</g>')
        self.nodes.append(''.join(parts))

    def render(self):
        markers = ''.join(
            f'<marker id="{self.key}-ah-{k}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6" '
            f'markerHeight="6" orient="auto-start-reverse" markerUnits="userSpaceOnUse">'
            f'<path class="mk-{k}" d="M 0,0.8 L 9.5,5 L 0,9.2 Z" transform="scale(1.25) translate(-1.5,-1)"/></marker>'
            for k in sorted(self.kinds)
        )
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" class="cdg" data-diagram="{self.key}" '
            f'width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}" role="img" '
            f'aria-labelledby="{self.key}-title">\n'
            f'<title id="{self.key}-title">{escape(self.title)}</title>\n'
            f'<!-- {CREDIT} (https://github.com/google/material-design-icons). -->\n'
            f'<style>{STYLE}</style>\n<defs>{markers}</defs>\n'
            f'<rect class="bg" width="{self.w}" height="{self.h}"/>\n'
            + text_el(24, 40, self.title, 't-title') + '\n'
            + text_el(24, 60, self.subtitle, 't-subtitle') + '\n'
            + text_el(self.w - 24, 40, CREDIT, 't-credit', 'end') + '\n'
            + '\n'.join(self.back) + '\n'
            + '<g class="links">\n' + '\n'.join(self.links) + '\n</g>\n'
            + '<g class="nodes">\n' + '\n'.join(self.nodes) + '\n</g>\n</svg>\n'
        )




# Layer 1: system -----------------------------------------------------------------


def layer1():
    g = Diagram('l1', 1280, 760, 'Layer 1 · Hardware Devices', 'Links between top level hardware components')
    g.region(20, 64, 560, 626, 'UAV')
    g.region(800, 64, 460, 626, 'Ground')
    g.deco('drone', 40, 112, 166, 148)

    nv = dict(w=150, h=96, layout='v', isz=52)
    g.node('elrs_rx', 410, 102, label='ELRS receiver', sub='2.4 GHz', icon_name='elrs_receiver', **nv)
    g.node('fc', 225, 252, label='Flight controller', sub='CubeOrange+ · PX4', icon_name='flight_controller', **nv)
    g.node('rfd_air', 410, 252, label='RFD900x (air)', sub='915 MHz telemetry', icon_name='radio_modem', optional=True, **nv)
    g.node('jetson', 225, 402, label='Jetson Orin Nano', sub='companion computer', icon_name='jetson', **nv)
    g.node('modem', 410, 402, label='4G modem', sub='USB LTE', icon_name='modem_4g', **nv)
    g.node('depth', 40, 402, label='Depth camera', sub='aux sensor · USB', icon_name='depth_camera', optional=True, **nv)
    g.node('fpv_cam', 410, 552, label='FPV camera + VTX', sub='5.8 GHz analog', icon_name='fpv_camera', optional=True, **nv)
    g.node('tailnet', 615, 402, 150, 96, label='Tailnet', sub='Tailscale · internet', layout='v', isz=48, icon_name='tailnet')
    g.node('rc_tx', 825, 102, label='RC transmitter', sub='safety pilot', icon_name='rc_transmitter', **nv)
    g.node('rfd_gnd', 825, 252, label='RFD900x (ground)', sub='USB serial', icon_name='radio_modem', optional=True, **nv)
    g.node('gcs', 1010, 252, 230, 246, label='GCS laptop', sub=['QGroundControl', 'Flight visualizer', 'Tailscale', 'FPV video viewer (optional)'],
           layout='v', isz=72, icon_name='laptop')
    g.node('fpv_mon', 825, 552, label='FPV monitor', sub='5.8 GHz receiver', icon_name='fpv_monitor', optional=True, **nv)
    g.node('capture', 1050, 552, label='Capture card', sub='HDMI → USB', icon_name='capture_card', optional=True, **nv)

    n = g.n
    g.link('rc', [n['elrs_rx'].r(), n['rc_tx'].l()], 'ELRS 2.4 GHz · RC control')
    g.link('wire', [n['fc'].t(), (n['fc'].cx, n['elrs_rx'].cy), n['elrs_rx'].l()], 'CRSF', lpos=(n['fc'].cx + 8, 210), anchor='start')
    g.link('rfd', [n['rfd_air'].r(), n['rfd_gnd'].l()], 'RFD900x 915 MHz · MAVLink', optional=True)
    g.link('wire', [n['fc'].r(), n['rfd_air'].l()], optional=True)
    g.link('wire', [n['rfd_gnd'].r(), (n['gcs'].x, n['rfd_gnd'].cy)], optional=True)
    g.link('wire', [n['fc'].b(-22), n['jetson'].t(-22)], 'USB · MAVLink', lpos=(n['fc'].cx - 30, 380), anchor='end')
    g.link('wire', [n['fc'].b(22), n['jetson'].t(22)], 'UART · uXRCE-DDS', lpos=(n['fc'].cx + 30, 380), anchor='start')
    g.link('wire', [n['jetson'].r(), n['modem'].l()])
    g.link('net', [n['modem'].r(), n['tailnet'].l()], 'LTE')
    g.link('net', [n['tailnet'].r(), (n['gcs'].x, n['tailnet'].cy)], 'Tailnet · WireGuard')
    g.link('wire', [n['depth'].r(), n['jetson'].l()], optional=True, ends='end')
    g.link('video', [n['fpv_cam'].r(), n['fpv_mon'].l()], '5.8 GHz analog video', optional=True, ends='end')
    g.link('video', [n['fpv_mon'].r(), n['capture'].l()], 'AV/HDMI', optional=True, ends='end')
    g.link('video', [n['capture'].t(), (n['capture'].cx, n['gcs'].y + n['gcs'].h)], 'USB', lpos=(n['capture'].cx + 8, 529), anchor='start', optional=True, ends='end')
    g.legend(24, 728)
    return g


# Layer 2: software modules -----------------------------------------------------------


def layer2():
    g = Diagram('l2', 1880, 900, 'Layer 2 · Software', 'Software modules runinng on each component')
    g.region(20, 74, 1100, 680, 'UAV')
    g.region(1350, 74, 510, 790, 'Ground')

    pn = dict(w=150, h=64, isz=34)
    g.node('depth', 40, 158, label='Depth camera', sub='USB', icon_name='depth_camera', optional=True, **pn)

    g.group(215, 92, 450, 548, 'Jetson Orin Nano', 'companion computer', icon_name='jetson')
    g.group(235, 126, 230, 394, 'ROS 2', kind='ros', icon_name='ros_graph')
    rn = dict(w=200, h=54, kind='proc')
    g.node('cam_drv', 250, 163, label='Camera driver', sub='image topics', optional=True, **rn)
    g.node('mission', 250, 253, label='Mission scripts', sub='flight core client', **rn)
    g.node('core', 250, 343, label='Flight core', sub='offboard control', **rn)
    g.node('bridge', 250, 433, label='Visualizer bridge', sub='flight core client', **rn)

    jn = dict(w=150, h=54, kind='proc')
    g.node('agent', 500, 343, label='MicroXRCEAgent', sub='DDS ⇄ ROS 2', **jn)
    g.node('router', 500, 433, label='MAVLink router', sub='serial → network', **jn)
    g.node('j_ts', 500, 553, label='Tailscale', sub='tailnet node', **jn)

    g.group(705, 92, 210, 428, 'Flight controller', 'PX4', icon_name='flight_controller')
    fn = dict(w=180, h=54, kind='proc')
    g.node('px_rc', 720, 163, label='RC input', sub='CRSF', **fn)
    g.node('px_mav1', 720, 253, label='MAVLink', sub='telemetry radio', optional=True, **fn)
    g.node('px_dds', 720, 343, label='uXRCE-DDS client', sub='uORB ⇄ DDS', **fn)
    g.node('px_mav', 720, 433, label='MAVLink', sub='USB', **fn)

    g.node('elrs_rx', 950, 158, label='ELRS RX', sub='2.4 GHz', icon_name='elrs_receiver', **pn)
    g.node('rfd_air', 950, 248, label='RFD900x air', sub='915 MHz', icon_name='radio_modem', optional=True, **pn)
    g.node('modem', 950, 548, label='4G modem', sub='USB LTE', icon_name='modem_4g', **pn)
    g.node('fpv_cam', 950, 658, label='FPV cam/VTX', sub='5.8 GHz', icon_name='fpv_camera', optional=True, **pn)

    g.node('tailnet', 1160, 548, label='Tailnet', sub='Tailscale', icon_name='tailnet', **pn)

    g.node('rc_tx', 1370, 158, label='RC TX', sub='ELRS', icon_name='rc_transmitter', **pn)
    g.node('rfd_gnd', 1370, 248, label='RFD900x gnd', sub='USB serial', icon_name='radio_modem', optional=True, **pn)
    g.node('fpv_mon', 1370, 658, label='FPV monitor', sub='5.8 GHz', icon_name='fpv_monitor', optional=True, **pn)
    g.node('capture', 1370, 768, label='Capture card', sub='HDMI → USB', icon_name='capture_card', optional=True, **pn)

    g.group(1550, 200, 290, 640, 'GCS laptop', icon_name='laptop')
    gn = dict(w=240, h=54, kind='proc')
    g.node('qgc', 1575, 253, label='QGroundControl', sub='MAVLink ground station', **gn)
    g.node('frontend', 1575, 343, label='Visualizer frontend', sub='web dashboard', **gn)
    g.node('backend', 1575, 433, label='Visualizer backend', sub='web server', **gn)
    g.node('g_ts', 1575, 553, label='Tailscale', sub='tailnet node', **gn)
    g.node('viewer', 1575, 773, label='Video viewer', sub='captured FPV feed', optional=True, **gn)

    n = g.n
    g.link('wire', [n['depth'].r(), n['cam_drv'].l()], optional=True, ends='end')
    g.link('ros', [n['cam_drv'].b(), n['mission'].t()], optional=True, ends='end')
    g.link('ros', [n['mission'].b(), n['core'].t()], 'control', lpos=(n['core'].cx + 8, 330), anchor='start')
    g.link('ros', [n['bridge'].t(), n['core'].b()], 'control', lpos=(n['core'].cx + 8, 420), anchor='start')
    bus = 482
    g.link('ros', [n['agent'].l(), n['core'].r()])
    g.link('ros', [n['agent'].l(-8), (bus, n['agent'].cy - 8), (bus, n['mission'].cy), n['mission'].r()], ends='end')
    g.link('ros', [n['agent'].l(8), (bus, n['agent'].cy + 8), (bus, n['bridge'].cy), n['bridge'].r()], ends='end')
    g.link('wire', [n['px_dds'].l(), n['agent'].r()], 'UART', lpos=(685, 364))
    g.link('wire', [n['px_mav'].l(), n['router'].r()], 'USB', lpos=(685, 454))
    g.link('net', [n['router'].b(), n['j_ts'].t()], 'MAVLink · UDP', lpos=(n['router'].cx + 8, 525), anchor='start')
    g.link('net', [n['bridge'].b(), (n['bridge'].cx, n['j_ts'].cy), n['j_ts'].l()], 'TCP', lpos=(n['bridge'].cx + 8, 560), anchor='start')
    g.link('wire', [n['px_rc'].r(), n['elrs_rx'].l()])
    g.link('wire', [n['px_mav1'].r(), n['rfd_air'].l()], optional=True)
    g.link('wire', [n['j_ts'].r(), n['modem'].l()], 'USB')
    g.link('rc', [n['elrs_rx'].r(), n['rc_tx'].l()], 'ELRS 2.4 GHz')
    g.link('rfd', [n['rfd_air'].r(), n['rfd_gnd'].l()], 'RFD900x · MAVLink', optional=True)
    g.link('net', [n['modem'].r(), n['tailnet'].l()], 'LTE')
    g.link('net', [n['tailnet'].r(), n['g_ts'].l()], 'WireGuard')
    g.link('video', [n['fpv_cam'].r(), n['fpv_mon'].l()], '5.8 GHz analog video', optional=True, ends='end')
    g.link('video', [n['fpv_mon'].b(), n['capture'].t()], 'AV/HDMI', lpos=(n['capture'].cx + 8, 750), anchor='start', optional=True, ends='end')
    g.link('video', [n['capture'].r(), n['viewer'].l()], 'USB', optional=True, ends='end')
    g.link('rfd', [n['rfd_gnd'].r(), n['qgc'].l()], 'serial', optional=True)
    g.link('net', [n['g_ts'].t(), n['backend'].b()], 'TCP', lpos=(n['backend'].cx + 8, 525), anchor='start')
    lane = 1828
    g.link('net', [n['g_ts'].r(), (lane, n['g_ts'].cy), (lane, n['qgc'].cy), n['qgc'].r()], 'MAVLink · UDP', lpos=(lane - 6, 338), anchor='end')
    g.link('net', [n['backend'].t(), n['frontend'].b()], 'WebSocket', lpos=(n['backend'].cx + 8, 420), anchor='start')
    g.legend(24, 880)
    return g


# Layer 3: programs, ROS 2 nodes and data flows -------------------------------------------


def layer3():
    g = Diagram('l3', 2420, 1160, 'Layer 3 · Programs & Nodes',
                'Individual programs and nodes')
    g.region(20, 74, 1590, 900, 'UAV')
    g.region(1845, 74, 555, 1030, 'Ground')

    pn = dict(w=150, h=64, isz=34)
    g.node('depth', 40, 168, label='Depth camera', sub='USB', icon_name='depth_camera', optional=True, **pn)

    g.group(205, 108, 900, 830, 'Jetson Orin Nano', 'companion computer', icon_name='jetson')
    g.group(225, 142, 680, 520, 'ROS 2 graph', kind='ros', icon_name='ros_graph')

    g.node('cam_drv', 265, 172, 210, 56, label='Camera driver node', sub='aux sensor', optional=True, kind='proc')
    g.node('t_cam', 505, 172, 380, 56, label='Camera images', sub='image and depth', optional=True, kind='data')
    g.node('t_out', 505, 262, 380, 70, label='Vehicle state', sub='PX4 → ROS 2', kind='data')
    g.node('mission', 265, 362, 210, 56, label='Mission script', sub='flight core client', kind='proc')
    g.node('t_if', 505, 437, 170, 70, label='Control interface', sub=['lease · commands', 'core state'], kind='data')
    g.node('core', 715, 437, 170, 70, label='Flight core node', sub='offboard control', kind='proc')
    g.node('bridge', 265, 552, 210, 66, label='Visualizer bridge node', sub='flight core client', kind='proc')
    g.node('t_in', 715, 562, 170, 76, label='Setpoints + commands', sub='ROS 2 → PX4', kind='data')

    g.node('agent', 935, 262, 150, 376, label='MicroXRCEAgent', sub='serial', kind='proc')
    g.node('router', 935, 690, 150, 84, label='MAVLink router', sub='serial → UDP', kind='proc')
    g.node('j_ts', 935, 820, 150, 70, label='Tailscale', sub='tailnet interface', kind='proc')

    g.group(1145, 142, 250, 666, 'Flight controller', 'PX4', icon_name='flight_controller')
    fn = dict(w=220, kind='proc')
    g.node('px_rc', 1160, 172, h=56, label='RC input', sub='CRSF', **fn)
    g.node('px_mav1', 1160, 266, h=56, label='MAVLink', sub='telemetry port', optional=True, **fn)
    g.node('px_dds', 1160, 410, h=80, label='uXRCE-DDS client', sub='telemetry port', **fn)
    g.node('px_uorb', 1160, 520, h=46, label='uORB', sub='internal message bus', **fn)
    g.node('px_mav', 1160, 704, h=56, label='MAVLink', sub='USB', **fn)

    g.node('elrs_rx', 1435, 168, label='ELRS RX', sub='CRSF', icon_name='elrs_receiver', **pn)
    g.node('rfd_air', 1435, 262, label='RFD900x air', sub='915 MHz', icon_name='radio_modem', optional=True, **pn)
    g.node('modem', 1435, 823, label='4G modem', sub='USB LTE', icon_name='modem_4g', **pn)
    g.node('fpv_cam', 1435, 905, label='FPV cam/VTX', sub='5.8 GHz', icon_name='fpv_camera', optional=True, **pn)

    g.node('tailnet', 1655, 823, label='Tailnet', sub='Tailscale', icon_name='tailnet', **pn)

    g.node('rc_tx', 1865, 168, label='RC TX', sub='ELRS', icon_name='rc_transmitter', **pn)
    g.node('rfd_gnd', 1865, 262, label='RFD900x gnd', sub='USB serial', icon_name='radio_modem', optional=True, **pn)
    g.node('fpv_mon', 1865, 905, label='FPV monitor', sub='5.8 GHz', icon_name='fpv_monitor', optional=True, **pn)
    g.node('capture', 1865, 1003, label='Capture card', sub='HDMI → USB', icon_name='capture_card', optional=True, **pn)

    g.group(2050, 200, 330, 890, 'GCS laptop', icon_name='laptop')
    gn = dict(w=280, kind='proc')
    g.node('qgc', 2075, 256, h=76, label='QGroundControl', sub=['MAVLink over UDP', 'serial to RFD900x (optional)'], **gn)
    g.node('browser', 2075, 404, h=70, label='Browser', sub='visualizer dashboard', icon_name='browser', **gn)
    g.node('vite', 2075, 520, h=70, label='Frontend dev server', sub='serves the dashboard', **gn)
    g.node('backend', 2075, 640, h=84, label='Visualizer backend', sub='relays state and commands', **gn)
    g.node('g_ts', 2075, 820, h=70, label='Tailscale', sub='tailnet interface', **gn)
    g.node('viewer', 2075, 1003, h=64, label='Video viewer', sub='captured FPV feed', optional=True, **gn)

    n = g.n
    g.link('wire', [n['depth'].r(), n['cam_drv'].l()], optional=True, ends='end')
    g.link('ros', [n['cam_drv'].r(), n['t_cam'].l()], optional=True, ends='end')
    lane_l = 245
    g.link('ros', [n['t_out'].l(-6), (lane_l, n['t_out'].cy - 6), (lane_l, n['mission'].cy), n['mission'].l()], ends='end')
    g.link('ros', [n['t_out'].l(6), (lane_l + 0.01, n['t_out'].cy + 6), (lane_l + 0.01, n['bridge'].cy), n['bridge'].l()], ends='end')
    g.link('ros', [n['t_out'].b(n['core'].cx - n['t_out'].cx), n['core'].t()], ends='end')
    g.link('ros', [n['agent'].l(n['t_out'].cy - n['agent'].cy), n['t_out'].r()], ends='end')
    lane_m = 490
    g.link('ros', [n['mission'].r(), (lane_m, n['mission'].cy), (lane_m, n['t_if'].cy - 20), n['t_if'].l(-20)])
    g.link('ros', [n['bridge'].r(-10), (lane_m, n['bridge'].cy - 10), (lane_m, n['t_if'].cy + 20), n['t_if'].l(20)])
    g.link('ros', [n['t_if'].r(), n['core'].l()])
    g.link('ros', [n['core'].b(), n['t_in'].t()], ends='end')
    g.link('ros', [n['t_in'].r(), n['agent'].l(n['t_in'].cy - n['agent'].cy)], ends='end')

    g.link('wire', [n['agent'].r(n['px_dds'].cy - n['agent'].cy), n['px_dds'].l()], 'UART', lpos=(1115, 443))
    g.link('wire', [n['router'].r(n['px_mav'].cy - n['router'].cy), n['px_mav'].l()], 'USB', lpos=(1115, 725))
    g.link('net', [n['router'].b(), n['j_ts'].t()], 'MAVLink · UDP', lpos=(n['router'].cx + 8, 801), anchor='start')
    g.link('net', [n['bridge'].b(), (n['bridge'].cx, n['j_ts'].cy + 18), n['j_ts'].l(18)], 'TCP', lpos=(n['bridge'].cx + 8, 860), anchor='start')
    g.link('wire', [n['px_rc'].r(), (n['elrs_rx'].x, n['px_rc'].cy)], 'CRSF')
    g.link('wire', [n['px_mav1'].r(), (n['rfd_air'].x, n['px_mav1'].cy)], optional=True)
    g.link('wire', [n['j_ts'].r(), n['modem'].l()], 'USB')

    g.link('rc', [n['elrs_rx'].r(), n['rc_tx'].l()], 'ELRS 2.4 GHz')
    g.link('rfd', [n['rfd_air'].r(), n['rfd_gnd'].l()], 'RFD900x · MAVLink', optional=True)
    g.link('net', [n['modem'].r(), n['tailnet'].l()], 'LTE')
    g.link('net', [n['tailnet'].r(), n['g_ts'].l()], 'WireGuard')
    g.link('video', [n['fpv_cam'].r(), n['fpv_mon'].l()], '5.8 GHz analog video', optional=True, ends='end')
    g.link('video', [n['fpv_mon'].b(), n['capture'].t()], 'AV/HDMI', lpos=(n['capture'].cx + 8, 985), anchor='start', optional=True, ends='end')
    g.link('video', [n['capture'].r(), n['viewer'].l()], 'USB', optional=True, ends='end')

    g.link('rfd', [n['rfd_gnd'].r(), (n['qgc'].x, n['rfd_gnd'].cy)], optional=True)
    lane = 2368
    g.link('net', [n['g_ts'].r(), (lane, n['g_ts'].cy), (lane, n['qgc'].cy), n['qgc'].r()], 'MAVLink · UDP', lpos=(lane - 6, 372), anchor='end', ends='end')
    g.link('net', [n['backend'].b(), n['g_ts'].t()], 'TCP', lpos=(n['backend'].cx + 8, 775), anchor='start', ends='end')
    g.link('net', [n['vite'].b(), n['backend'].t()], 'WebSocket proxy', lpos=(n['vite'].cx + 8, 619), anchor='start', ends='end')
    g.link('net', [n['browser'].b(), n['vite'].t()], 'HTTP + WebSocket', lpos=(n['vite'].cx + 8, 501), anchor='start', ends='end')
    g.legend(24, 1135)
    return g


# Simulation -----------------------------------------------------------------------------


def simulation():
    g = Diagram('sim', 1580, 760, 'Simulation',
                'Hardware replaced by Gazebo and PX4 SITL')
    g.region(20, 74, 1530, 640, 'Developer machine')
    g.group(40, 108, 1260, 520, 'Dev container', 'ROS 2')

    g.node('gz_cam', 60, 172, 195, 64, label='Gazebo camera', sub='simulated sensor', icon_name='depth_camera', optional=True)
    g.node('gz', 60, 312, 195, 76, label='Gazebo', sub=['physics + sensors', 'vehicle model'], icon_name='gazebo', isz=44)
    g.node('gz_gui', 60, 440, 195, 64, label='Gazebo GUI', sub='3D view', icon_name='sim_pc', optional=True)

    g.group(270, 142, 230, 460, 'PX4 SITL', 'replaces the Cube', icon_name='px4_sitl')
    sn = dict(w=200, kind='proc')
    g.node('px_gz', 285, 316, h=64, label='Gazebo bridge', sub='sensors in, motors out', **sn)
    g.node('px_dds', 285, 420, h=56, label='uXRCE-DDS client', sub='over UDP', **sn)
    g.node('px_mav', 285, 516, h=56, label='MAVLink', sub='over UDP', **sn)

    g.node('agent', 540, 420, 160, 56, label='MicroXRCEAgent', sub='UDP', kind='proc')

    g.group(740, 142, 270, 460, 'ROS 2 graph', kind='ros', icon_name='ros_graph')
    rn = dict(w=230, kind='proc')
    g.node('ros_gz', 760, 186, h=60, label='Gazebo → ROS 2 bridge', sub='camera images', optional=True, **rn)
    g.node('mission', 760, 296, h=60, label='Mission script', sub='flight core client', **rn)
    g.node('core', 760, 418, h=60, label='Flight core node', sub='sim mode (arming allowed)', **rn)
    g.node('bridge', 760, 530, h=60, label='Visualizer bridge node', sub='flight core client', **rn)

    g.group(1050, 142, 220, 460, 'Flight visualizer')
    vn = dict(w=190, kind='proc')
    g.node('vite', 1065, 296, h=60, label='Frontend dev server', sub='serves the dashboard', **vn)
    g.node('backend', 1065, 520, h=70, label='Visualizer backend', sub='relays state and commands', **vn)

    g.node('browser', 1340, 294, 190, 64, label='Browser', sub='visualizer dashboard', icon_name='browser')
    g.node('qgc', 1340, 610, 190, 64, label='QGroundControl', sub='MAVLink ground station', icon_name='laptop', optional=True)

    n = g.n
    g.link('gz', [n['gz_gui'].t(), n['gz'].b()], 'gz transport', lpos=(n['gz'].cx + 8, 418), anchor='start', optional=True)
    g.link('gz', [n['gz'].t(), n['gz_cam'].b()], 'sensor', lpos=(n['gz'].cx + 8, 278), anchor='start', optional=True, ends='end')
    g.link('gz', [n['gz_cam'].r(), (262, n['gz_cam'].cy), (262, 128), (n['ros_gz'].cx + 55, 128), n['ros_gz'].t(55)], 'gz transport · images', lpos=(500, 122), optional=True, ends='end')
    g.link('ros', [n['ros_gz'].b(), n['mission'].t()], 'camera images', lpos=(n['mission'].cx + 8, 276), anchor='start', optional=True, ends='end')
    g.link('gz', [n['gz'].r(), (n['px_gz'].x, n['gz'].cy)])
    g.link('net', [n['px_dds'].r(), n['agent'].l()], 'UDP', ldy=16)
    bus = 720
    g.link('ros', [n['agent'].r(), n['core'].l()])
    g.link('ros', [n['agent'].r(-8), (bus, n['agent'].cy - 8), (bus, n['mission'].cy), n['mission'].l()], ends='end')
    g.link('ros', [n['agent'].r(8), (bus, n['agent'].cy + 8), (bus, n['bridge'].cy), n['bridge'].l()], ends='end')
    g.link('ros', [n['mission'].b(), n['core'].t()], 'control', lpos=(n['core'].cx + 8, 392), anchor='start')
    g.link('ros', [n['bridge'].t(), n['core'].b()], 'control', lpos=(n['core'].cx + 8, 508), anchor='start')
    g.link('net', [n['bridge'].r(), n['backend'].l(n['bridge'].cy - n['backend'].cy)], 'TCP')
    g.link('net', [n['vite'].b(), n['backend'].t()], 'WebSocket proxy', lpos=(n['vite'].cx + 8, 440), anchor='start', ends='end')
    g.link('net', [n['browser'].l(), n['vite'].r()], 'HTTP · WS')
    g.link('net', [n['px_mav'].b(), (n['px_mav'].cx, n['qgc'].cy), n['qgc'].l()], 'MAVLink · UDP', lpos=(860, n['qgc'].cy - 6), optional=True, ends='end')
    g.legend(24, 740)
    return g


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, build in [('comm_l1_system', layer1), ('comm_l2_modules', layer2),
                        ('comm_l3_nodes', layer3), ('comm_sim', simulation)]:
        (OUT / f'{name}.svg').write_text(build().render())
        print(f'wrote {OUT / name}.svg')


if __name__ == '__main__':
    main()
