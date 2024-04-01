/**
 * Downloads a chart as a PNG image.
 *
 * @param {string} canvasId - The ID of the canvas element containing the chart.
 */
function downloadChart(canvasId) {
    var canvas = document.getElementById(canvasId);
    var image = canvas.toDataURL("image/png").replace("image/png", "image/octet-stream");
    var link = document.createElement('a');
    link.download = 'chart.png';
    link.href = image;
    link.click();
}

/**
 * Converts a table to a CSV string.
 *
 * @param {HTMLTableElement} table - The table to convert.
 * @returns {string} The CSV string.
 */
function tableToCSV(table) {
    var rows = [];
    for (var i = 0, len = table.rows.length; i < len; i++) {
        var row = table.rows[i];
        var cells = [];
        for (var j = 0, len2 = row.cells.length; j < len2; j++) {
            cells.push(row.cells[j].innerText);
        }
        rows.push(cells.join(','));
    }
    return rows.join('\n');
}

/**
 * Exports a table to a CSV file.
 *
 * @param {string} filename - The name of the file to export to.
 */
function exportTableToCSV(filename) {
    var csv = tableToCSV(document.getElementById('loans-table'));
    downloadCSV(csv, filename);
}

// Define a color palette
var colorPalette = [
    'rgba(255, 99, 132, 1)',  // red
    'rgba(54, 162, 235, 1)',  // blue
    'rgba(255, 206, 86, 1)',  // yellow
    'rgba(75, 192, 192, 1)',  // green
    'rgba(153, 102, 255, 1)',  // purple
    'rgba(255, 159, 64, 1)'   // orange
];

// Function to get the next color from the palette
var colorIndex = 0;
function getNextColor() {
    var color = colorPalette[colorIndex];
    colorIndex = (colorIndex + 1) % colorPalette.length;
    return color;
}

/**
 * Downloads a CSV file.
 *
 * @param {string} csv - The CSV data.
 * @param {string} filename - The name of the file to download.
 */
function downloadCSV(csv, filename) {
    var csvFile;
    var downloadLink;
    csvFile = new Blob([csv], {type: "text/csv"});
    downloadLink = document.createElement("a");
    downloadLink.download = filename;
    downloadLink.href = window.URL.createObjectURL(csvFile);
    downloadLink.style.display = "none";
    document.body.appendChild(downloadLink);
    downloadLink.click();
}

/**
 * Fetches data from the server when the window loads.
 */
window.onload = function() {
    fetch('scripts/fetch_data.php')
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Loans issued and repayments made chart
        new Chart(document.getElementById('loansChart'), {
        type: 'line',
        data: {
            labels: data[0].map(item => item.month),
            datasets: [
                {
                    label: 'Total Loans',
                    data: data[0].map(item => item.total_loans),
                    borderColor: getNextColor(),
                    fill: false
                },
                {
                    label: 'Total Repayments',
                    data: data[0].map(item => item.total_repayments),
                    borderColor: getNextColor(),
                    fill: false
                }
            ]
        },
        // ... rest of the chart options
        });

        // Top borrowers chart
        new Chart(document.getElementById('top-borrowers-chart'), {
            type: 'pie',
            data: {
                labels: data[2].map(item => item.borrower),
                datasets: [{
                    label: 'Total Loans',
                    data: data[2].map(item => item.total),
                    backgroundColor: data[2].map(() => getNextColor()),
                    borderColor: data[2].map(() => getNextColor()),
                    borderWidth: 1
                }]
            },
            // ... rest of the chart options
        });

        // Default loans chart
        new Chart(document.getElementById('arrears-chart'), {
            type: 'line',
            data: {
                labels: data[1].map(item => item.month),
                datasets: [{
                    label: 'Default Loans',
                    data: data[1].map(item => item.total_loans),
                    borderColor: getNextColor(),
                    fill: false
                }]
            },
            // ... rest of the chart options
        });

        // Populate the table
        var tableBody = document.getElementById('loans-table').getElementsByTagName('tbody')[0];
        data[3].forEach(item => {
        var row = tableBody.insertRow();
        row.insertCell().innerText = item.loan_num;
        row.insertCell().innerText = item.borrower;
        row.insertCell().innerText = item.loan_status;
        row.insertCell().innerText = item.loan_date;
        row.insertCell().innerText = item.due_date;
        row.insertCell().innerText = item.loan_amount;
        row.insertCell().innerText = item.total_penalties;
        row.insertCell().innerText = item.loan_balance;
    });

    })
    .catch(error => {
        console.error('There has been a problem with your fetch operation:', error);
    });
};

/**
 * Filters table rows based on the search input.
 */
document.getElementById('search-input').addEventListener('keyup', function() {
    var searchValue = this.value.toLowerCase();
    var tableRows = document.getElementById('loans-table').getElementsByTagName('tbody')[0].rows;
    for (var i = 0; i < tableRows.length; i++) {
        var cells = tableRows[i].cells;
        var match = false;
        for (var j = 0; j < cells.length; j++) {
            if (cells[j].innerText.toLowerCase().includes(searchValue)) {
                match = true;
                break;
            }
        }
        tableRows[i].style.display = match ? '' : 'none';
    }
});