function downloadChart(canvasId) {
    var canvas = document.getElementById(canvasId);
    var image = canvas.toDataURL("image/png").replace("image/png", "image/octet-stream");
    var link = document.createElement('a');
    link.download = 'chart.png';
    link.href = image;
    link.click();
}

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

function exportTableToCSV(filename) {
    var csv = tableToCSV(document.getElementById('loans-table'));
    downloadCSV(csv, filename);
}

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

function getRandomColor() {
    var r = Math.floor(Math.random() * 256);
    var g = Math.floor(Math.random() * 256);
    var b = Math.floor(Math.random() * 256);
    return 'rgba(' + r + ', ' + g + ', ' + b + ', 1)';
}

window.onload = function() {
    fetch('scripts/fetch_data.php')
        .then(response => response.json())
        .then(data => {
            // ... existing code ...
        });
};

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