function plotGrainHistogram(containerId, areasUm2, stats) {
  const target = typeof containerId === 'string' ? document.getElementById(containerId) : containerId;
  if (!target) {
    return;
  }

  if (!areasUm2 || areasUm2.length === 0) {
    target.innerHTML = '<p class="muted">No grain area data available for this image.</p>';
    return;
  }

  const trace = {
    x: areasUm2,
    type: 'histogram',
    marker: { color: '#01696f' },
    opacity: 0.8,
    name: 'Area distribution'
  };

  const shapeColor = '#964219';
  const shapes = ['d10_um2', 'd50_um2', 'd90_um2']
    .filter((k) => Number.isFinite(Number(stats?.[k])))
    .map((k) => ({
      type: 'line',
      x0: Number(stats[k]),
      x1: Number(stats[k]),
      y0: 0,
      y1: 1,
      xref: 'x',
      yref: 'paper',
      line: { color: shapeColor, dash: 'dash', width: 2 }
    }));

  const annotations = ['d10_um2', 'd50_um2', 'd90_um2']
    .filter((k) => Number.isFinite(Number(stats?.[k])))
    .map((k, idx) => ({
      x: Number(stats[k]),
      y: 1,
      yref: 'paper',
      xref: 'x',
      text: `${k.replace('_um2', '').toUpperCase()}: ${Number(stats[k]).toFixed(2)}`,
      showarrow: false,
      yshift: -14 - idx * 14,
      font: { size: 11, color: shapeColor }
    }));

  const layout = {
    margin: { t: 20, r: 10, b: 50, l: 55 },
    xaxis: { title: 'Grain / feature area (um^2)' },
    yaxis: { title: 'Count' },
    shapes,
    annotations
  };

  Plotly.newPlot(target, [trace], layout, { displayModeBar: false, responsive: true });
}

function plotComparisonHistograms(containerId, series) {
  const target = typeof containerId === 'string' ? document.getElementById(containerId) : containerId;
  if (!target) {
    return;
  }

  const valid = (series || []).filter((s) => Array.isArray(s.areasUm2) && s.areasUm2.length > 0);
  if (valid.length === 0) {
    target.innerHTML = '<p class="muted">Select at least one image with area data to compare.</p>';
    return;
  }

  const palette = ['#0a6d6d', '#d17a22', '#7f5539', '#4f772d', '#3d5a80'];
  const traces = valid.map((entry, i) => ({
    x: entry.areasUm2,
    type: 'histogram',
    opacity: 0.5,
    marker: { color: palette[i % palette.length] },
    name: entry.label,
    histnorm: 'probability density'
  }));

  const layout = {
    barmode: 'overlay',
    margin: { t: 20, r: 10, b: 50, l: 55 },
    xaxis: { title: 'Grain / feature area (um^2)' },
    yaxis: { title: 'Density' },
    legend: { orientation: 'h' }
  };

  Plotly.newPlot(target, traces, layout, { displayModeBar: false, responsive: true });
}
