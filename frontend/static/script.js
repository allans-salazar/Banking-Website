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
      // Save name to local storage and redirect
      localStorage.setItem("user_name", data.name);
      window.location.href = "/user_page.html";
    }
  })
  .catch(err => {
    console.error(err);
    alert("Login failed: Server error");
  });
}

  function registerUser() {
    const name = document.getElementById("name").value;
    const lastname = document.getElementById("lastname").value;
    const username = document.getElementById("username").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const ssn = document.getElementById("ssn").value;

    if (!name || !lastname || !username || !email || !password || !ssn) {
      alert("Please fill out all fields.");
      return;
    }

    fetch("http://127.0.0.1:5000/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, lastname, username, email, password, ssn })
    })
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        alert("Registration failed: " + data.error);
      } else {
        alert("Account created successfully!");
        window.location.href = "/";
      }
    })
    .catch(err => {
      console.error(err);
      alert("Error during registration.");
    });
  }