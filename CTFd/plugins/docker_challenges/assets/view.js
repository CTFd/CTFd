CTFd._internal.challenge.data = undefined

CTFd._internal.challenge.renderer = CTFd._internal.markdown;


CTFd._internal.challenge.preRender = function() {}

CTFd._internal.challenge.render = function(markdown) {

    return CTFd._internal.challenge.renderer.parse(markdown)
}


CTFd._internal.challenge.postRender = function() {
    const containername = CTFd._internal.challenge.data.docker_image;
    get_docker_status(containername);
    createWarningModalBody();
}

function createWarningModalBody(){
    // Creates the Warning Modal placeholder, that will be updated when stuff happens.
    if (CTFd.lib.$('#warningModalBody').length === 0) {
        CTFd.lib.$('body').append('<div id="warningModalBody"></div>');
    }
}

function get_docker_status(container) {
    // Use CTFd.fetch to call the API
    CTFd.fetch("/api/v1/docker_status").then(response => response.json())
    .then(result => {
        result.data.forEach(item => {
            if (item.docker_image == container) {
                // Split the ports and create the data string
                var ports = String(item.ports).split(',');
                var data = '';
                
                ports.forEach(port => {
                    port = String(port);
                    data = data + 'Host: ' + item.host + ' Port: ' + port + '<br />';
                });
                // Update the DOM with the docker container information
                // CTFd.lib.$('#docker_container').html('<pre>Docker Container Information:<br />' + data + 
                // '<div class="mt-2" id="' + String(item.instance_id).substring(0, 10) + '_revert_container"></div>');

                CTFd.lib.$('#docker_container').html(
                    '<pre>Docker Container Information:<br />' + data + '</pre>' +
                    '<button class="btn btn-danger mt-2 stop-container-btn" ' +
                    'data-container="' + item.docker_image + '">' +
                    'Stop Container</button>' +
                    '<div class="mt-2" id="' + String(item.instance_id).substring(0, 10) + '_revert_container"></div>'
                );


                // OPTIONAL:: Use event delegation to prevent multiple handlers
                CTFd.lib.$(document).off('click', '.stop-container-btn').on('click', '.stop-container-btn', function (e) {
                    e.preventDefault();
                    e.stopPropagation();
                    const container = CTFd.lib.$(this).data('container');
                    // Disable button temporarily
                    const $btn = CTFd.lib.$(this);
                    $btn.prop('disabled', true).text('Stopping...');
                    stop_container(container);
                    // Re-enable after delay
                    setTimeout(() => {
                        $btn.prop('disabled', false).text('Stop Container');
                    }, 3000);
                });

                // Update the DOM with connection info information.
                // Note that connection info should contain "host" and "port"
                var $link = CTFd.lib.$('.challenge-connection-info');
                $link.html($link.html().replace(/host/gi, item.host));
                $link.html($link.html().replace(/port|\b\d{5}\b/gi, ports[0].split("/")[0]));

                // Check if there are links in there, if not and we use a http[s] address, make it a link
                CTFd.lib.$(".challenge-connection-info").each(function () {
                    const $span = CTFd.lib.$(this);
                    const html = $span.html();
                
                    // Skip if already has a link
                    if (html.includes("<a")) {
                        return;
                    }
                
                    // If it contains "http", try to extract and wrap it
                    const urlMatch = html.match(/(http[s]?:\/\/[^\s<]+)/);
                
                    if (urlMatch) {
                        const url = urlMatch[0];
                        const linked = html.replace(url, `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`);
                        $span.html(linked);
                    }
                });

                // Set up the countdown timer
                var countDownDate = new Date(parseInt(item.revert_time) * 1000).getTime();
                var x = setInterval(function() {
                    var now = new Date().getTime();
                    var distance = countDownDate - now;
                    var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                    var seconds = Math.floor((distance % (1000 * 60)) / 1000);
                    if (seconds < 10) {
                        seconds = "0" + seconds;
                    }

                    // Update the countdown display
                    CTFd.lib.$("#" + String(item.instance_id).substring(0, 10) + "_revert_container").html('Stop or Revert Available in ' + minutes + ':' + seconds);

                    // Check if the countdown is finished and enable the revert button
                    if (distance < 0) {
                        clearInterval(x);
                        CTFd.lib.$("#" + String(item.instance_id).substring(0, 10) + "_revert_container").html(
                            '<a onclick="start_container(\'' + item.docker_image + '\');" class="btn btn-dark">' +
                            '<small style="color:white;"><i class="fas fa-redo"></i> Revert</small></a> '+
                            '<a onclick="stop_container(\'' + item.docker_image + '\');" class="btn btn-dark">' +
                            '<small style="color:white;"><i class="fas fa-redo"></i> Stop</small></a>'
                        );
                    }
                }, 1000);

                return false; // Stop once the correct container is found
            }
        });
    })
    .catch(error => {
        console.error('Error fetching docker status:', error);
    });
    // Display the normal start button, if there is no need for updating
    const NormalStartButtonHTML=`
        <span>
            <a onclick="start_container('${CTFd._internal.challenge.data.docker_image}');" class='btn btn-dark'>
                <small style='color:white;'><i class="fas fa-play"></i>  Start Docker Instance for challenge</small>
            </a>
        </span>`
    CTFd.lib.$('#docker_container').html(NormalStartButtonHTML);
}

function stop_container(container) {
    // Prevent multiple simultaneous requests
    if (window.stoppingContainer) {
        console.log("Stop request already in progress, ignoring");
        return;
    }
    
    if (confirm("Are you sure you want to stop the container for: \n" + CTFd._internal.challenge.data.name)) {
        window.stoppingContainer = true;
        
        CTFd.fetch("/api/v1/container?name=" + encodeURIComponent(container) + 
                   "&challenge=" + encodeURIComponent(CTFd._internal.challenge.data.name) + 
                   "&stopcontainer=True", {
            method: "GET"
        })
        .then(function (response) {
            return response.json().then(function (json) {
                window.stoppingContainer = false;
                if (response.ok && json.success !== false) {
                    updateWarningModal({
                        title: "Success!",
                        warningText: "The Docker container for <br><strong>" + CTFd._internal.challenge.data.name + "</strong><br> was stopped successfully.",
                        buttonText: "Close",
                        onClose: function () {
                            // Refresh status after a short delay to avoid race conditions
                            setTimeout(() => {
                                get_docker_status(container);
                            }, 500);
                        }
                    });
                } else {
                    throw new Error(json.error || json.message || 'Failed to stop container');
                }
            });
        })
        .catch(function (error) {
            window.stoppingContainer = false;
            updateWarningModal({
                title: "Error",
                warningText: error.message || "An unknown error occurred while stopping the container.",
                buttonText: "Close",
                onClose: function () {
                    setTimeout(() => {
                        get_docker_status(container);
                    }, 500);
                }
            });
        });
    }
}

function start_container(container) {
    CTFd.lib.$('#docker_container').html('<div class="text-center"><i class="fas fa-circle-notch fa-spin fa-1x"></i></div>');
    CTFd.fetch("/api/v1/container?name=" + encodeURIComponent(container) + "&challenge=" + encodeURIComponent(CTFd._internal.challenge.data.name), {
        method: "GET"
    }).then(function (response) {
        return response.json().then(function (json) {
            if (response.ok) {
                get_docker_status(container);
    
                updateWarningModal({
                    title: "Attention!",
                    warningText: "A Docker container is started for you.<br>Note that you can only revert or stop a container once per 5 minutes!",
                    buttonText: "Got it!"
                });

            } else {
                throw new Error(json.message || 'Failed to start container');
            }
        });
    }).catch(function (error) {
        // Handle error and notify the user
        updateWarningModal({
            title: "Error!",
            warningText: error.message || "An unknown error occurred when starting your Docker container.",
            buttonText: "Got it!",
            onClose: function () {
                get_docker_status(container);  // ← Will be called when modal is closed
            }
        });
    });
}

// WE NEED TO CREATE THE MODAL FIRST, and this should be only used to fill it.

function updateWarningModal({
    title , warningText, buttonText, onClose } = {}) {
    const modalHTML = `
        <div id="warningModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; z-index:9999; background-color:rgba(0,0,0,0.9);">
          <div style="position:relative; margin:10% auto; width:400px; background:#1e1e1e; border-radius:8px; box-shadow:0 4px 20px rgba(0,0,0,0.7); overflow:hidden;">
            <div style="padding:1.25rem; display:flex; justify-content:space-between; align-items:center; background:#2d2d2d; border-bottom:1px solid #444;">
              <h5 style="margin:0; color:#e0e0e0; font-size:1.25rem; font-weight:600;">${title}</h5>
              <button type="button" id="warningCloseBtn" style="border:none; background:none; font-size:1.5rem; line-height:1; cursor:pointer; color:#999; transition:color 0.2s;">&times;</button>
            </div>
            <div style="padding:1.25rem; color:#b0b0b0; line-height:1.6;">
              ${warningText}
            </div>
            <div style="padding:1.25rem; text-align:right; border-top:1px solid #444; background:#2d2d2d;">
              <button type="button" class="btn btn-dark" id="warningOkBtn">${buttonText}</button>
            </div>
          </div>
        </div>
    `;
    CTFd.lib.$("#warningModalBody").html(modalHTML);

    // Show the modal
    CTFd.lib.$("#warningModal").show();

    // Close logic with callback
    const closeModal = () => {
        CTFd.lib.$("#warningModal").hide();
        if (typeof onClose === 'function') {
            onClose();  
        }
    };

    CTFd.lib.$("#warningCloseBtn").on("click", closeModal);
    CTFd.lib.$("#warningOkBtn").on("click", closeModal);
}

// In order to capture the flag submission, and remove the "Revert" and "Stop" buttons after solving a challenge
// We need to hook that call, and do this manually.
function checkForCorrectFlag() {
    const challengeWindow = document.querySelector('#challenge-window');
    if (!challengeWindow || getComputedStyle(challengeWindow).display === 'none') {
        clearInterval(checkInterval);
        checkInterval = null;
        return;
    }

    const notification = document.querySelector('.notification-row .alert');
    if (!notification) return;

    const strong = notification.querySelector('strong');
    if (!strong) return;

    const message = strong.textContent.trim();

    if (message.includes("Correct")) {
        get_docker_status(CTFd._internal.challenge.data.docker_image);
        clearInterval(checkInterval);
        checkInterval = null;
    }
}

if (!checkInterval) {
    var checkInterval = setInterval(checkForCorrectFlag, 1500);
}
