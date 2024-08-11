let displayedFiles = 0;
const filesPerPage = 5;

function updateFileList() {
    $('#loading-files').show();
    $.getJSON('/monitor', function (data) {
        $('#loading-files').hide();
        console.log('File list updated:', data); 
        var fileList = $('#file-list');
        fileList.empty();
        displayedFiles = 0;

        data.sort((a, b) => new Date(b.last_sent) - new Date(a.last_sent));

        displayFiles(data);
    }).fail(function(jqXHR, textStatus, errorThrown) {
        $('#loading-files').hide();
        console.error('Failed to update file list:', textStatus, errorThrown); 
    });
}

function displayFiles(data) {
    const fileList = $('#file-list');
    const loadMoreButton = $('#load-more');

    for (let i = displayedFiles; i < displayedFiles + filesPerPage && i < data.length; i++) {
        const file = data[i];
        var fileInfo = $('<p>');

        fileInfo.text(`[${file.file_id}] ${file.last_sent} - ${file.file_path}`);

        if (file.send_success) {
            fileInfo.append(' (Sent successfully)');
            if (file.forward_success) {
                fileInfo.append(' (Forwarded successfully)');
            }
        } else {
            fileInfo.append(' (Error sending)');
        }
        if (file.encrypted) {
            fileInfo.append(' (Encrypted)');
        }
        fileInfo.append($('<a>').attr('href', '/download/' + file.file_id).text(' Download'));
        fileList.append(fileInfo);
    }

    displayedFiles += filesPerPage;

    if (displayedFiles < data.length) {
        loadMoreButton.show();
    } else {
        loadMoreButton.hide();
    }
}

function updateChartData() {
    $('#loading-stats').show();
    $.getJSON('/monitor', function (data) {
        $('#loading-stats').hide();
        // Process data to extract relevant statistics
        let processedFiles = data.length;
        let sentFiles = data.filter(file => file.send_success).length;
        let totalUploadedData = 0;
        let totalProcessingTime = 0;
        let totalUploadTime = 0; 

        data.forEach(function (file) {
            totalUploadedData += file.file_size || 0;
            totalProcessingTime += file.processing_time || 0;
            totalUploadTime += (file.file_size || 0) / (file.upload_speed || 1); 
        });

        // Calculate average upload speed in MB/s
        let averageUploadSpeed = (totalUploadedData / (totalUploadTime || 1)) / 1024 / 1024;

        // Calculate average processing time in seconds
        let averageProcessingTime = (totalProcessingTime / (data.length || 1)) / 1000; 

        // Convert total uploaded data to MB or GB
        let totalUploadedDataSize = totalUploadedData / 1024 / 1024; // MB
        let totalUploadedDataSizeUnit = "MB";
        if (totalUploadedDataSize > 1024) {
            totalUploadedDataSize /= 1024; // GB
            totalUploadedDataSizeUnit = "GB";
        }

        // Update the chart with the new data
        myChart.data.datasets[0].data = [
            processedFiles,
            sentFiles,
            averageUploadSpeed,
            averageProcessingTime,
            totalUploadedDataSize
        ];

        // Update the chart labels to reflect the units
        myChart.data.labels = [
            'Processed Files',
            'Sent Files',
            'Avg. Upload Speed (MB/s)',
            'Avg. Processing Time (s)',
            'Total Uploaded Data (' + totalUploadedDataSizeUnit + ')'
        ];

        myChart.update();
    }).fail(function(jqXHR, textStatus, errorThrown) {
        $('#loading-stats').hide();
        console.error('Failed to update stats:', textStatus, errorThrown); // Debug message
    });
}

const ctx = document.getElementById('statisticsChart').getContext('2d');
const myChart = new Chart(ctx, {
    type: 'bar', 
    data: {
        labels: [
            'Processed Files',
            'Sent Files',
            'Avg. Upload Speed (MB/s)',
            'Avg. Processing Time (s)',
            'Total Uploaded Data (MB)'
        ],
        datasets: [{
            label: 'File Statistics',
            data: [0, 0, 0, 0, 0], 
            backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)',
                'rgba(75, 192, 192, 0.2)',
                'rgba(153, 102, 255, 0.2)'
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)'
            ],
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        },
        onHover: (event, chartElement) => {
            event.native.target.style.cursor = chartElement.length ? 'pointer' : 'default';
        },
        plugins: {
            tooltip: {
                mode: 'nearest',
                intersect: false 
            }
        }
    }
});

// API Statistics Chart
const apiCtx = document.getElementById('apiStatisticsChart').getContext('2d');
const apiChart = new Chart(apiCtx, {
    type: 'line',
    data: {
        labels: [], // Time labels
        datasets: [{
            label: 'Requests per Second',
            data: [],
            borderColor: 'rgba(75, 192, 192, 1)',
            fill: false
        },
        {
            label: 'Average Response Time (ms)',
            data: [],
            borderColor: 'rgba(255, 206, 86, 1)',
            fill: false
        },
        {
            label: 'Errors per Second',
            data: [],
            borderColor: 'rgba(255, 99, 132, 1)',
            fill: false
        }]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

function updateApiChartData() {
    $('#loading-api-stats').show();
    $.getJSON('/api_stats', function (data) {
        $('#loading-api-stats').hide();
        apiChart.data.labels.push(new Date().toLocaleTimeString());
        apiChart.data.datasets[0].data.push(data.requestsPerSecond);
        apiChart.data.datasets[1].data.push(data.averageResponseTime);
        apiChart.data.datasets[2].data.push(data.errorsPerSecond);

        // Limit the number of data points displayed
        if (apiChart.data.labels.length > 10) {
            apiChart.data.labels.shift();
            apiChart.data.datasets.forEach(dataset => {
                dataset.data.shift();
            });
        }

        apiChart.update();
    }).fail(function(jqXHR, textStatus, errorThrown) {
        $('#loading-api-stats').hide();
        console.error('Failed to update API stats:', textStatus, errorThrown); // Debug message
    });
}

$('#load-more').click(function() {
    $.getJSON('/monitor', function(data) {
        data.sort((a, b) => new Date(b.last_sent) - new Date(a.last_sent));
        displayFiles(data);
    });
});

$('#clear-logs').click(function() {
    $.post('/clear_logs', function(data) {
        alert(data);
    });
});

$('#clear-json-data').click(function() {
    $.post('/clear_json_data', function(data) {
        alert(data);
        updateFileList(); 
        updateChartData();
        updateApiChartData();
    });
});

$(document).ready(function() {
    updateFileList();
    updateChartData();
    updateApiChartData();
    setInterval(updateFileList, 5000);
    setInterval(updateChartData, 5000);
    setInterval(updateApiChartData, 5000);
});