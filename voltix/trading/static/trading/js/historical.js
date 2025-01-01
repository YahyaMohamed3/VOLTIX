import { createChart } from './chart.js';

document.addEventListener('DOMContentLoaded', () => {
    const myChart = createChart('myChart');
    const percentChangeElement = document.querySelector('#percent-change');
    const percentChange = parseFloat(percentChangeElement.textContent);
    const color = percentChange < 0 ? '#FF506A' : '#08F6B5';
    const elementsToColor = ['#percent-change', '#price', '#change', '#arrow'];

    elementsToColor.forEach(selector => {
        document.querySelector(selector).style.color = color;
    });

    const arrowElement = document.querySelector('#arrow');
    arrowElement.textContent = percentChange > 0 ? '↑' : '↓';

    const startDateInput = document.querySelector('#start-date');
    const endDateInput = document.querySelector('#end-date');
    const selectDateBtn = document.querySelector('#select-date-btn');


    selectDateBtn.addEventListener('click', (event) => {
        event.preventDefault();
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;
        const symbol = document.querySelector('#ticker').textContent;
        const chartDiv = document.querySelector('.chart');


        if (startDate && endDate) {
            fetch(`/trading/api/stock-data/?symbol=${symbol}&start_date=${startDate}&end_date=${endDate}`)
                .then(response => response.json())
                .then(data => {
                    
                    // Check for message or error and display it
                    if (data.message) {
                        messageDiv.textContent = data.message;
                        messageDiv.style.backgroundColor = '#f0f8ff'; // Light blue background for informational message
                        messageDiv.style.display = 'block';  // Show the message div
                    } else if (data.error) {
                        messageDiv.textContent = `Error: ${data.error}`;
                        messageDiv.style.backgroundColor = '#f8d7da'; // Light red background for error message
                        messageDiv.style.display = 'block';  // Show the message div
                    }

                    chartDiv.classList.add('show');
                    updateChart(data);
                })
                .catch(error => {
                    console.error('Error fetching data:', error);
                    messageDiv.textContent = `Error fetching data: ${error.message}`;
                    messageDiv.style.backgroundColor = '#f8d7da'; // Light red background for error message
                    messageDiv.style.display = 'block';  // Show the message div
                });
        }
    });

     // Function to update the chart with real data
     function updateChart(data) {
        console.log('Updating chart with data:', data); // Debugging: log the data being used to update the chart
        myChart.data.labels = data.dates;
        myChart.data.datasets[0].data = data.close_prices;
        myChart.data.datasets[0].metaVolume = data.volumes;
        myChart.data.datasets[0].metaPercentChange = data.percent_changes;
        myChart.update();
    }
});
