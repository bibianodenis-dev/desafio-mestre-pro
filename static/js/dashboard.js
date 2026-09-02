/**
 * DASHBOARD & CHARTS CONTROLLER - QUIZ CONCURSOS
 * Powered by Chart.js 4.x
 */

document.addEventListener('DOMContentLoaded', function () {
    // Render Dashboard Charts if canvas elements exist
    initDashboardCharts();
});

function initDashboardCharts() {
    // 1. Gráfico Geral: Acertos x Erros (Doughnut)
    const ctxGeral = document.getElementById('chartAcertosErrosGeral');
    if (ctxGeral && window.dashboardData) {
        const data = window.dashboardData;
        new Chart(ctxGeral, {
            type: 'doughnut',
            data: {
                labels: ['Acertos', 'Erros'],
                datasets: [{
                    data: [data.total_acertos, data.total_erros],
                    backgroundColor: ['#10b981', '#ef4444'],
                    borderWidth: 3,
                    borderColor: '#ffffff',
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: { family: 'Plus Jakarta Sans', size: 13, weight: '600' },
                            padding: 16
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const value = context.raw;
                                const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                                return ` ${context.label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                },
                cutout: '70%'
            }
        });
    }

    // 2. Gráfico por Subtema: % de Acerto (Bar Chart)
    const ctxSubtemas = document.getElementById('chartSubtemas');
    if (ctxSubtemas && window.dashboardData && window.dashboardData.subtemas_stats) {
        const subtemasStats = window.dashboardData.subtemas_stats;
        const labels = subtemasStats.map(s => s.subtema);
        const percentualData = subtemasStats.map(s => s.percentual_acerto);
        const backgroundColors = percentualData.map(val => val >= 70 ? '#10b981' : val >= 50 ? '#f59e0b' : '#ef4444');

        new Chart(ctxSubtemas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: '% de Acerto',
                    data: percentualData,
                    backgroundColor: backgroundColors,
                    borderRadius: 8,
                    maxBarThickness: 40
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: value => value + '%',
                            font: { family: 'Plus Jakarta Sans', size: 12 }
                        },
                        grid: { color: 'rgba(226, 232, 240, 0.6)' }
                    },
                    x: {
                        ticks: {
                            font: { family: 'Plus Jakarta Sans', size: 11, weight: '500' },
                            maxRotation: 45,
                            minRotation: 0
                        },
                        grid: { display: false }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return ` Aproveitamento: ${context.raw}%`;
                            }
                        }
                    }
                }
            }
        });
    }

    // 3. Gráfico de Evolução Histórica (Line Chart)
    const ctxEvolucao = document.getElementById('chartEvolucaoHistorica');
    if (ctxEvolucao && window.dashboardData && window.dashboardData.historico) {
        const historico = window.dashboardData.historico;
        const labels = historico.map(h => h.data);
        const dataAcertos = historico.map(h => h.acerto_cumulativo_pct);

        new Chart(ctxEvolucao, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Aproveitamento Acumulado (%)',
                    data: dataAcertos,
                    borderColor: '#4f46e5',
                    backgroundColor: 'rgba(79, 70, 229, 0.1)',
                    fill: true,
                    tension: 0.3,
                    pointBackgroundColor: '#4f46e5',
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { callback: v => v + '%' }
                    },
                    x: {
                        grid: { display: false }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    // 4. Gráfico Tempo Médio por Tema (Horizontal Bar Chart)
    const ctxTempo = document.getElementById('chartTempoMedioTema');
    if (ctxTempo && window.dashboardData && window.dashboardData.temas_stats) {
        const temasStats = window.dashboardData.temas_stats;
        const labels = temasStats.map(t => t.tema);
        const tempoData = temasStats.map(t => t.tempo_medio);

        new Chart(ctxTempo, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Tempo Médio (segundos)',
                    data: tempoData,
                    backgroundColor: '#06b6d4',
                    borderRadius: 6,
                    maxBarThickness: 30
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: { callback: v => v + 's' }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    // 5. Pizza de Acertos por Tema
    const ctxAcertosTema = document.getElementById('chartAcertosPorTema');
    if (ctxAcertosTema && window.dashboardData && window.dashboardData.temas_stats) {
        const temasStats = window.dashboardData.temas_stats;
        const labels = temasStats.map(t => t.tema);
        const acertosData = temasStats.map(t => t.total_acertos);
        
        const colors = [
            '#4f46e5', '#06b6d4', '#10b981', '#f59e0b', 
            '#ec4899', '#8b5cf6', '#3b82f6', '#64748b'
        ];

        new Chart(ctxAcertosTema, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: acertosData,
                    backgroundColor: colors.slice(0, labels.length)
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'right' }
                }
            }
        });
    }
}
