function renderOverlayImage(container, resultItem) {
  const host = typeof container === 'string' ? document.getElementById(container) : container;
  if (!host) {
    return;
  }

  host.innerHTML = '';
  if (!resultItem || !resultItem.overlay_path) {
    host.innerHTML = '<p class="muted">No overlay image available.</p>';
    return;
  }

  const wrap = document.createElement('div');
  wrap.className = 'overlay-wrap';

  const title = document.createElement('p');
  title.textContent = `Overlay: ${resultItem.filename || 'unknown'}`;

  const img = document.createElement('img');
  img.src = resultItem.overlay_path;
  img.alt = `Overlay result for ${resultItem.filename || 'image'}`;

  wrap.appendChild(title);
  wrap.appendChild(img);
  host.appendChild(wrap);
}

function renderStatsTable(container, resultItem) {
  const host = typeof container === 'string' ? document.getElementById(container) : container;
  if (!host) {
    return;
  }

  host.innerHTML = '';
  if (!resultItem) {
    host.innerHTML = '<p class="muted">No statistics available.</p>';
    return;
  }

  const rows = [
    ['Filename', resultItem.filename ?? 'N/A'],
    ['Grain count', resultItem.grain_count ?? 'N/A'],
    ['Mean area (um^2)', Number(resultItem.mean_area_um2 ?? 0).toFixed(2)],
    ['Std area (um^2)', Number(resultItem.std_area_um2 ?? 0).toFixed(2)],
    ['D10 (um^2)', Number(resultItem.d10_um2 ?? 0).toFixed(2)],
    ['D50 (um^2)', Number(resultItem.d50_um2 ?? 0).toFixed(2)],
    ['D90 (um^2)', Number(resultItem.d90_um2 ?? 0).toFixed(2)],
    ['Detection quality', resultItem.detection_quality ?? 'unknown']
  ];

  const table = document.createElement('table');
  table.className = 'stats-table';

  const tbody = document.createElement('tbody');
  rows.forEach(([k, v]) => {
    const tr = document.createElement('tr');
    const th = document.createElement('th');
    th.textContent = k;
    const td = document.createElement('td');
    td.textContent = String(v);
    tr.appendChild(th);
    tr.appendChild(td);
    tbody.appendChild(tr);
  });

  table.appendChild(tbody);
  host.appendChild(table);
}
