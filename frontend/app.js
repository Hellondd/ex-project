const API_BASE = "/api";

async function loadWorkspaces() {
    const res = await fetch(`${API_BASE}/workspaces`);
    const data = await res.json();
    const list = document.getElementById('workspace-list');
    list.innerHTML = '<h3>Доступные места:</h3>';
    data.forEach(ws => {
        list.innerHTML += `
            <div class="ws-item">
                <strong>ID: ${ws.id}</strong> | ${ws.name} (${ws.type})
            </div>`;
    });
}

async function createBooking() {
    const payload = {
        workspace_id: parseInt(document.getElementById('wsId').value),
        user_id: 1, // Mock user
        book_date: document.getElementById('bDate').value,
        start_time: document.getElementById('bStart').value + ":00",
        end_time: document.getElementById('bEnd').value + ":00"
    };

    const res = await fetch(`${API_BASE}/bookings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    const msg = document.getElementById('msg');
    if (res.ok) {
        msg.innerText = "Успешно!";
        msg.style.color = "green";
    } else {
        const err = await res.json();
        msg.innerText = "Ошибка: " + err.detail;
        msg.style.color = "red";
    }
}

document.getElementById('submitBtn').addEventListener('click', createBooking);
window.onload = loadWorkspaces;