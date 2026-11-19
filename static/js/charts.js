// ===== Интерактивные графики статистики (Chart.js) =====

const ACCENT = '#4f6df5';
const PALETTE = ['#4f6df5', '#2fb673', '#f5a623', '#e04f5f', '#8b5cf6', '#14b8a6', '#f472b6'];

function formatMoney(value) {
    return value.toLocaleString('ru-RU') + ' ₽';
}

Chart.defaults.font.family = "'Inter', 'Segoe UI', Arial, sans-serif";
Chart.defaults.color = '#6b7280';

const data = window.chartData;

// --- Столбчатая диаграмма: траты по категориям ---
new Chart(document.getElementById('chart-categories'), {
    type: 'bar',
    data: {
        labels: data.categories,
        datasets: [{
            label: 'Траты',
            data: data.category_amounts,
            backgroundColor: ACCENT,
            hoverBackgroundColor: '#3d54c4',
            borderRadius: 8,
            maxBarThickness: 60,
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: { display: false },
            title: {
                display: true,
                text: 'Траты по категориям',
                color: '#2c3244',
                font: { size: 14, weight: 'bold' },
            },
            tooltip: {
                callbacks: {
                    label: ctx => ' ' + formatMoney(ctx.parsed.y),
                },
            },
        },
        scales: {
            y: {
                ticks: { callback: value => formatMoney(value) },
                grid: { color: '#eef0f4' },
            },
            x: { grid: { display: false } },
        },
    }
});

// --- Кольцевая диаграмма: доля карт ---
const totalCards = data.card_amounts.reduce((sum, v) => sum + v, 0);

new Chart(document.getElementById('chart-cards'), {
    type: 'doughnut',
    data: {
        labels: data.cards,
        datasets: [{
            data: data.card_amounts,
            backgroundColor: PALETTE,
            borderColor: '#ffffff',
            borderWidth: 2,
            hoverOffset: 10,
        }]
    },
    options: {
        responsive: true,
        cutout: '55%',
        plugins: {
            legend: { position: 'bottom' },
            title: {
                display: true,
                text: 'Доля карт в общих тратах',
                color: '#2c3244',
                font: { size: 14, weight: 'bold' },
            },
            tooltip: {
                callbacks: {
                    label: ctx => {
                        const percent = Math.round(ctx.parsed / totalCards * 100);
                        return ` ${ctx.label}: ${formatMoney(ctx.parsed)} (${percent}%)`;
                    },
                },
            },
        },
    }
});
