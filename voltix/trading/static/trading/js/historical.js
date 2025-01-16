import { createChart } from './chart.js';

document.addEventListener('DOMContentLoaded', () => {
    const myChart = createChart('myChart');
    const messageDiv = document.getElementById('message');
    const chartDiv = document.querySelector('.chart');
    const dateDiv = document.querySelector('.date-div');
    const afterDate = document.querySelector('.after-date');
    const selectDateBtn = document.querySelector('#select-date-btn');
    const startBtn = document.querySelector('#start-btn');
    const backArrow = document.querySelector('#back-arrow');
    const csrftoken = document.querySelector('[name=csrf-token]').content;

    // Input elements
    const startDateInput = document.querySelector('#start-date');
    const endDateInput = document.querySelector('#end-date');
    const initialCapitalInput = document.querySelector('#initial-capital');
    const feeInput = document.querySelector('#fee');
    const riskInput = document.querySelector('#risk');
    const strategyInput = document.querySelector('#strategy');

    // Ticker and Percent Change Elements
    const percentChangeElement = document.querySelector('#percent-change');
    const percentChange = parseFloat(percentChangeElement.textContent);
    const color = percentChange < 0 ? '#FF506A' : '#08F6B5';
    const elementsToColor = ['#percent-change', '#price', '#change', '#arrow'];

    // Initialize Arrow Symbol
    const arrowElement = document.querySelector('#arrow');
    arrowElement.textContent = percentChange > 0 ? '↑' : '↓';

    // Update colors for relevant elements
    updateElementColors(elementsToColor, color);

    // Event Listeners
    backArrow.addEventListener('click', handleBackArrowClick);
    selectDateBtn.addEventListener('click', handleSelectDateClick);
    startBtn.addEventListener('click', handleStartBtnClick);

    // Function to update the chart with real data
    function updateChart(data) {
        console.log('Updating chart with data:', data); 
        myChart.data.labels = data.dates;
        myChart.data.datasets[0].data = data.close_prices;
        myChart.data.datasets[0].metaVolume = data.volumes;
        myChart.data.datasets[0].metaPercentChange = data.percent_changes;
        myChart.update();
    }

    // Function to handle back arrow click
    function handleBackArrowClick(event) {
        event.preventDefault();
        dateDiv.style.display = 'block';
        afterDate.classList.remove('show');
        selectDateBtn.style.display = 'block';
        startBtn.style.display = 'none';
    }

    // Function to handle select date button click
    function handleSelectDateClick(event) {
        event.preventDefault();
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;
        const symbol = document.querySelector('#ticker').textContent;

        if (startDate && endDate) {
            fetchData(`/trading/api/stock-data/?symbol=${symbol}&start_date=${startDate}&end_date=${endDate}`, updateChart);
            messageDiv.style.display = 'none';
        } else {
            showMessage('Please select a start and end date');
        }
    }

    // Function to handle start button click
    function handleStartBtnClick(event) {
        event.preventDefault();
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;
        fetchSimulationData(startDate, endDate);
    }

    // Fetch data from an API and update chart
    function fetchData(url, callback) {
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    showMessage(data.message);
                } else if (data.error) {
                    showMessage(`Error: ${data.error}`);
                } else {
                    chartDiv.classList.add('show');
                    dateDiv.style.display = 'none';
                    afterDate.classList.add('show');
                    selectDateBtn.style.display = 'none';
                    startBtn.style.display = 'block';
                    callback(data);
                }
            })
            .catch(error => {
                console.error('Error fetching data:', error);
                showMessage(`Error fetching data: ${error.message}`);
            });
    }

    // Fetch simulation data
    function fetchSimulationData(startDate, endDate) {
        const initialCapital = initialCapitalInput.value;
        const fee = feeInput.value;
        const risk = riskInput.value;
        const strategy = strategyInput.value;
        const symbol = document.querySelector('#ticker').textContent;

        if (initialCapital && fee && risk && strategy) {
            fetch(`/trading/api/simulation/?symbol=${symbol}&start_date=${startDate}&end_date=${endDate}&intial_capital=${initialCapital}&fee=${fee}&risk=${risk}&strategy=${strategy}` , {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify({
                    symbol, start_date: startDate, end_date: endDate,
                    initial_capital: initialCapital, fee, risk, strategy
                })
            })
            .then(response => response.json())
            .then(data => console.log('Strategy data:', data))
            .catch(error => console.error('Error fetching strategy data:', error));
        } else {
            showMessage('Please fill all the fields');
        }
    }

    // Show message in the message div
    function showMessage(message) {
        messageDiv.textContent = message;
        messageDiv.style.display = 'block';
    }

    // Update the color of multiple elements
    function updateElementColors(selectors, color) {
        selectors.forEach(selector => {
            const element = document.querySelector(selector);
            if (element) {
                element.style.color = color;
            }
        });
    }
});
