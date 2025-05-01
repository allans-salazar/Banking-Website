function loginUser() {
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
  
    fetch('http://127.0.0.1:5000/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: email, password: password })
    })
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        alert("Login failed: " + data.error);
      } else {
        alert(`Welcome back, ${data.username}! Role: ${data.role}`);
      }
    })
    .catch(err => {
      console.error(err);
      alert("Login failed: Server error");
    });
  }