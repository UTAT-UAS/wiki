// Communication link diagrams: optional-component toggle, zoom, pan and full screen.
//
// Usage in Markdown (needs md_in_html):
//   <div class="cd-diagram" markdown>![alt](diagrams/x.svg)</div>
//
// The SVG is fetched and inlined so the page theme applies to it. Optional
// parts carry the cd-optional class, written by media/build_comm_diagrams.py.
// Without JavaScript the plain <img> stays as the fallback.
(() => {
  async function setup(root) {
    if (root.dataset.cdReady) return;
    root.dataset.cdReady = '1';
    const img = root.querySelector('img');
    if (!img) return;

    let svg;
    try {
      const res = await fetch(img.src);
      if (!res.ok) return;
      const doc = new DOMParser().parseFromString(await res.text(), 'image/svg+xml');
      svg = doc.documentElement;
      if (svg.nodeName !== 'svg') return;
    } catch {
      return; // keep the <img> fallback
    }
    svg = document.importNode(svg, true);
    svg.removeAttribute('width');
    svg.removeAttribute('height');

    const stage = document.createElement('div');
    stage.className = 'cd-stage';
    stage.append(svg);

    // Zoom and pan by changing the viewBox, clamped to the full diagram.
    const base = svg.viewBox.baseVal;
    const full = { x: base.x, y: base.y, w: base.width, h: base.height };
    let view = { ...full };
    const setView = (v) => {
      const w = Math.min(full.w, Math.max(full.w / 8, v.w));
      const h = (w / full.w) * full.h;
      const x = Math.min(full.x + full.w - w, Math.max(full.x, v.x));
      const y = Math.min(full.y + full.h - h, Math.max(full.y, v.y));
      view = { x, y, w, h };
      svg.setAttribute('viewBox', `${x} ${y} ${w} ${h}`);
      stage.classList.toggle('is-zoomed', w < full.w - 0.5);
    };
    const zoomAt = (factor, cx = view.x + view.w / 2, cy = view.y + view.h / 2) => {
      const w = view.w / factor;
      const h = view.h / factor;
      setView({ x: cx - ((cx - view.x) / view.w) * w, y: cy - ((cy - view.y) / view.h) * h, w, h });
    };

    let drag = null;
    stage.addEventListener('pointerdown', (e) => {
      if (e.button !== 0 || !stage.classList.contains('is-zoomed')) return;
      drag = { x: e.clientX, y: e.clientY, view: { ...view } };
      stage.setPointerCapture(e.pointerId);
      stage.classList.add('is-dragging');
    });
    stage.addEventListener('pointermove', (e) => {
      if (!drag) return;
      const scale = view.w / svg.getBoundingClientRect().width;
      setView({ ...drag.view, x: drag.view.x - (e.clientX - drag.x) * scale, y: drag.view.y - (e.clientY - drag.y) * scale });
    });
    const endDrag = () => {
      drag = null;
      stage.classList.remove('is-dragging');
    };
    stage.addEventListener('pointerup', endDrag);
    stage.addEventListener('pointercancel', endDrag);
    stage.addEventListener(
      'wheel',
      (e) => {
        // Scrolling over the diagram zooms it instead of scrolling the page.
        e.preventDefault();
        const r = svg.getBoundingClientRect();
        const cx = view.x + ((e.clientX - r.left) / r.width) * view.w;
        const cy = view.y + ((e.clientY - r.top) / r.height) * view.h;
        zoomAt(e.deltaY < 0 ? 1.15 : 1 / 1.15, cx, cy);
      },
      { passive: false },
    );

    const bar = document.createElement('div');
    bar.className = 'cd-toolbar';
    const label = document.createElement('label');
    label.className = 'cd-toggle';
    const opt = document.createElement('input');
    opt.type = 'checkbox';
    opt.checked = true;
    opt.addEventListener('change', () => svg.classList.toggle('hide-optional', !opt.checked));
    label.append(opt, ' Show optional components');
    const hint = document.createElement('span');
    hint.className = 'cd-hint';
    hint.textContent = 'Scroll to zoom · drag to pan';
    const open = document.createElement('a');
    open.className = 'cd-btn';
    open.href = img.src;
    open.target = '_blank';
    open.rel = 'noopener';
    open.title = 'Open the SVG on its own';
    open.textContent = 'SVG';
    bar.append(
      label,
      hint,
      button('+', 'Zoom in', () => zoomAt(1.4)),
      button('−', 'Zoom out', () => zoomAt(1 / 1.4)),
      button('⟲', 'Reset view', () => setView(full)),
      button('⛶', 'Full screen', () => {
        if (document.fullscreenElement) document.exitFullscreen();
        else root.requestFullscreen?.();
      }),
      open,
    );

    // md_in_html wraps the image in a <p>; replace that too.
    const p = img.parentElement;
    (p.tagName === 'P' && p.childElementCount === 1 && !p.textContent.trim() ? p : img).replaceWith(bar, stage);
  }

  function button(text, title, onClick) {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'cd-btn';
    b.textContent = text;
    b.title = title;
    b.setAttribute('aria-label', title);
    b.addEventListener('click', onClick);
    return b;
  }

  const run = () => document.querySelectorAll('.cd-diagram').forEach(setup);
  if (window.document$) window.document$.subscribe(run);
  else if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run);
  else run();
})();
