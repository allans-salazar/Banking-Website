function searchUser() {
    const userId = document.getElementById('user_id').value;
    fetch(`http://127.0.0.1:5000/get_user?user_id=${userId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert("Login failed: " + data.error);
            } else {
                alert(`Welcome, ${data.username}! Role: ${data.role}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert("Error occurred while logging in.");
        });
}