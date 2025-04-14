function searchUser() {
    const username = document.getElementById('username').value;
    fetch(`/get_user?username=${username}`)
    .then(response => response.json())
    .then(data => {
        const resultDiv = document.getElementById('result');
        if (data.error) {
            resultDiv.innerHTML = data.error;
        } else {
            resultDiv.innerHTML = `Username: ${data.username}`;
        }
    });
}