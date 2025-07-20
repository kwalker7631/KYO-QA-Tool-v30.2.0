// app.js
// Author: Kenneth Walker
// Date: 2025-07-19
// Version: 30.2.0

document.addEventListener('DOMContentLoaded', () => {
    // --- Element Selectors ---
    const pdfFilesInput = document.getElementById('pdf-files');
    const filePreviewContainer = document.getElementById('file-preview-container');
    const fileList = document.getElementById('file-list');
    const form = document.getElementById('upload-form');
    const startButton = document.getElementById('start-button');
    const progressBar = document.getElementById('progress-bar');
    const progressContainer = document.getElementById('progress-container');
    const logOutput = document.getElementById('log-output');
    const statusText = document.getElementById('status-text');
    const resultLinkContainer = document.getElementById('result-link-container');
    const resultLink = document.getElementById('result-link');
    const statusSummary = document.getElementById('status-summary');
    
    // Tabs
    const tabLogs = document.getElementById('tab-logs');
    const tabReview = document.getElementById('tab-review');
    const logContainer = document.getElementById('log-output-container');
    const reviewContainer = document.getElementById('review-container');
    const reviewList = document.getElementById('review-list');

    // Pattern Manager Modal
    const patternModal = document.getElementById('pattern-modal');
    const patternManagerBtn = document.getElementById('pattern-manager-btn');
    const modalCloseBtn = document.getElementById('modal-close-btn');
    const modalBackdrop = document.getElementById('modal-backdrop');
    const modelPatternsTextarea = document.getElementById('model-patterns-textarea');
    const qaPatternsTextarea = document.getElementById('qa-patterns-textarea');
    const patternSaveBtn = document.getElementById('pattern-save-btn');
    const patternStatus = document.getElementById('pattern-status');

    let statusInterval;
    let statusCounters = {};

    // --- Event Listeners ---
    pdfFilesInput.addEventListener('change', updateFilePreview);
    form.addEventListener('submit', handleFormSubmit);
    tabLogs.addEventListener('click', () => switchTab('logs'));
    tabReview.addEventListener('click', () => switchTab('review'));
    patternManagerBtn.addEventListener('click', openPatternManager);
    modalCloseBtn.addEventListener('click', closePatternManager);
    modalBackdrop.addEventListener('click', closePatternManager);
    patternSaveBtn.addEventListener('click', savePatterns);

    function updateFilePreview() {
        if (pdfFilesInput.files.length > 0) {
            filePreviewContainer.classList.remove('hidden');
            fileList.innerHTML = '';
            Array.from(pdfFilesInput.files).forEach(file => {
                const fileItem = document.createElement('div');
                fileItem.className = 'file-list-item text-sm text-gray-700 p-2 bg-white';
                fileItem.textContent = file.name;
                fileList.appendChild(fileItem);
            });
        } else {
            filePreviewContainer.classList.add('hidden');
        }
    }

    async function handleFormSubmit(e) {
        e.preventDefault();
        resetUI();
        
        const formData = new FormData(form);
        startButton.disabled = true;
        startButton.textContent = 'Processing...';
        progressContainer.style.display = 'block';

        try {
            const response = await fetch('/api/process', { method: 'POST', body: formData });
            if (response.ok) {
                statusInterval = setInterval(checkStatus, 1000);
            } else {
                logMessage(`Error starting job: ${await response.text()}`, 'error');
                resetUI();
            }
        } catch (error) {
            logMessage(`Network or server error: ${error}`, 'error');
            resetUI();
        }
    }

    function checkStatus() {
        fetch('/api/status')
            .then(response => response.json())
            .then(messages => messages.forEach(handleMessage));
    }

    function handleMessage(msg) {
        switch (msg.type) {
            case 'log':
                logMessage(msg.msg, msg.tag || 'info');
                break;
            case 'progress':
                updateProgress(msg.current, msg.total);
                break;
            case 'status':
                statusText.textContent = msg.msg;
                break;
            case 'file_complete':
                statusCounters[msg.status] = (statusCounters[msg.status] || 0) + 1;
                updateStatusSummary();
                break;
            case 'review_item':
                addReviewItem(msg.data);
                break;
            case 'finish':
                clearInterval(statusInterval);
                statusText.textContent = `Job ${msg.status}!`;
                if (msg.status === 'Complete') {
                    resultLinkContainer.style.display = 'block';
                    resultLink.href = '/api/get-result';
                }
                startButton.disabled = false;
                startButton.textContent = 'Start Processing';
                break;
        }
    }

    function switchTab(tabName) {
        if (tabName === 'logs') {
            logContainer.style.display = 'block';
            reviewContainer.style.display = 'none';
            tabLogs.classList.add('border-[var(--kyocera-red)]', 'text-[var(--kyocera-red)]');
            tabReview.classList.remove('border-[var(--kyocera-red)]', 'text-[var(--kyocera-red)]');
        } else {
            logContainer.style.display = 'none';
            reviewContainer.style.display = 'block';
            tabReview.classList.add('border-[var(--kyocera-red)]', 'text-[var(--kyocera-red)]');
            tabLogs.classList.remove('border-[var(--kyocera-red)]', 'text-[var(--kyocera-red)]');
        }
    }

    function addReviewItem(item) {
        if (reviewList.querySelector('.text-gray-500')) {
            reviewList.innerHTML = '';
        }
        const itemDiv = document.createElement('div');
        itemDiv.className = 'p-3 mb-2 bg-yellow-100 border border-yellow-300 rounded-lg';
        itemDiv.innerHTML = `<p class="font-bold">${item.filename}</p><p class="text-sm text-yellow-800">${item.reason}</p>`;
        reviewList.appendChild(itemDiv);
    }
    
    function updateStatusSummary() {
        const statuses = {
            'Success': { color: 'green', label: 'Success' },
            'Needs Review': { color: 'yellow', label: 'Review' },
            'Failed': { color: 'red', label: 'Failed' },
            'Protected': { color: 'gray', label: 'Protected' },
            'Corrupted': { color: 'purple', label: 'Corrupted' },
        };
        statusSummary.innerHTML = '';
        for (const [status, config] of Object.entries(statuses)) {
            const count = statusCounters[status] || 0;
            const card = document.createElement('div');
            card.className = `p-4 bg-${config.color}-100 border border-${config.color}-200 rounded-lg text-center`;
            card.innerHTML = `<p class="text-3xl font-bold text-${config.color}-800">${count}</p><p class="text-sm font-medium text-${config.color}-600">${config.label}</p>`;
            statusSummary.appendChild(card);
        }
    }

    async function openPatternManager() {
        try {
            const response = await fetch('/api/patterns');
            const data = await response.json();
            modelPatternsTextarea.value = data.model_patterns.join('\n');
            qaPatternsTextarea.value = data.qa_patterns.join('\n');
            patternModal.classList.remove('hidden');
        } catch (error) {
            logMessage('Could not load patterns.', 'error');
        }
    }

    function closePatternManager() {
        patternModal.classList.add('hidden');
        patternStatus.textContent = '';
    }

    async function savePatterns() {
        const model_patterns = modelPatternsTextarea.value.split('\n').filter(p => p.trim() !== '');
        const qa_patterns = qaPatternsTextarea.value.split('\n').filter(p => p.trim() !== '');

        try {
            const response = await fetch('/api/patterns', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model_patterns, qa_patterns }),
            });
            if (response.ok) {
                patternStatus.textContent = 'Saved successfully!';
                setTimeout(closePatternManager, 1500);
            } else {
                patternStatus.textContent = 'Error saving.';
                patternStatus.style.color = 'red';
            }
        } catch (error) {
            patternStatus.textContent = 'Server error.';
            patternStatus.style.color = 'red';
        }
    }

    function updateProgress(current, total) {
        const percentage = total > 0 ? (current / total) * 100 : 0;
        progressBar.style.width = `${percentage}%`;
        progressBar.textContent = `${current} / ${total}`;
    }

    function logMessage(message, type = 'info') {
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry log-${type}`;
        logEntry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        logOutput.appendChild(logEntry);
        logOutput.scrollTop = logOutput.scrollHeight;
    }

    function resetUI() {
        startButton.disabled = false;
        startButton.textContent = 'Start Processing';
        progressContainer.style.display = 'none';
        progressBar.style.width = '0%';
        progressBar.textContent = '';
        logOutput.innerHTML = '';
        reviewList.innerHTML = '<p class="text-gray-500">No items need review yet.</p>';
        statusText.textContent = 'Awaiting job...';
        resultLinkContainer.style.display = 'none';
        resultLink.href = '#';
        statusCounters = {};
        updateStatusSummary();
        if (statusInterval) clearInterval(statusInterval);
        filePreviewContainer.classList.add('hidden');
        fileList.innerHTML = '';
    }

    resetUI();
});
