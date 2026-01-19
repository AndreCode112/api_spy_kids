function checkDeviceStatus() {
    fetch('/api/device/status/check_5_seconds/', {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
    })
    .catch(err => console.error("Erro:", err));
}
setInterval(checkDeviceStatus, 5000);