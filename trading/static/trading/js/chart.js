export function createChart(canvasId) {
    const ctx = document.getElementById(canvasId).getContext('2d');

    // Gradient fill for the area under the line
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(0, 0, 0, 0.2)');
    gradient.addColorStop(1, 'rgba(0, 0, 0, 0.05)');

    const initialData = {
        labels: [], // Dates will be populated dynamically
        datasets: [
            {
                label: 'Price',
                data: [], // Price data
                borderColor: '#000000',
                backgroundColor: gradient,
                fill: true,
                tension: 0.2,
                borderWidth: 2,
                pointRadius: 0,
                pointHoverRadius: 6,
                pointBackgroundColor: '#FFFFFF',
                pointHoverBackgroundColor: '#FFFFFF',
            }
        ]
    };

    const chartConfig = {
        type: 'line',
        data: initialData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false, // Hide legend since we only have one dataset
                },
                tooltip: {
                    mode: 'nearest',
                    intersect: false,
                    callbacks: {
                        title: (tooltipItems) => {
                            return `Date: ${tooltipItems[0].label}`;
                        },
                        label: (tooltipItem) => {
                            const datasetIndex = tooltipItem.datasetIndex;
                            const value = tooltipItem.raw;
                            const index = tooltipItem.dataIndex;
                            const volume = tooltipItem.chart.data.datasets[0].metaVolume[index];
                            const percentChange = tooltipItem.chart.data.datasets[0].metaPercentChange[index];

                            if (datasetIndex === 0) {
                                return [
                                    `Price: $${value.toFixed(2)}`,
                                    `Percent Change: ${percentChange.toFixed(2)}%`,
                                    `Volume: ${volume}`,
                                ];
                            }
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true, // Ensure x-axis is displayed
                    title: {
                        display: true,
                        text: 'Date',
                        color: '#000000',
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    },
                    ticks: {
                        display: true, // Ensure ticks are displayed
                        color: '#000000',
                        font: {
                            size: 11
                        },
                        maxRotation: 45, // Rotate labels for better readability
                        minRotation: 45
                    },
                    grid: {
                        display: true,
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                y: {
                    display: true, // Ensure y-axis is displayed
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Price ($)',
                        color: '#000000',
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    },
                    ticks: {
                        display: true, // Ensure ticks are displayed
                        color: '#000000',
                        font: {
                            size: 11
                        },
                        callback: function(value) {
                            return '$' + value.toFixed(2);
                        }
                    },
                    grid: {
                        display: true,
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                }
            },
            hover: {
                mode: 'nearest',
                intersect: false,
            }
        }
    };

    return new Chart(ctx, chartConfig);
}