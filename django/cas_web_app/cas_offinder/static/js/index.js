function checkletter(self, message) {
    const PAMletter = self.value.toUpperCase();
    const PAMtype = ['A', 'C', 'G', 'T', 'R', 'Y', 'S', 'W', 'K', 'M', 'B', 'D', 'H', 'V', 'N'];
    if (message == 'query') {
        var messages = 'Please check query sequence'
    } else if (message == 'PAM') {
        var messages = 'Please check PAM'
    } else {
        var messages = message
    }
    for (var i = 0; i < PAMletter.length; i++) {
        if (!PAMtype.includes(PAMletter[i])) {
            alert(messages);
            self.value = '';
            return null;
        }
    }
    self.value = PAMletter;
}

function print_hi() {
    document.write("Hi<br>");
}

function mismatch_option_selector(this_id, id, name, default_value) {
    var select = document.createElement("select")
    select.id = id
    select.name = name

    for (var count = 0; count <= 9; count++) {
        var option = document.createElement("option");
        option.value = count;
        option.innerHTML = count;
        if (count == default_value) {
            option.selected = true;
        }
        select.appendChild(option);
    }
    document.getElementById(this_id).appendChild(select);
}





document.addEventListener('DOMContentLoaded', function () {
    const fileInput = document.getElementById('reference_file');
    const form = document.getElementById('upload-form');
    const progressBar = document.getElementById('progress-bar');
    const progressContainer = document.getElementById('progress-container');
    const progressInfo = document.getElementById('progress-info');
    const uploadSpeed = document.getElementById('upload-speed');
    const estimatedTime = document.getElementById('estimated-time');

    // Function to update progress bar
    function updateProgressBar(percentage) {
        // Remove decimal places using Math.floor()
        const wholePercentage = Math.floor(percentage);
        progressBar.style.width = wholePercentage + '%';
        progressBar.textContent = wholePercentage + '%';
    }

    // Function to format bytes to human-readable format
    function formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    // Function to format time to human-readable format
    function formatTime(seconds) {
        if (seconds < 60) {
            return seconds.toFixed(0) + ' seconds';
        } else if (seconds < 3600) {
            return (seconds / 60).toFixed(0) + ' minutes';
        } else {
            return (seconds / 3600).toFixed(0) + ' hours';
        }
    }

    // Event listener for file input change
    fileInput.addEventListener('change', function () {
        const file = fileInput.files[0];
        if (file) {
            // Check file extension
            const allowedExtensions = ['.fa'];
            const fileExtension = file.name.split('.').pop().toLowerCase();
            if (!allowedExtensions.includes('.' + fileExtension)) {
                alert('Please upload FASTA(*.fa) file');
                fileInput.value = ''; // Clear the file input
                return;
            }

            // Show progress bar and info
            progressContainer.style.display = 'block';
            progressInfo.style.display = 'block';

            const formData = new FormData();
            formData.append('reference_file', file);
            formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

            const xhr = new XMLHttpRequest();
            //xhr.open('POST', '{% url "cas_offinder:upload_file" %}', true); // Remove this line
            xhr.open('POST', uploadUrl, true); // Add this line

            // Progress event
            xhr.upload.addEventListener('progress', function (event) {
                if (event.lengthComputable) {
                    const percentComplete = (event.loaded / event.total) * 100;
                    updateProgressBar(percentComplete);

                    // Calculate upload speed and estimated time
                    const currentTime = new Date().getTime();
                    const elapsedTime = (currentTime - startTime) / 1000; // in seconds
                    const bytesUploaded = event.loaded;
                    const speed = bytesUploaded / elapsedTime; // in bytes/second
                    const remainingBytes = event.total - bytesUploaded;
                    const remainingTime = remainingBytes / speed; // in seconds

                    uploadSpeed.textContent = 'Speed: ' + formatBytes(speed) + '/s';
                    estimatedTime.textContent = 'Estimated time: ' + formatTime(remainingTime);
                }
            });

            // Load event
            xhr.addEventListener('load', function () {
                if (xhr.status === 200) {
                    console.log('File uploaded successfully');
                    updateProgressBar(100);
                    uploadSpeed.textContent = 'Upload complete';
                    estimatedTime.textContent = '';
                    window.location.reload(); // Add this line
                } else {
                    console.error('File upload failed with status:', xhr.status);
                    console.error('Response text:', xhr.responseText);
                    alert('File upload failed');
                }
            });

            // Error event
            xhr.addEventListener('error', function () {
                console.error('File upload failed');
                alert('File upload failed');
            });

            // Abort event
            xhr.addEventListener('abort', function () {
                console.log('File upload aborted');
            });

            // Start time for speed calculation
            const startTime = new Date().getTime();

            // Send the request
            xhr.send(formData);
        }
    });


    // Prevent default form submission when enter key is pressed
    form.addEventListener('submit', function (event) {
        // You can add validation here if needed
        // If validation fails, call event.preventDefault();
    });

    // Delete file button event listener
    const deleteButtons = document.querySelectorAll('.delete-file-button');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function (event) { // Add 'event' parameter
            event.preventDefault(); // Add this line
            const filePath = this.dataset.filePath;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch(deleteUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken
                },
                body: `file_path=${encodeURIComponent(filePath)}`
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        console.log('File deleted successfully');
                        window.location.reload(); // Reload the page to update the list
                    } else {
                        console.error('File deletion failed:', data.error);
                        alert('File deletion failed: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('File deletion failed:', error);
                    alert('File deletion failed: ' + error);
                });
        });
    });
});


function deleteFile(file_path) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    fetch('/delete/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken,
        },
        body: `file_path=${encodeURIComponent(file_path)}`,
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                console.log('File deleted successfully');
                // Update the UI (e.g., remove the file from the list)
                location.reload(); // Or update the file list dynamically
            } else {
                console.error('File deletion failed:', data.error);
                alert(`File deletion failed: ${data.error}`);
            }
        })
        .catch(error => {
            console.error('File deletion failed:', error);
            alert(`File deletion failed: ${error}`);
        });
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatTime(seconds) {
    if (seconds < 60) {
        return seconds.toFixed(0) + 's';
    } else if (seconds < 3600) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return minutes + 'm ' + remainingSeconds + 's';
    } else {
        const hours = Math.floor(seconds / 3600);
        const remainingMinutes = Math.floor((seconds % 3600) / 60);
        return hours + 'h ' + remainingMinutes + 'm';
    }
}