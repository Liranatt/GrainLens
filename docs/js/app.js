async function loadIndex() {
  try {
    const res = await fetch('data/results/index.json', { cache: 'no-store' });
    if (!res.ok) {
      return [];
    }
    const data = await res.json();
    return Array.isArray(data) ? data : [];
  } catch (err) {
    console.warn('Could not load index.json', err);
    return [];
  }
}

async function loadCases() {
  try {
    const res = await fetch('data/case_studies.json', { cache: 'no-store' });
    if (!res.ok) {
      return [];
    }
    const data = await res.json();
    return Array.isArray(data) ? data : [];
  } catch (err) {
    console.warn('Could not load case_studies.json', err);
    return [];
  }
}

function initTabs() {
  const tabs = document.querySelectorAll('button.tab');
  const panes = document.querySelectorAll('.tab-pane');

  tabs.forEach((btn) => {
    btn.addEventListener('click', () => {
      const id = btn.dataset.tab;
      tabs.forEach((b) => b.classList.toggle('active', b === btn));
      panes.forEach((p) => p.classList.toggle('active', p.id === `tab-${id}`));
    });
  });
}

async function loadPerImageJson(filename) {
  const stem = filename.replace(/\.[^/.]+$/, '');
  try {
    const res = await fetch(`data/results/${stem}.json`, { cache: 'no-store' });
    if (!res.ok) {
      return null;
    }
    return await res.json();
  } catch {
    return null;
  }
}

function initAnalyzeTab(index) {
  const controls = document.getElementById('analyze-controls');
  const imgHost = document.getElementById('analyze-image');
  const statsHost = document.getElementById('analyze-stats');
  const chartHost = document.getElementById('analyze-chart');

  controls.innerHTML = '';
  if (!index.length) {
    controls.innerHTML = '<p class="muted">No processed results found. Run python -m pipeline.process first.</p>';
    imgHost.innerHTML = '<p class="muted">No image selected.</p>';
    statsHost.innerHTML = '<p class="muted">No stats to display.</p>';
    chartHost.innerHTML = '<p class="muted">No chart to display.</p>';
    return;
  }

  const row = document.createElement('div');
  row.className = 'form-row';

  const label = document.createElement('label');
  label.setAttribute('for', 'image-select');
  label.textContent = 'Select image:';

  const select = document.createElement('select');
  select.id = 'image-select';

  index.forEach((item) => {
    const opt = document.createElement('option');
    opt.value = item.filename;
    opt.textContent = item.filename;
    select.appendChild(opt);
  });

  row.appendChild(label);
  row.appendChild(select);
  controls.appendChild(row);

  const renderSelected = async () => {
    const selectedName = select.value;
    const fromIndex = index.find((it) => it.filename === selectedName) || null;
    const fullData = (await loadPerImageJson(selectedName)) || fromIndex;

    renderOverlayImage(imgHost, fullData || fromIndex);
    renderStatsTable(statsHost, fullData || fromIndex);
    plotGrainHistogram('analyze-chart', fullData?.areas_um2 || [], fullData || fromIndex || {});
  };

  select.addEventListener('change', renderSelected);
  renderSelected();
}

async function initCasesTab() {
  const container = document.getElementById('cases-container');
  const cases = await loadCases();
  if (!cases.length) {
    container.innerHTML = '<p class="muted">No case studies found yet. Fill data/case_studies.json.</p>';
    return;
  }

  container.innerHTML = '';
  cases.forEach((entry) => {
    const card = document.createElement('article');
    card.className = 'case-card';
    card.innerHTML = `
      <h3>${entry.title || entry.case_id || 'Untitled case'}</h3>
      <p><strong>Case ID:</strong> ${entry.case_id || 'N/A'}</p>
      <p><strong>Processing:</strong> ${entry.processing_text || 'TO_FILL'}</p>
      <p><strong>Thermodynamics:</strong> ${entry.thermo_text || 'TO_FILL'}</p>
      <p><strong>Key features:</strong> ${(entry.key_features || []).join(', ') || 'TO_FILL'}</p>
      <p><strong>Expected properties:</strong> ${entry.expected_properties || 'TO_FILL'}</p>
      <p><strong>Application notes:</strong> ${entry.application_notes || 'TO_FILL'}</p>
      <p><strong>Report summary:</strong> ${entry.report_summary || 'TO_FILL'}</p>
    `;
    container.appendChild(card);
  });
}

function initCompareTab(index) {
  const controls = document.getElementById('compare-controls');
  controls.innerHTML = '';
  const chartId = 'compare-chart';

  if (!index.length) {
    document.getElementById(chartId).innerHTML = '<p class="muted">No processed results available to compare.</p>';
    return;
  }

  const helper = document.createElement('p');
  helper.className = 'muted';
  helper.textContent = 'Select one or more images to compare their grain area distributions.';
  controls.appendChild(helper);

  const checklist = document.createElement('div');
  checklist.className = 'form-row';
  controls.appendChild(checklist);

  const update = async () => {
    const selected = Array.from(checklist.querySelectorAll('input[type="checkbox"]:checked'))
      .map((cb) => cb.value);

    const series = [];
    for (const filename of selected) {
      const full = await loadPerImageJson(filename);
      const fallback = index.find((item) => item.filename === filename);
      const merged = full || fallback;
      if (!merged) {
        continue;
      }
      series.push({
        label: merged.filename,
        areasUm2: merged.areas_um2 || []
      });
    }

    plotComparisonHistograms(chartId, series);
  };

  index.forEach((item, i) => {
    const wrap = document.createElement('label');
    wrap.style.display = 'inline-flex';
    wrap.style.alignItems = 'center';
    wrap.style.gap = '0.25rem';

    const cb = document.createElement('input');
    cb.type = 'checkbox';
    cb.value = item.filename;
    cb.checked = i < Math.min(2, index.length);
    cb.addEventListener('change', update);

    const text = document.createElement('span');
    text.textContent = item.filename;

    wrap.appendChild(cb);
    wrap.appendChild(text);
    checklist.appendChild(wrap);
  });

  update();
}

document.addEventListener('DOMContentLoaded', async () => {
  initTabs();
  const index = await loadIndex();
  initAnalyzeTab(index);
  await initCasesTab();
  initCompareTab(index);
});
