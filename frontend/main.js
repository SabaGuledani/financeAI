const API_BASE = 'http://localhost:8000';

const fileInput = document.getElementById('file-input');
const uploadBtn = document.getElementById('upload-btn');
const statusEl = document.getElementById('upload-status');

// ── Pie chart colours: biggest → smallest → others ─────────
const PIE_COLORS = [
    '#455e91', '#6681B7', '#9EAFD1', '#bac6de', '#CCDAF5', '#DFE9F3',
];

async function loadExpenseBreakdown(paymentsId) {
    const chartEl = document.getElementById('expense-breakdown-chart');
    const legendEl = document.getElementById('expense-breakdown-legend');
    const emptyEl = document.getElementById('expense-breakdown-empty');

    try {
        const res = await fetch(
            `${API_BASE}/main-insights/spending-by-category?dataset_id=${paymentsId}`
        );
        if (!res.ok) throw new Error(`Server error ${res.status}`);

        const records = await res.json();

        // Filter out zero / negative GEL values, already sorted desc by backend
        const positive = records.filter(r => r.GEL > 0);
        if (!positive.length) {
            emptyEl.textContent = 'No GEL spending data found.';
            return;
        }

        // Top 5 + "Others" bucket for the rest
        const top5 = positive.slice(0, 5);
        const rest = positive.slice(5);
        const othersTotal = rest.reduce((sum, r) => sum + r.GEL, 0);

        const data = othersTotal > 0
            ? [...top5, { category: 'Others', GEL: othersTotal }]
            : top5;

        emptyEl.style.display = 'none';
        chartEl.style.display = 'block';
        legendEl.style.display = 'flex';

        const series = data.map(r => r.GEL);
        const labels = data.map(r => r.category);
        const total = series.reduce((a, b) => a + b, 0);

        const pie = new Chartist.Pie('#expense-breakdown-chart', { series, labels }, {
            donut: true,
            donutWidth: 60,
            showLabel: false,
            startAngle: 270,
        });

        pie.on('draw', (ctx) => {
            if (ctx.type === 'slice') {
                const color = PIE_COLORS[ctx.index] || PIE_COLORS[PIE_COLORS.length - 1];
                ctx.element.attr({ style: `stroke: ${color}; fill: none;` });
            }
        });

        // Build legend
        legendEl.innerHTML = data.map((r, i) => `
            <li class="pie-legend-item">
                <span class="pie-legend-dot" style="background:${PIE_COLORS[i] || PIE_COLORS[PIE_COLORS.length - 1]}"></span>
                <span class="pie-legend-label">${r.category}</span>
                <span class="pie-legend-value">₾${r.GEL.toFixed(2)}</span>
                <span class="pie-legend-pct">${((r.GEL / total) * 100).toFixed(1)}%</span>
            </li>
        `).join('');

    } catch (err) {
        emptyEl.textContent = `Failed to load chart: ${err.message}`;
    }
}

// ── Spending Over Time line chart ─────────────────────────
const MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

// Tooltip element — created once, shared across re-renders
const lineTooltip = document.createElement('div');
lineTooltip.className = 'line-tooltip';
lineTooltip.style.display = 'none';
document.body.appendChild(lineTooltip);

function moveTooltip(e) {
    lineTooltip.style.left = (e.pageX + 16) + 'px';
    lineTooltip.style.top = (e.pageY - 56) + 'px';
}

async function loadSpendingOverTime(transactionsId) {
    const chartEl = document.getElementById('spending-over-time-chart');
    const emptyEl = document.getElementById('spending-over-time-empty');

    try {
        const res = await fetch(
            `${API_BASE}/main-insights/spending-by-month?dataset_id=${transactionsId}`
        );
        if (!res.ok) throw new Error(`Server error ${res.status}`);

        const records = await res.json();
        console.log(records);

        const data = records.filter(r => r.GEL > 0);
        if (!data.length) {
            emptyEl.textContent = 'No monthly GEL data found.';
            return;
        }

        // Sort chronologically
        data.sort((a, b) => a.year !== b.year ? a.year - b.year : a.month - b.month);

        const labels = data.map(r => `${MONTH_NAMES[r.month - 1]} ${r.year}`);
        const series = [data.map(r => r.GEL)];

        emptyEl.style.display = 'none';
        chartEl.style.display = 'block';

        // Thin x-axis labels: show all up to 12, every 2nd up to 24, every 3rd beyond
        const xLabelFn = (v, i) => {
            if (labels.length <= 12) return v;
            if (labels.length <= 24) return i % 2 === 0 ? v : null;
            return i % 3 === 0 ? v : null;
        };

        const chart = new Chartist.Line('#spending-over-time-chart', { labels, series }, {
            fullWidth: true,
            chartPadding: { right: 24, left: 8, top: 20, bottom: 0 },
            axisY: {
                labelInterpolationFnc: v => `₾${Math.round(v)}`,
            },
            axisX: {
                labelInterpolationFnc: xLabelFn,
            },
            lineSmooth: Chartist.Interpolation.cardinal({ tension: 0.2 }),
            low: 0,
            showArea: true,
        });

        // Stamp each point with its real label + value as the chart draws
        chart.on('draw', (ctx) => {
            if (ctx.type === 'point') {
                ctx.element._node.setAttribute('data-label', labels[ctx.index]);
                ctx.element._node.setAttribute('data-value', data[ctx.index].GEL.toFixed(2));
            }
        });

        // Attach tooltip listeners after the SVG is fully rendered
        chart.on('created', () => {
            chartEl.querySelectorAll('.ct-point').forEach((point) => {
                const fresh = point.cloneNode(true);
                point.parentNode.replaceChild(fresh, point);

                fresh.addEventListener('mouseenter', (e) => {
                    lineTooltip.innerHTML = `
                        <span class="tt-month">${fresh.getAttribute('data-label')}</span>
                        <span class="tt-value">₾${fresh.getAttribute('data-value')}</span>
                    `;
                    lineTooltip.style.display = 'flex';
                    moveTooltip(e);
                });
                fresh.addEventListener('mousemove', moveTooltip);
                fresh.addEventListener('mouseleave', () => {
                    lineTooltip.style.display = 'none';
                });
            });
        });

    } catch (err) {
        emptyEl.textContent = `Failed to load chart: ${err.message}`;
    }
}

// ── Top Merchants bar chart ────────────────────────────────
const barTooltip = document.createElement('div');
barTooltip.className = 'line-tooltip';
barTooltip.style.display = 'none';
document.body.appendChild(barTooltip);

function moveBarTooltip(e) {
    barTooltip.style.left = (e.pageX + 16) + 'px';
    barTooltip.style.top = (e.pageY - 56) + 'px';
}

async function loadTopMerchants(paymentsId) {
    const chartEl = document.getElementById('top-merchants-chart');
    const emptyEl = document.getElementById('top-merchants-empty');

    try {
        const res = await fetch(
            `${API_BASE}/behaviour/spending-by-merchant?dataset_id=${paymentsId}`
        );
        if (!res.ok) throw new Error(`Server error ${res.status}`);

        const records = await res.json();

        const data = records.filter(r => r.GEL > 0).slice(0, 10);
        if (!data.length) {
            emptyEl.textContent = 'No merchant data found.';
            return;
        }

        // Chartist horizontal bars render bottom-to-top, so reverse for top-down display
        const reversed = [...data].reverse();
        const labels = reversed.map(r => r.transaction_object);
        const series = [reversed.map(r => parseFloat(r.GEL.toFixed(2)))];

        emptyEl.style.display = 'none';
        chartEl.style.display = 'block';

        const chart = new Chartist.Bar('#top-merchants-chart', { labels, series }, {
            seriesBarDistance: 10,
            reverseData: false,
            horizontalBars: true,
            axisY: {
                offset: 108,
                labelOffset: { x: -10, y: 0 },
                labelInterpolationFnc: v => v.length > 12 ? v.slice(0, 11) + '…' : v,
            },
            axisX: {
                labelInterpolationFnc: v => `₾${Math.round(v)}`,
                onlyInteger: true,
            },
            chartPadding: { top: 8, right: 24, bottom: 8, left: 0 },
        });

        // Stamp real data onto each bar via the draw event
        chart.on('draw', (ctx) => {
            if (ctx.type === 'bar') {
                const item = reversed[ctx.index];
                ctx.element._node.setAttribute('data-merchant', item.transaction_object);
                ctx.element._node.setAttribute('data-value', item.GEL.toFixed(2));
            }
        });

        chart.on('created', () => {
            chartEl.querySelectorAll('.ct-bar').forEach((bar) => {
                const fresh = bar.cloneNode(true);
                bar.parentNode.replaceChild(fresh, bar);

                fresh.addEventListener('mouseenter', (e) => {
                    barTooltip.innerHTML = `
                        <span class="tt-month">${fresh.getAttribute('data-merchant')}</span>
                        <span class="tt-value">₾${fresh.getAttribute('data-value')}</span>
                    `;
                    barTooltip.style.display = 'flex';
                    moveBarTooltip(e);
                });
                fresh.addEventListener('mousemove', moveBarTooltip);
                fresh.addEventListener('mouseleave', () => {
                    barTooltip.style.display = 'none';
                });
            });
        });

    } catch (err) {
        emptyEl.textContent = `Failed to load chart: ${err.message}`;
    }
}

// ── Merchant last transactions ─────────────────────────────
async function loadMerchantLastTransactions(paymentsId) {
    const emptyEl  = document.getElementById('merchant-last-empty');
    const tableEl  = document.getElementById('merchant-last-table');
    const tbodyEl  = document.getElementById('merchant-last-tbody');
    const nameEl   = document.getElementById('merchant-last-name');

    try {
        const res = await fetch(
            `${API_BASE}/behaviour/top-merchant-last-transactions?dataset_id=${paymentsId}`
        );
        if (!res.ok) throw new Error(`Server error ${res.status}`);

        const records = await res.json();
        if (!records.length) {
            emptyEl.textContent = 'No transactions found.';
            return;
        }

        nameEl.textContent  = records[0].transaction_object;
        emptyEl.style.display = 'none';
        tableEl.style.display = 'table';

        tbodyEl.innerHTML = records.map(r => {
            const date = new Date(r['თარიღი']).toLocaleDateString('en-GB', {
                day: 'numeric', month: 'short', year: 'numeric'
            });
            return `<tr>
                <td>${date}</td>
                <td class="amount-cell">₾${r.GEL.toFixed(2)}</td>
            </tr>`;
        }).join('');

    } catch (err) {
        emptyEl.textContent = `Failed to load: ${err.message}`;
    }
}

// ── Frequency card ─────────────────────────────────────────
async function loadFrequency(paymentsId) {
    try {
        const [perDayRes, mostActiveRes] = await Promise.all([
            fetch(`${API_BASE}/behaviour/transactions-per-day?dataset_id=${paymentsId}`),
            fetch(`${API_BASE}/behaviour/most-active-day?dataset_id=${paymentsId}`),
        ]);

        if (perDayRes.ok) {
            const records = await perDayRes.json();
            // GEL column holds the count (it's a .count() result from the backend)
            const counts = records.map(r => r.GEL);
            const avg = counts.reduce((a, b) => a + b, 0) / counts.length;
            const max = Math.max(...counts);
            document.getElementById('freq-avg-per-day').textContent  = avg.toFixed(1);
            document.getElementById('freq-max-per-day').textContent  = max;
        }

        if (mostActiveRes.ok) {
            const records = await mostActiveRes.json();
            if (records.length) {
                const raw  = records[0]['თარიღი'];           // "2025-07-26T00:00:00"
                const date = new Date(raw);
                const formatted = date.toLocaleDateString('en-GB', {
                    day: 'numeric', month: 'short', year: 'numeric'
                });
                document.getElementById('freq-most-active-day').textContent = formatted;
            }
        }
    } catch (err) {
        console.error('Failed to load frequency data:', err);
    }
}

// ── Totals panel ───────────────────────────────────────────
async function loadTotals(paymentsId) {
    try {
        const [spendingRes, countRes, meansRes] = await Promise.all([
            fetch(`${API_BASE}/main-insights/total-spending?dataset_id=${paymentsId}`),
            fetch(`${API_BASE}/main-insights/transaction-count?dataset_id=${paymentsId}`),
            fetch(`${API_BASE}/main-insights/transaction-means?dataset_id=${paymentsId}`),
        ]);

        if (spendingRes.ok) {
            const s = await spendingRes.json();
            document.getElementById('total-spending').textContent = s.GEL.toFixed(2);
        }
        if (countRes.ok) {
            const c = await countRes.json();
            document.getElementById('transaction-count').textContent = c.count;
        }
        if (meansRes.ok) {
            const m = await meansRes.json();
            document.getElementById('avg-transaction').textContent = m.GEL.toFixed(2);
        }
    } catch (err) {
        console.error('Failed to load totals:', err);
    }
}

// ── Biggest Purchase ───────────────────────────────────────
async function loadBiggestPurchase(paymentsId) {
    try {
        const res = await fetch(
            `${API_BASE}/main-insights/biggest-spending?dataset_id=${paymentsId}`
        );
        if (!res.ok) throw new Error(`Server error ${res.status}`);

        const records = await res.json();
        const top = records[0];
        if (!top) return;

        document.getElementById('biggest-purchase-name').textContent   = top.transaction_object;
        document.getElementById('biggest-purchase-amount').textContent = `₾${top.GEL.toFixed(2)}`;
    } catch (err) {
        document.getElementById('biggest-purchase-name').textContent = 'Error loading';
    }
}

// ── Top Merchant ───────────────────────────────────────────
async function loadTopMerchant(paymentsId) {
    try {
        const res = await fetch(
            `${API_BASE}/behaviour/spending-by-merchant?dataset_id=${paymentsId}`
        );
        if (!res.ok) throw new Error(`Server error ${res.status}`);

        const records = await res.json();
        const top = records.find(r => r.GEL > 0);
        if (!top) return;

        document.getElementById('top-merchant-name').textContent   = top.transaction_object;
        document.getElementById('top-merchant-amount').textContent = `₾${top.GEL.toFixed(2)}`;
    } catch (err) {
        document.getElementById('top-merchant-name').textContent = 'Error loading';
    }
}

// ── Average Spending by Day of Week bar chart ──────────────
async function loadAvgSpendingByDay(paymentsId) {
    const chartEl = document.getElementById('avg-spending-day-chart');
    const emptyEl = document.getElementById('avg-spending-day-empty');

    try {
        const res = await fetch(
            `${API_BASE}/behaviour/avg-spending-by-weekday?dataset_id=${paymentsId}`
        );
        if (!res.ok) throw new Error(`Server error ${res.status}`);

        const records = await res.json();

        if (!records.length) {
            emptyEl.textContent = 'No data found.';
            return;
        }

        // records are already sorted Mon–Sun (weekday 0–6) from backend
        const labels = records.map(r => r.weekday_name.slice(0, 3)); // Mon, Tue…
        const series = [records.map(r => parseFloat(r.GEL.toFixed(2)))];

        emptyEl.style.display = 'none';
        chartEl.style.display = 'block';

        const chart = new Chartist.Bar('#avg-spending-day-chart', { labels, series }, {
            fullWidth: true,
            chartPadding: { top: 20, right: 16, bottom: 16, left: 8 },
            axisY: {
                labelInterpolationFnc: v => `₾${Math.round(v)}`,
                onlyInteger: true,
            },
            axisX: {
                offset: 42,
                labelOffset: { x: 0, y: 10 },
            },
        });

        // Stamp actual values onto each bar
        chart.on('draw', (ctx) => {
            if (ctx.type === 'bar') {
                ctx.element._node.setAttribute('data-label', records[ctx.index].weekday_name);
                ctx.element._node.setAttribute('data-value', records[ctx.index].GEL.toFixed(2));
            }
        });

        chart.on('created', () => {
            chartEl.querySelectorAll('.ct-bar').forEach((bar) => {
                const fresh = bar.cloneNode(true);
                bar.parentNode.replaceChild(fresh, bar);

                fresh.addEventListener('mouseenter', (e) => {
                    barTooltip.innerHTML = `
                        <span class="tt-month">${fresh.getAttribute('data-label')}</span>
                        <span class="tt-value">₾${fresh.getAttribute('data-value')}</span>
                    `;
                    barTooltip.style.display = 'flex';
                    moveBarTooltip(e);
                });
                fresh.addEventListener('mousemove', moveBarTooltip);
                fresh.addEventListener('mouseleave', () => {
                    barTooltip.style.display = 'none';
                });
            });
        });

    } catch (err) {
        emptyEl.textContent = `Failed to load chart: ${err.message}`;
    }
}

// ── Transactions Table ─────────────────────────────────────
let _allTransactions = [];
let _sortCol = 'date';   // 'date' | 'amount'
let _sortDir = 'desc';   // 'asc'  | 'desc'

function sortRows(rows) {
    return [...rows].sort((a, b) => {
        let va, vb;
        if (_sortCol === 'date') {
            va = a['თარიღი'] ? new Date(a['თარიღი']).getTime() : 0;
            vb = b['თარიღი'] ? new Date(b['თარიღი']).getTime() : 0;
        } else {
            va = typeof a.GEL === 'number' ? a.GEL : 0;
            vb = typeof b.GEL === 'number' ? b.GEL : 0;
        }
        return _sortDir === 'asc' ? va - vb : vb - va;
    });
}

function updateSortHeaders() {
    ['date', 'amount'].forEach(col => {
        const th    = document.getElementById(`th-${col}`);
        const arrow = th.querySelector('.sort-arrow');
        if (col === _sortCol) {
            th.classList.add('sort-active');
            arrow.textContent = _sortDir === 'asc' ? '↑' : '↓';
        } else {
            th.classList.remove('sort-active');
            arrow.textContent = '';
        }
    });
}

function applyTransactionFilters() {
    if (!_allTransactions.length) return;

    const query      = document.getElementById('transactions-search').value.trim().toLowerCase();
    const dateFrom   = document.getElementById('filter-date-from').value;
    const dateTo     = document.getElementById('filter-date-to').value;
    const merchant   = document.getElementById('filter-merchant').value;
    const amountMin  = parseFloat(document.getElementById('filter-amount-min').value);
    const amountMax  = parseFloat(document.getElementById('filter-amount-max').value);

    const fromMs = dateFrom ? new Date(dateFrom).getTime() : -Infinity;
    const toMs   = dateTo   ? new Date(dateTo + 'T23:59:59').getTime() : Infinity;

    const filtered = _allTransactions.filter(r => {
        const rowMs = r['თარიღი'] ? new Date(r['თარიღი']).getTime() : 0;
        const gel   = typeof r.GEL === 'number' ? r.GEL : 0;

        if (query && !(
            (r.transaction_object || '').toLowerCase().includes(query) ||
            (r.category || '').toLowerCase().includes(query)
        )) return false;

        if (merchant && (r.transaction_object || '') !== merchant) return false;
        if (rowMs < fromMs || rowMs > toMs) return false;
        if (!isNaN(amountMin) && gel < amountMin) return false;
        if (!isNaN(amountMax) && gel > amountMax) return false;

        return true;
    });

    renderTransactionsTable(sortRows(filtered));
}

function renderTransactionsTable(rows) {
    const tbody   = document.getElementById('transactions-tbody');
    const countEl = document.getElementById('transactions-count');

    if (!rows.length) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;color:#999;padding:24px;">No matching payments</td></tr>`;
        countEl.textContent = '0 payments';
        return;
    }

    tbody.innerHTML = rows.map(r => {
        const raw  = r['თარიღი'];
        const date = raw
            ? new Date(raw).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
            : '—';
        const merchant = r.transaction_object || '—';
        const category = r.category || '—';
        const amount   = typeof r.GEL === 'number' ? r.GEL.toFixed(2) : '—';
        return `<tr>
            <td>${date}</td>
            <td>${merchant}</td>
            <td>${category}</td>
            <td class="amount-cell">₾${amount}</td>
        </tr>`;
    }).join('');

    countEl.textContent = `${rows.length} payment${rows.length !== 1 ? 's' : ''}`;
}

async function loadTransactionsTable(paymentsId) {
    const emptyEl   = document.getElementById('transactions-empty');
    const wrapperEl = document.getElementById('transactions-wrapper');
    const countEl   = document.getElementById('transactions-count');

    try {
        const res = await fetch(`${API_BASE}/transactions?dataset_id=${paymentsId}`);
        if (!res.ok) throw new Error(`Server error ${res.status}`);

        const records = await res.json();
        _allTransactions = records;

        if (!records.length) {
            emptyEl.textContent = 'No payments found in the uploaded file.';
            return;
        }

        // Pre-fill date range from actual data
        const dates = records.map(r => r['თარიღი']).filter(Boolean).map(d => d.slice(0, 10)).sort();
        if (dates.length) {
            document.getElementById('filter-date-from').value = dates[0];
            document.getElementById('filter-date-to').value   = dates[dates.length - 1];
        }

        // Populate merchant dropdown with sorted unique values
        const merchants = [...new Set(records.map(r => r.transaction_object).filter(Boolean))].sort();
        const select = document.getElementById('filter-merchant');
        select.innerHTML = '<option value="">All merchants</option>' +
            merchants.map(m => `<option value="${m}">${m}</option>`).join('');

        emptyEl.style.display = 'none';
        wrapperEl.style.display = 'block';
        countEl.style.display = 'block';

        updateSortHeaders();
        renderTransactionsTable(sortRows(records));

    } catch (err) {
        emptyEl.textContent = `Failed to load payments: ${err.message}`;
    }
}

// Filter inputs
['transactions-search', 'filter-date-from', 'filter-date-to', 'filter-merchant', 'filter-amount-min', 'filter-amount-max']
    .forEach(id => document.getElementById(id).addEventListener('input', applyTransactionFilters));

// Sort headers
['date', 'amount'].forEach(col => {
    document.getElementById(`th-${col}`).addEventListener('click', () => {
        if (_sortCol === col) {
            _sortDir = _sortDir === 'asc' ? 'desc' : 'asc';
        } else {
            _sortCol = col;
            _sortDir = col === 'date' ? 'desc' : 'desc';
        }
        updateSortHeaders();
        applyTransactionFilters();
    });
});

document.getElementById('filter-reset').addEventListener('click', () => {
    document.getElementById('transactions-search').value = '';
    document.getElementById('filter-merchant').value     = '';
    document.getElementById('filter-amount-min').value  = '';
    document.getElementById('filter-amount-max').value  = '';

    const dates = _allTransactions.map(r => r['თარიღი']).filter(Boolean).map(d => d.slice(0, 10)).sort();
    if (dates.length) {
        document.getElementById('filter-date-from').value = dates[0];
        document.getElementById('filter-date-to').value   = dates[dates.length - 1];
    }

    _sortCol = 'date';
    _sortDir = 'desc';
    updateSortHeaders();
    renderTransactionsTable(sortRows(_allTransactions));
});

// ── Spending Pace Warning ──────────────────────────────────
async function loadSpentSoFarWarning(paymentsId) {
    const card = document.getElementById('spending-warning-card');
    const textEl = document.getElementById('spending-warning-text');
    const iconEl = document.getElementById('spending-warning-icon');
    try {
        const res = await fetch(`${API_BASE}/main-insights/spent-so-far-warning?dataset_id=${paymentsId}`);
        if (!res.ok) throw new Error(`Server error ${res.status}`);
        const data = await res.json();
        const isWarning = data.message.includes('may exceed');
        iconEl.src = isWarning ? 'src/icons/warning.png' : 'src/icons/happy.png';
        iconEl.alt = isWarning ? 'Warning' : 'On track';
        textEl.textContent = data.message;
        card.style.display = 'flex';
    } catch (err) {
        card.style.display = 'none';
    }
}

// ── Monthly Spending Prediction ────────────────────────────
async function loadMonthlySpendingPrediction(paymentsId) {
    const card = document.getElementById('spending-prediction-card');
    const textEl = document.getElementById('spending-prediction-text');
    try {
        const res = await fetch(`${API_BASE}/main-insights/monthly-spending-prediction?dataset_id=${paymentsId}`);
        if (!res.ok) throw new Error(`Server error ${res.status}`);
        const data = await res.json();
        textEl.textContent = data.message;
        card.style.display = 'block';
    } catch (err) {
        card.style.display = 'none';
    }
}

// ── Upload ─────────────────────────────────────────────────
fileInput.addEventListener('change', async() => {
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    uploadBtn.disabled = true;
    uploadBtn.textContent = 'Uploading…';
    statusEl.className = 'upload-status';
    statusEl.textContent = '';

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
        window._paymentsId = uploadData.payments_id;

        statusEl.className = 'upload-status upload-status--success';
        statusEl.textContent = `✓ "${file.name}" uploaded successfully`;
        uploadBtn.textContent = file.name;

        loadExpenseBreakdown(uploadData.payments_id);
        loadSpentSoFarWarning(uploadData.payments_id);
        loadSpendingOverTime(uploadData.payments_id);
        loadMonthlySpendingPrediction(uploadData.payments_id);
        loadTopMerchants(uploadData.payments_id);
        loadTopMerchant(uploadData.payments_id);
        loadBiggestPurchase(uploadData.payments_id);
        loadTotals(uploadData.payments_id);
        loadFrequency(uploadData.payments_id);
        loadMerchantLastTransactions(uploadData.payments_id);
        loadAvgSpendingByDay(uploadData.payments_id);
        loadTransactionsTable(uploadData.payments_id);

    } catch (err) {
        statusEl.className = 'upload-status upload-status--error';
        statusEl.textContent = `✗ Upload failed: ${err.message}`;
        uploadBtn.textContent = 'Upload file';
    } finally {
        uploadBtn.disabled = false;
        fileInput.value = '';
    }
});