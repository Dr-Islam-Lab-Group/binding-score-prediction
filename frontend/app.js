const API_BASE = "https://your-backend-domain.com";

function setActiveButton(group, activeId) {
  group.forEach((id) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.toggle("active", id === activeId);
  });
}

function showMode(mode) {
  document.getElementById("single-panel").classList.toggle("hidden", mode !== "single");
  document.getElementById("csv-panel").classList.toggle("hidden", mode !== "csv");

  setActiveButton(["single-btn", "csv-btn"], mode === "single" ? "single-btn" : "csv-btn");
}

function renderSingleResult(targetId, data) {
  document.getElementById(targetId).innerHTML = `
    <div class="result-card">
      <div class="metric-label">Prediction Result</div>
      <div class="result-grid">
        <div class="metric">
          <div class="metric-label">Model</div>
          <div class="metric-value">ML Predictor</div>
        </div>
        <div class="metric">
          <div class="metric-label">Final Score</div>
          <div class="metric-value">${data.final_score}</div>
        </div>
        <div class="metric">
          <div class="metric-label">Status</div>
          <div class="metric-value">${data.status}</div>
        </div>
      </div>
    </div>
  `;
}

function renderBatchResult(targetId, data) {
  const rows = data.predictions.map((row) => {
    const ok = row.status === "success";
    return `
      <tr>
        <td>${row.smiles ?? ""}</td>
        <td>${row.active_site_residues ?? ""}</td>
        <td>${row.final_score ?? ""}</td>
        <td>
          <span class="status-pill ${ok ? "status-success" : "status-failed"}">
            ${row.status}
          </span>
        </td>
      </tr>
    `;
  }).join("");

  document.getElementById(targetId).innerHTML = `
    <div class="result-card">
      <div class="result-grid">
        <div class="metric">
          <div class="metric-label">Total Rows</div>
          <div class="metric-value">${data.total_rows}</div>
        </div>
        <div class="metric">
          <div class="metric-label">Success Rows</div>
          <div class="metric-value">${data.success_rows}</div>
        </div>
        <div class="metric">
          <div class="metric-label">Failed Rows</div>
          <div class="metric-value">${data.failed_rows}</div>
        </div>
      </div>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>SMILES</th>
              <th>Active-site residues</th>
              <th>Final score</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    </div>
  `;
}

async function predictSingle() {
  const smiles = document.getElementById("smiles").value.trim();
  const residues = document.getElementById("residues").value.trim();
  const resultId = "single-result";

  if (!smiles) {
    alert("Please enter a ligand SMILES string.");
    return;
  }

  if (residues.length !== 27) {
    alert("Please enter exactly 27 active-site residues.");
    return;
  }

  document.getElementById(resultId).innerHTML = `<div class="result-card">Running prediction...</div>`;

  try {
    const response = await fetch(`${API_BASE}/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        smiles: smiles,
        active_site_residues: residues
      })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Prediction failed");
    }

    renderSingleResult(resultId, data);
  } catch (error) {
    document.getElementById(resultId).innerHTML = `
      <div class="result-card">
        <div class="metric-label">Error</div>
        <div class="metric-value">${error.message}</div>
      </div>
    `;
  }
}

async function predictBatch() {
  const fileInput = document.getElementById("csv-file");
  const file = fileInput.files[0];
  const resultId = "batch-result";

  if (!file) {
    alert("Please upload a CSV file.");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  document.getElementById(resultId).innerHTML = `<div class="result-card">Running batch prediction...</div>`;

  try {
    const response = await fetch(`${API_BASE}/predict-batch`, {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Batch prediction failed");
    }

    renderBatchResult(resultId, data);
  } catch (error) {
    document.getElementById(resultId).innerHTML = `
      <div class="result-card">
        <div class="metric-label">Error</div>
        <div class="metric-value">${error.message}</div>
      </div>
    `;
  }
}

showMode("single");
