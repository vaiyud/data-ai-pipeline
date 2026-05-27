const fileUploadInput = document.getElementById('resume-upload');
const filePreviewBar = document.getElementById('resume-preview-bar');
const filePreviewName = document.getElementById('resume-preview-name');
const cancelFileBtn = document.getElementById('cancel-file');
const inputField = document.getElementById('user-message');
const chatForm = document.getElementById('chat-input-form');
const scrollBox = document.getElementById('chat-scroll-box');

// show file selection at user input area
fileUploadInput.addEventListener('change', function() {
    if (this.files && this.files[0]) {
        filePreviewName.textContent = this.files[0].name;
        filePreviewBar.className = 'd-flex align-items-center justify-content-between bg-white border rounded p-2 mb-2'; // unhide preview bar
    }
});

// clear selected file using cancel button
cancelFileBtn.addEventListener('click', function() {
    clearFileAttachment();
});

function clearFileAttachment() {
    fileUploadInput.value = ''; // reset file input
    filePreviewBar.className = 'd-none'; // hide preview bar
}

// user input submission
chatForm.addEventListener('submit', function(event) {
    // prevent page from refreshing when the form submits
    event.preventDefault();

    const messageText = inputField.value.trim();
    const hasFile = fileUploadInput.files && fileUploadInput.files[0];

    // prevent adding empty spaces/files to the history
    if (!messageText && !hasFile) return;

    // create the wrapper div with right-aligned flexbox layout (user)
    const messageWrapper = document.createElement('div');
    messageWrapper.className = 'd-flex flex-column align-items-end mb-3';

    // generate current local time format HR:MM AM/PM
    const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // build  dynamic bubble internal content layout
    let bubbleContent = '';

     // add a file icon inside the bubble for uploaded file
    if (hasFile) {
        const escapedFileName = escapeHTML(fileUploadInput.files[0].name);
        bubbleContent += `
            <div class="d-flex align-items-center border text-dark rounded p-2 mb-1 w-100 border-info text-start">
                <i class="fa fa-file-text-o text-dark me-2"></i>
                <span class="small text-truncate fw-semibold" style="max-width: 180px;">${escapedFileName}</span>
            </div>
        `;
    }

    // append text with file if exist
    if (messageText) {
        bubbleContent += `<div class="text-end text-break">${escapeHTML(messageText)}</div>`;
    }

    // add the sanitized user bubble HTML layout
    messageWrapper.innerHTML = `
        <div class="bg-info text-dark rounded shadow-sm px-3 py-2 text-end mw-75">
            ${bubbleContent}
        </div>
        <small class="text-muted mt-1 me-1">You • ${currentTime}</small>
    `;

    // append new message to scrollable message history
    scrollBox.appendChild(messageWrapper);

    // clear the input for the next message/file upload
    inputField.value = '';
    clearFileAttachment();

    // auto-scroll to the bottom so the new message is immediately visible
    scrollBox.scrollTop = scrollBox.scrollHeight;
});

// helper function to prevent XSS (Cross-Site Scripting) attacks if input contains HTML tags (prints as str)
function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
        tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    );
}