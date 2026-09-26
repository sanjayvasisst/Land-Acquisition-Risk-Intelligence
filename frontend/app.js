const form = document.getElementById('projectForm');
const sampleBtn = document.getElementById('sampleBtn');
const emptyState = document.getElementById('emptyState');
const results = document.getElementById('results');
const status = document.getElementById('status');
const errorBox = document.getElementById('error');

const sample = {
  project_type:'Highway', state:'Rajasthan', district:'Udaipur', land_area_acres:100,
  affected_families:50, approval_days:120, pending_approvals:2, legal_disputes:1,
  compensation_paid_pct:60, documentation_complete_pct:70, notifications_pending:1,
  ownership_conflicts:1, rehabilitation_progress_pct:50, possession_progress_pct:40,
  stakeholder_response_days:20, inter_departmental_issues:3, historical_delay_rate_pct:40
};

const numeric = new Set([
  'land_area_acres','affected_families','approval_days','pending_approvals','legal_disputes',
  'compensation_paid_pct','documentation_complete_pct','notifications_pending','ownership_conflicts',
  'rehabilitation_progress_pct','possession_progress_pct','stakeholder_response_days',
  'inter_departmental_issues','historical_delay_rate_pct'
]);

sampleBtn.onclick = () => {
  Object.entries(sample).forEach(([key, value]) => {
    const el = form.elements[key]; if (el) el.value = value;
  });
};

function payloadFromForm() {
  const data = {};
  for (const el of form.elements) {
    if (!el.name) continue;
    data[el.name] = numeric.has(el.name) ? Number(el.value) : el.value.trim();
  }
  return data;
}

function render(data) {
  emptyState.classList.add('hidden'); results.classList.remove('hidden');
  const pct = Math.round(data.delay_probability * 100);
  document.getElementById('probability').textContent = `${pct}%`;
  document.getElementById('risk').textContent = data.risk_level;
  document.getElementById('delay').textContent = data.expected_delay;
  status.textContent = `${data.risk_level} RISK`;
  status.className = `status ${data.risk_level.toLowerCase()}`;

  const drivers = document.getElementById('drivers');
  drivers.innerHTML = data.top_drivers.length ? data.top_drivers.map(d => `
    <div class="driver">
      <div class="driver-top"><span>${d.feature}</span><span>${d.contribution_pct}%</span></div>
      <div class="bar"><i style="width:${d.contribution_pct}%"></i></div>
      <small>${d.direction}</small>
    </div>`).join('') : '<p style="font-size:12px;color:#6d7788">SHAP explanation was not available for this request.</p>';

  document.getElementById('actions').innerHTML = data.recommendations.map(x => `<li>${x}</li>`).join('');
}

form.onsubmit = async (event) => {
  event.preventDefault(); errorBox.textContent = '';
  const button = form.querySelector('.primary'); button.disabled = true; button.textContent = 'Analyzing…';
  status.textContent = 'Analyzing'; status.className = 'status idle';
  try {
    const response = await fetch('/api/predict', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payloadFromForm())});
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail?.[0]?.msg || data.detail || 'Prediction failed');
    render(data);
  } catch (error) {
    errorBox.textContent = error.message;
    status.textContent = 'Error';
    status.className = 'status high';
  } finally {
    button.disabled = false; button.innerHTML = 'Analyze project <span>→</span>';
  }
};
