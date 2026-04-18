const socket = io();

// UI Elements
const btnLaunch = document.getElementById('btn-launch');
const btnSend = document.getElementById('btn-send');
const btnStop = document.getElementById('btn-stop');
const btnClose = document.getElementById('btn-close');
const btnClear = document.getElementById('btn-clear');
const logWindow = document.getElementById('log-window');
const statSent = document.getElementById('stat-sent');
const connectionDot = document.getElementById('connection-dot');
const connectionStatus = document.getElementById('connection-status');
const numbersInput = document.getElementById('numbers');
const messageInput = document.getElementById('message');

let sentCount = 0;

// Socket connection handlers
socket.on('connect', () => {
    connectionDot.classList.add('connected');
    connectionStatus.innerText = 'Connected to Server';
    addLog('System', 'Connected to backend server.');
});

socket.on('disconnect', () => {
    connectionDot.classList.remove('connected');
    connectionStatus.innerText = 'Server Disconnected';
    addLog('Error', 'Lost connection to server.');
});

socket.on('log_update', (data) => {
    const message = data.message;
    let type = 'system';
    
    if (message.includes('✅')) {
        type = 'success';
        sentCount++;
        statSent.innerText = sentCount;
    } else if (message.includes('❌') || message.includes('⚠️')) {
        type = 'error';
    }
    
    addLog(type, message);

    // Re-enable send button if all tasks completed
    if (message.includes('All tasks completed')) {
        btnSend.disabled = false;
        btnStop.disabled = true;
    }
});

// Helper: Add log to window
function addLog(type, message) {
    const div = document.createElement('div');
    div.className = `log-entry ${type.toLowerCase()}`;
    div.innerText = `[${new Date().toLocaleTimeString()}] ${message}`;
    logWindow.appendChild(div);
    logWindow.scrollTop = logWindow.scrollHeight;
}

// Event Listeners
btnLaunch.addEventListener('click', () => {
    socket.emit('start_browser');
    btnLaunch.disabled = true;
    btnSend.disabled = false;
    addLog('System', 'Requesting browser launch...');
});

btnSend.addEventListener('click', () => {
    const numbers = numbersInput.value.split('\n').filter(n => n.trim() !== '');
    const message = messageInput.value.trim();
    const min_delay = document.getElementById('min-delay').value;
    const max_delay = document.getElementById('max-delay').value;

    if (numbers.length === 0) {
        addLog('Error', 'Please enter at least one phone number.');
        return;
    }
    if (message === '') {
        addLog('Error', 'Please enter a message.');
        return;
    }

    sentCount = 0;
    statSent.innerText = '0';
    btnSend.disabled = true;
    btnStop.disabled = false;
    
    socket.emit('send_messages', { numbers, message, min_delay, max_delay });
    addLog('System', `Starting automation for ${numbers.length} numbers.`);
});

btnStop.addEventListener('click', () => {
    socket.emit('stop_automation');
    btnStop.disabled = true;
});

btnClose.addEventListener('click', () => {
    socket.emit('close_browser');
    btnLaunch.disabled = false;
    btnSend.disabled = true;
    btnStop.disabled = true;
});

btnClear.addEventListener('click', () => {
    logWindow.innerHTML = '';
    sentCount = 0;
    statSent.innerText = '0';
    addLog('System', 'Logs cleared.');
});
