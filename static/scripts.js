document.addEventListener("DOMContentLoaded", function() {
    // Fetch the list of files on initial load
    fetch('/files')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const fileListElement = document.getElementById('file-list');
            fileListElement.innerHTML = '';  // Clear any existing content

            if (!data.files || data.files.length === 0) {
                fileListElement.innerHTML = '<p>No readings available.</p>';
                return;
            }

            // Sort files based on their names (assuming they contain timestamps)
            const sortedFiles = data.files.sort((a, b) => {
                const dateA = new Date(a.split('_')[0]); // Adjust this based on your filename format
                const dateB = new Date(b.split('_')[0]);
                return dateB - dateA; // Sort in descending order
            });

            // Display the top 10 files
            const topFiles = sortedFiles.slice(0, 15);

            topFiles.forEach(file => {
                const button = document.createElement('a');
                button.href = '#';
                button.textContent = file;
                button.className = 'file-button';

                // Add click event listener
                button.addEventListener('click', function(event) {
                    event.preventDefault();
                    loadReadings(file);
                });

                fileListElement.appendChild(button);
            });

            // Load readings for the first file by default
            if (topFiles.length > 0) {
                loadReadings(topFiles[0]);
            }
        })
        .catch(error => console.error('Error fetching files:', error));

    let isInitialPoll = true; // Flag to check if it's the initial poll
    const initialPollingInterval = 1000; // Initial check every 1 second
    const subsequentPollingInterval = 3600000; // 1 hour in milliseconds

    // Function to fetch and display the list of files and update the graph
    function fetchFilesAndUpdateGraph() {
        fetch('/files')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (!data.files) {
                    console.error('No files returned.');
                    return;
                }

                const fileListElement = document.getElementById('file-list');
                const currentFiles = Array.from(fileListElement.getElementsByTagName('a')).map(button => button.textContent);

                // Only update if files have changed
                if (JSON.stringify(currentFiles) !== JSON.stringify(data.files)) {
                    fileListElement.innerHTML = ''; // Clear file list before repopulating

                    data.files.forEach(file => {
                        if (!currentFiles.includes(file)) {
                            const button = document.createElement('a');
                            button.href = '#';
                            button.textContent = file;
                            button.className = 'file-button';

                            // Load readings on click
                            button.addEventListener('click', function(event) {
                                event.preventDefault();
                                loadReadings(file);
                            });

                            fileListElement.insertBefore(button, fileListElement.firstChild); // Add at top
                        }
                    });

                    // Load readings for the latest file if necessary
                    if (data.files.length > 0 && currentFiles.length === 0) {
                        loadReadings(data.files[0]); // Load readings for the first file
                    }
                }
            })
            .catch(error => console.error('Error fetching files:', error));
    }

    // Function to load readings from the selected file
    // Function to calculate and display average acceleration
function displayAverageAcceleration(readings) {
    // Calculate average acceleration
    const totalAcceleration = readings.reduce((sum, reading) => sum + reading.acceleration, 0);
    const averageAcceleration = totalAcceleration / readings.length;

    // Update the average number display
    const averageNumberElement = document.getElementById('average-number');
    averageNumberElement.textContent = averageAcceleration.toFixed(2); // Display with two decimal places
}

// Function to load readings from the selected file
function displayAverageSlope(readings) {
    if (readings.length < 2) return; // Need at least two points to calculate slope

    let totalSlope = 0;
    let count = 0;

    for (let i = 1; i < readings.length; i++) {
        const y2 = readings[i].acceleration;
        const y1 = readings[i - 1].acceleration;

        const timeParts1 = readings[i - 1].timestamp.split('-');
        const timeParts2 = readings[i].timestamp.split('-');

        // Convert timestamps to Date objects for time difference calculation
        const time1 = new Date(`1970-01-01T${timeParts1[0]}:${timeParts1[1]}:${timeParts1[2]}`);
        const time2 = new Date(`1970-01-01T${timeParts2[0]}:${timeParts2[1]}:${timeParts2[2]}`);

        const deltaY = y2 - y1;
        const deltaX = (time2 - time1) / 1000; // Convert time difference to seconds

        const slope = deltaY / deltaX;
        totalSlope += slope;
        count++;
    }

    const averageSlope = totalSlope / count;

    // Update the average slope display
    const averageSlopeElement = document.getElementById('average-slope');
    averageSlopeElement.textContent = averageSlope.toFixed(2); // Display with two decimal places
}

async function fetchFileCount() {
    try {
        const response = await fetch('/file_count');
        if (response.ok) {
            const data = await response.json();
            document.getElementById('csv-file-count').textContent = data.file_count;
        } else {
            console.error('Failed to fetch file count:', response.statusText);
        }
    } catch (error) {
        console.error('Error fetching file count:', error);
    }
}

// Fetch the file count every 5 seconds
setInterval(fetchFileCount, 1000);

// Fetch initially to populate the count
fetchFileCount();

async function fetchLatestEvent() {
    try {
        // Fetch the latest event from the endpoint
        const response = await fetch("/latest-event");
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        // Update the display with the latest event
        const displayElement = document.getElementById("latest-event-display");
        displayElement.textContent = data.latest_event || "No events found"; // Handle empty response
    } catch (error) {
        console.error("Error fetching latest event:", error);
        document.getElementById("latest-event-display").textContent = "Error loading event"; // Handle error
    }
}

// Initial fetch to display the latest event
fetchLatestEvent();

// Poll the latest event every 5 seconds for updates
setInterval(fetchLatestEvent, 5000);

document.addEventListener("DOMContentLoaded", () => {
    // Function to fetch and display the latest event
    async function fetchLatestEvent() {
        try {
            // Fetch data from FastAPI endpoint
            const response = await fetch("/latest-event");
            const data = await response.json();
            const displayElement = document.getElementById("latest-event-display");

            // Check for valid response and update the display
            if (data.latest_event) {
                displayElement.innerText = data.latest_event; // Display the latest event name
            } else {
                displayElement.innerText = "No events found"; // Handle empty response
            }
        } catch (error) {
            console.error("Error fetching latest event:", error);
            document.getElementById("latest-event-display").innerText = "Error loading event";
        }
    }

    // Fetch the latest event on page load
    fetchLatestEvent();
});

// Function to load readings from the selected file
function loadReadings(fileName) {
    fetch(`/readings/${fileName}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                console.error(data.error);
                return;
            }

            const readings = data.readings;

            // Call function to display the average acceleration
            displayAverageAcceleration(readings);

            // Call function to display the average slope
            displayAverageSlope(readings);

            // Parse the timestamp and format it to a valid Date object
            const labels = readings.map(reading => {
                const timeParts = reading.timestamp.split('-');
                const hours = timeParts[0];
                const minutes = timeParts[1];
                const seconds = timeParts[2];
                return new Date(`1970-01-01T${hours}:${minutes}:${seconds}`).toISOString(); // Base date used
            });

            const accelerations = readings.map(reading => reading.acceleration);

            const ctx = document.getElementById('graph').getContext('2d');
            // Clear previous chart if it exists
            if (Chart.getChart(ctx)) {
                Chart.getChart(ctx).destroy(); // Destroy existing chart instance
            }

            // Create new chart
            const myChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels, // Time-stamped labels
                    datasets: [{
                        label: fileName, // Show the file name in the legend
                        data: accelerations, // Acceleration data
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderWidth: 2,
                        fill: true,
                    }]
                },
                options: {
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: 'second',
                                displayFormats: {
                                    second: 'HH:mm:ss'
                                }
                            },
                            title: {
                                display: true,
                                text: 'time'
                            },
                            position: 'bottom' // Ensure x-axis is at the bottom
                        },
                        y: {
                            min: -10000, // Set minimum y-axis value
                            max: 10000, // Set maximum y-axis value
                            ticks: {
                                stepSize: 500 // Set interval between tick marks
                            },
                            title: {
                                display: true,
                                text: 'acceleration'
                            },
                            position: 'left' // Ensure y-axis is on the left
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error loading readings:', error));
}

    // Initial call to populate the file list and load readings
    fetchFilesAndUpdateGraph();

    // Start polling for new files 
    const pollFiles = setInterval(() => {
        fetchFilesAndUpdateGraph();

        if (isInitialPoll) {
            // After the first poll, switch to 1 hour
            isInitialPoll = false;
            clearInterval(pollFiles); // Clear the initial interval
            setInterval(fetchFilesAndUpdateGraph, subsequentPollingInterval); // Start a new interval with 1 hour
        }
    }, initialPollingInterval); // Initial interval is 1 second
    });
