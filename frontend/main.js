const API_BASE = 'http://localhost:8000';

const fileInput = document.getElementById('file-input');
const uploadBtn = document.getElementById('upload-btn');
const statusEl  = document.getElementById('upload-status');

// ── Pie chart colours (cycles if more categories) ──────────
const PIE_COLORS = [
    '#6c63ff', '#ff6584', '#43b89c', '#f9a825',
    '#ef5350', '#42a5f5', '#ab47bc', '#26a69a',
    '#ff7043', '#8d6e63',
];

async function loadExpenseBreakdown(paymentsId) {
    const chartEl  = document.getElementById('expense-breakdown-chart');
    const legendEl = document.getElementById('expense-breakdown-legend');
    const emptyEl  = document.getElementById('expense-breakdown-empty');

    try {
        const res = await fetch(
            `${API_BASE}/main-insights/spending-by-category?dataset_id=${paymentsId}`
        );
        if (!res.ok) throw new Error(`Server error ${res.status}`);

        const records = await res.json();

        // Filter out zero / negative GEL values
        const data = records.filter(r => r.GEL > 0);
        if (!data.length) {
            emptyEl.textContent = 'No GEL spending data found.';
            return;
        }

        emptyEl.style.display = 'none';
        chartEl.style.display = 'block';
        legendEl.style.display = 'flex';

        const series = data.map(r => r.GEL);
        const labels = data.map(r => r.category);
        const total  = series.reduce((a, b) => a + b, 0);

        // Inject per-slice colours via a <style> tag
        const styleTag = document.getElementById('pie-colors') || document.createElement('style');
        styleTag.id = 'pie-colors';
        styleTag.textContent = data.map((_, i) => `
            .ct-series-${String.fromCharCode(97 + i)} .ct-slice-pie {
                fill: ${PIE_COLORS[i % PIE_COLORS.length]};
                stroke: #fff;
                stroke-width: 2px;
            }
        `).join('');
        document.head.appendChild(styleTag);

        new Chartist.Pie('#expense-breakdown-chart', { series, labels }, {
            donut: true,
            donutWidth: 60,
            showLabel: false,
            startAngle: 270,
        });

        // Build legend
        legendEl.innerHTML = data.map((r, i) => `
            <li class="pie-legend-item">
                <span class="pie-legend-dot" style="background:${PIE_COLORS[i % PIE_COLORS.length]}"></span>
                <span class="pie-legend-label">${r.category}</span>
                <span class="pie-legend-value">₾${r.GEL.toFixed(2)}</span>
                <span class="pie-legend-pct">${((r.GEL / total) * 100).toFixed(1)}%</span>
            </li>
        `).join('');

    } catch (err) {
        emptyEl.textContent = `Failed to load chart: ${err.message}`;
    }
}

// ── Upload ─────────────────────────────────────────────────
fileInput.addEventListener('change', async () => {
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    uploadBtn.disabled    = true;
    uploadBtn.textContent = 'Uploading…';
    statusEl.className    = 'upload-status';
    statusEl.textContent  = '';

    try {
        const res = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData,
        });

        if (!res.ok) {
            const err = await res.text();
            throw new Error(err || `Server error ${res.status}`);
        }

        const uploadData = await res.json();
        window._transactionsId = uploadData.transactions_id;
        window._paymentsId     = uploadData.payments_id;

        statusEl.className    = 'upload-status upload-status--success';
        statusEl.textContent  = `✓ "${file.name}" uploaded successfully`;
        uploadBtn.textContent = file.name;

        loadExpenseBreakdown(uploadData.payments_id);

    } catch (err) {
        statusEl.className    = 'upload-status upload-status--error';
        statusEl.textContent  = `✗ Upload failed: ${err.message}`;
        uploadBtn.textContent = 'Upload file';
    } finally {
        uploadBtn.disabled = false;
        fileInput.value = '';
    }
});
