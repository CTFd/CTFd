// Guards for internal namespace to prevent duplicate definitions
if (typeof CTFd._internal === 'undefined') {
    CTFd._internal = {};
}
if (typeof CTFd._internal.challenge === 'undefined') {
    CTFd._internal.challenge = {};
}

if (typeof CTFd._internal.challenge.preRender !== 'function') {
    CTFd._internal.challenge.preRender = function() {};
}

CTFd._internal.challenge.data = CTFd._internal.challenge.data || undefined;

if (typeof CTFd._internal.challenge.postRender !== 'function') {
    CTFd._internal.challenge.postRender = function() {
        setTimeout(function() {
            overrideSubmitBehavior();
            try { checkChallengePendingOnOpen(); } catch (e) { console.warn('[photo] checkChallengePendingOnOpen failed', e); }
        }, 100);
    };
}

// Lightweight translation helper used by this plugin (mirrors other plugins)
if (typeof CTFd.translations === 'undefined') {
    CTFd.translations = {};
}
// Translation helper so our notifications can be localized
if (typeof window.__photo_plugin_translate === 'undefined') {
    window.__photo_plugin_translate = function(str) {
        return (CTFd.translations && CTFd.translations[str]) ? CTFd.translations[str] : str;
    };
}
var __ = window.__photo_plugin_translate;

function showSimpleNotification(title, body) {
    // Ensure a target container exists (insert after submit-row if missing)
    if (CTFd.lib.$('#photo-response-container').length === 0) {
        CTFd.lib.$('.submit-row').after('<div id="photo-response-container" class="mt-3"></div>');
    }
    const responseContainer = CTFd.lib.$('#photo-response-container');
    const responseHtml = `
        <div class="multi-question-alert alert alert-info alert-dismissible fade show" role="alert">
            <strong>${title}</strong> ${body}
        </div>
    `;
    responseContainer.html(responseHtml);
}

function markChallengePending() {
    // Disable inputs and submit button
    CTFd.lib.$('#challenge-input').prop('disabled', true);
    CTFd.lib.$('#challenge-submit-photo').prop('disabled', true).addClass('disabled-button');

    // Dim challenge text and inputs to indicate pending status
    CTFd.lib.$('.challenge-name, .challenge-value, .challenge-desc, .submit-row').css('opacity', '0.6');

    // Remove other badges then add pending badge
    CTFd.lib.$('.photo-pending-badge').remove();
    CTFd.lib.$('.photo-rejected-badge').remove();
    CTFd.lib.$('.photo-approved-badge').remove();
    CTFd.lib.$('.challenge-name').append('<span class="photo-pending-badge badge bg-warning ms-2">Pending Review</span>');
}

function markChallengeRejected() {
    // Enable inputs and clear pending styling
    CTFd.lib.$('#challenge-input').prop('disabled', false);
    CTFd.lib.$('#challenge-submit-photo').prop('disabled', false).removeClass('disabled-button');
    CTFd.lib.$('.challenge-name, .challenge-value, .challenge-desc, .submit-row').css('opacity', '1');

    // Remove pending badge and add rejected badge
    CTFd.lib.$('.photo-pending-badge').remove();
    if (CTFd.lib.$('.challenge-name .photo-rejected-badge').length === 0) {
        CTFd.lib.$('.challenge-name').append('<span class="photo-rejected-badge badge bg-danger ms-2">Rejected</span>');
    }
}

function markChallengeApproved() {
    // Let the regular CTFd UI handle marking a challenge as solved (green).
    // We create a Solve on the backend when an admin approves; reload the
    // page so the standard challenge rendering (and solved-state UI) is used.
    try { CTFd.lib.$('.photo-pending-badge').remove(); } catch (e) {}
    showSimpleNotification(__('Submission Approved'), __('Your photo submission was approved. The challenge will be marked accordingly.'));
    // Avoid triggering repeated reloads if the page keeps re-rendering.
    // Use sessionStorage per-challenge so the flag survives a single reload
    // but prevents an infinite reload loop when the status remains "approved".
    try {
        function _resolveChallengeIdForGuard() {
            try { const id = Number(CTFd._internal.challenge?.data?.id); if (!Number.isNaN(id) && id > 0) return id; } catch (e) {}
            try { const val = CTFd.lib.$('#challenge-id').val(); const id = Number(val); if (!Number.isNaN(id) && id > 0) return id; } catch (e) {}
            try { const dataId = CTFd.lib.$('[data-challenge-id]').attr('data-challenge-id'); const id = Number(dataId); if (!Number.isNaN(id) && id > 0) return id; } catch (e) {}
            try { const m = window.location.pathname.match(/challenges\/(\d+)/); if (m) { const id = Number(m[1]); if (!Number.isNaN(id) && id > 0) return id; } } catch (e) {}
            return null;
        }
        var _cid = _resolveChallengeIdForGuard();
        if (_cid !== null) {
            var key = 'photo_approved_reload_done_' + String(_cid);
            if (sessionStorage.getItem(key)) {
                return;
            }
            sessionStorage.setItem(key, '1');
        } else {
            // Fallback to window-scoped guard if we couldn't resolve id
            if (window.__photo_approved_reload_done) {
                return;
            }
            window.__photo_approved_reload_done = true;
        }
    } catch (e) {}
    setTimeout(function() { window.location.reload(); }, 800);
}

// Check server for pending submissions for the currently opened challenge
function checkChallengePendingOnOpen() {
    // resolve challenge id using same logic as submit handler
    function resolveChallengeId() {
        try { const id = Number(CTFd._internal.challenge?.data?.id); if (!Number.isNaN(id) && id > 0) return id; } catch (e) {}
        try { const val = CTFd.lib.$('#challenge-id').val(); const id = Number(val); if (!Number.isNaN(id) && id > 0) return id; } catch (e) {}
        try { const dataId = CTFd.lib.$('[data-challenge-id]').attr('data-challenge-id'); const id = Number(dataId); if (!Number.isNaN(id) && id > 0) return id; } catch (e) {}
        try { const m = window.location.pathname.match(/challenges\/(\d+)/); if (m) { const id = Number(m[1]); if (!Number.isNaN(id) && id > 0) return id; } } catch (e) {}
        return NaN;
    }

    var challenge_id = resolveChallengeId();
    if (Number.isNaN(challenge_id)) { return; }

    // Use CTFd.fetch for convenience (GET request, no body)
    var url = `/api/v1/photo_challenges/status/${challenge_id}`;
    try {
        CTFd.fetch(url).then(function(resp) {
            try { return resp.json(); } catch (e) { return Promise.resolve({}); }
        }).then(function(data) {
                if (data && data.status) {
                    try {
                        if (data.status === 'pending') {
                            markChallengePending();
                            showSimpleNotification(__('Submission Pending'), __('You have a photo submission pending review for this challenge.'));
                        } else if (data.status === 'rejected') {
                            markChallengeRejected();
                            showSimpleNotification(__('Submission Rejected'), __('Your photo submission was rejected. You may resubmit.'));
                        } else if (data.status === 'approved') {
                            markChallengeApproved();
                        }
                    } catch (e) { console.warn('[photo] markChallengePending failed', e); }
            }
        }).catch(function(err) {
            console.warn('[photo] pending status check failed', err);
        });
    } catch (e) {
        // Fallback to native fetch if CTFd.fetch is not available
        try {
            window.fetch(url, {credentials: 'same-origin'}).then(r => r.json()).then(function(data){ if (data && data.pending) { markChallengePending(); showSimpleNotification(__('Submission Pending'), __('You have a photo submission pending review for this challenge.')); } }).catch(()=>{});
        } catch (e) {}
    }
}

// Override the submit button behavior for multi-question challenges
function overrideSubmitBehavior() {
    console.log("Overriding submit behavior...");
    
    // Check if already overridden
    if (CTFd.lib.$("#challenge-submit-photo").length > 0 || CTFd.lib.$("#challenge-submit").data('photo-question-override')) {
        console.log("Submit behavior already overridden, skipping...");
        return;
    }
    
    // Completely replace the submit button to avoid any CTFd interference
    var originalButton = CTFd.lib.$("#challenge-submit");
    var buttonHtml = originalButton[0].outerHTML;
    
    // Create a new button with the same styling but completely new element
    var newButton = CTFd.lib.$(buttonHtml);
    newButton.attr('id', 'challenge-submit-photo');
    newButton.removeAttr('x-on:click'); // Remove Alpine.js bindings
    newButton.removeAttr('@click');     // Remove other framework bindings
    
    // Replace the original button
    originalButton.replaceWith(newButton);
    
    // Remove ALL existing event handlers from multiple elements
    CTFd.lib.$("#challenge-submit-photo").off();
    CTFd.lib.$("#challenge-input").off();
    CTFd.lib.$("#challenge-window form").off();
    CTFd.lib.$("#challenge-window").off('submit');
    CTFd.lib.$("body").off('submit', '#challenge-window form');
    CTFd.lib.$(document).off('click', '#challenge-submit, #challenge-submit-photo');
    CTFd.lib.$(document).off('submit', '#challenge-window form');
    
    // Mark as overridden
    CTFd.lib.$("#challenge-submit-photo").data('photo-question-override', true);
    
    // Prevent form submission entirely
    CTFd.lib.$("#challenge-window form").on('submit.photo-question', function(e) {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        console.log("Form submit blocked for multi-question challenge");
        return false;
    });
    
    // Add our custom click handler
    CTFd.lib.$("#challenge-submit-photo").on('click.photo-question', function(e) {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        
        // Prevent rapid double-clicks
        if (CTFd.lib.$(this).data('submitting')) {
            console.log("Already submitting, ignoring duplicate click");
            return;
        }
        
        console.log("Custom submit handler triggered");
        
        // Robustly determine challenge id from several possible sources
        function resolveChallengeId() {
            // 1) CTFd internal challenge data
            try {
                const id = Number(CTFd._internal.challenge?.data?.id);
                if (!Number.isNaN(id) && id > 0) return id;
            } catch (e) {}

            // 2) hidden input #challenge-id
            try {
                const val = CTFd.lib.$("#challenge-id").val();
                const id = Number(val);
                if (!Number.isNaN(id) && id > 0) return id;
            } catch (e) {}

            // 3) data attribute on DOM
            try {
                const dataId = CTFd.lib.$('[data-challenge-id]').attr('data-challenge-id');
                const id = Number(dataId);
                if (!Number.isNaN(id) && id > 0) return id;
            } catch (e) {}

            // 4) attempt to parse from URL
            try {
                const m = window.location.pathname.match(/challenges\/(\d+)/);
                if (m) {
                    const id = Number(m[1]);
                    if (!Number.isNaN(id) && id > 0) return id;
                }
            } catch (e) {}

            return NaN;
        }

        var challenge_id = resolveChallengeId();
        const fileInput = document.querySelector('#photo-file');

        // If a photo is not provided, give the user an error
        if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
            showSimpleNotification(
                __("Error"),
                __("Please upload a photo before submitting.")
            );
            return;
        }

        console.log("Submit data:", { challenge_id, fileInput });
        if (Number.isNaN(challenge_id)) {
            showSimpleNotification(
                __("Error"),
                __("Could not determine challenge id. Please reload and try again.")
            );
            return;
        }
        
        // Disable submit button and mark as submitting
        CTFd.lib.$(this).prop('disabled', true);
        CTFd.lib.$(this).addClass('disabled-button');
        CTFd.lib.$(this).data('submitting', true);

        var formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('challenge_id', String(challenge_id));

        // debug: log FormData entries to ensure file is present (file object will show as [object File])
        // for (const pair of formData.entries()) {
        //     console.log('FormData:', pair[0], pair[1]);
        // }

        // Use native window.fetch to avoid CTFd.fetch forcing JSON headers
        return window.fetch('/api/v1/photo_challenges/upload', {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                // provide CSRF token expected by server
                'CSRF-Token': (CTFd && CTFd.config && CTFd.config.csrfNonce) || '' ,
                'Accept': 'application/json'
            },
            body: formData
        }).then(response => { console.log(response); return response.json(); }).then(function(response) {
            console.log("Response received:", response);
            
            // Re-enable submit button
            CTFd.lib.$("#challenge-submit-photo").prop('disabled', false);
            CTFd.lib.$("#challenge-submit-photo").removeClass('disabled-button');
            CTFd.lib.$("#challenge-submit-photo").data('submitting', false);
            
            if (response.status === 403) {
                // User is not logged in or CTF is paused.
                return response;
            }
            if (response.status === 429) {
                // User was ratelimited but process response
                return response;
            }
            
            // Handle all responses with our custom handler
            // Handle a pending state
            if (response.success) {
                // Show pending notification
                showSimpleNotification(
                    __("Submission Pending"),
                    __("Your photo submission is pending review. You will be notified once it has been reviewed.")
                );
                // Visually mark the challenge as pending for the team
                try { markChallengePending(); } catch (e) { console.warn('[photo] markChallengePending failed', e); }
                return response;
            }
            
            // Show result
            showPhotoChallengeResponse(response.data);
            
            return response;
        }).catch(function(error) {
            console.error("Submit error:", error);
            // Re-enable submit button
            CTFd.lib.$("#challenge-submit-photo").prop('disabled', false);
            CTFd.lib.$("#challenge-submit-photo").removeClass('disabled-button');
            CTFd.lib.$("#challenge-submit-photo").data('submitting', false);
            throw error;
        });
    });
    
    // Handle Enter key
    CTFd.lib.$("#challenge-input").on('keyup.multi-question', function(e) {
        if (e.keyCode === 13) {
            e.preventDefault();
            CTFd.lib.$("#challenge-submit-multi").trigger('click.multi-question');
        }
    });
}

function showPhotoChallengeResponse(data) {
    // Find or create result notification area
    var resultNotification = CTFd.lib.$("#result-notification");
    var resultMessage = CTFd.lib.$("#result-message");
    
    if (resultNotification.length === 0) {
        // Create notification area if it doesn't exist
        var notificationHtml = `
            <div class="row notification-row">
                <div class="col-12">
                    <div id="result-notification" class="alert alert-dismissable text-center w-100" 
                         role="alert" style="display: none;">
                        <strong id="result-message"></strong>
                    </div>
                </div>
            </div>
        `;
        CTFd.lib.$('.photo-challenge-container').after(notificationHtml);
        resultNotification = CTFd.lib.$("#result-notification");
        resultMessage = CTFd.lib.$("#result-message");
    }
    
    // Clear previous classes
    resultNotification.removeClass();
    resultNotification.addClass("alert alert-dismissable text-center w-100");
    
    // Set message
    resultMessage.text(data.message || "");
    
    // Set appropriate styling based on status
    if (data.status === "correct") {
        resultNotification.addClass("alert-success");
    } else if (data.status === "pending") {
        resultNotification.addClass("alert-info");
    } else if (data.status === "incorrect") {
        resultNotification.addClass("alert-danger");
    } else if (data.status === "already_solved") {
        resultNotification.addClass("alert-info");
    } else {
        resultNotification.addClass("alert-warning");
    }
    
    // Show notification
    resultNotification.show();
    
    // Auto-hide after 5 seconds
    setTimeout(function() {
        resultNotification.hide();
    }, 5000);
}

CTFd._internal.challenge.submit = function (preview) {
    console.log("[photo] custom submit handler fired, preview =", preview);
    var challenge_id = parseInt(CTFd.lib.$('#challenge-id').val())

    // If a photo file input exists, send multipart/form-data with the file
    const fileInput = document.querySelector('#photo-file');
    if (fileInput && fileInput.files && fileInput.files.length > 0) {
        const file = fileInput.files[0];
        console.log("Submitting photo file:", file);
        const form = new FormData();
        form.append('challenge_id', challenge_id);
        // include submission field so server-side code expecting form['submission'] doesn't fail
        form.append('submission', '');
        form.append('file', file);

        // Send the multipart/form-data to the plugin upload API so the server
        // receives a multipart Content-Type instead of application/json.
        let url = '/api/v1/photo_evidence/photos/upload';
        if (preview) {
            url += '?preview=true';
        }

        return fetch(url, {
            method: 'POST',
            body: form,
            credentials: 'same-origin'
        }).then(function (response) {
            // Preserve response handling consistent with other submit handlers
            if (response.status === 429) {
                return response;
            }
            if (response.status === 403) {
                return response;
            }
            return response;
        });
    }

};