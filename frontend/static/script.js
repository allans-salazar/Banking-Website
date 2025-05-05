// =====================
// Suspicious Input Detection
// =====================

// Check if the input contains common SQL injection patterns
function isSuspicious(input) {
  const patterns = ["'", "--", ";", "/*", "OR 1=1"];
  return patterns.some(p => input.includes(p));
}

// Send a log of suspicious activity to the backend
function logSuspiciousActivity(username, type) {
  fetch('http://127.0.0.1:5000/log_suspicious', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, log_type: type })
  });
}

// =====================
// Login Functionality (index.html)
// =====================

function loginUser() {
  const email = document.getElementById('login-email').value;
  const password = document.getElementById('login-password').value;

  // Check inputs for suspicious characters
  if (isSuspicious(email) || isSuspicious(password)) {
    logSuspiciousActivity(email, "sql_injection_attempt");
  }

  // Send login request to the Flask backend
  fetch('http://127.0.0.1:5000/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: email, password: password })
  })
  .then(res => res.json())
  .then(data => {
    if (data.error) {
      // Log and alert failed login
      logSuspiciousActivity(email, "failed_login");
      alert("Login failed: " + data.error);
    } else {
      // Admin Login - Prompt for PIN (2FA)
      if (data.message === "admin") {
        const pin = prompt("Enter Admin PIN for 2FA:");
        if (pin === "111") {
          // Save session info and redirect to admin dashboard
          localStorage.setItem("user_name", data.name);
          localStorage.setItem("username", email);
          window.location.href = "/admin_dashboard.html";
        } else {
          // Alert and log failed PIN attempt
          alert("Incorrect PIN. Access denied.");
          fetch("/log_suspicious", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              username: email,
              log_type: "failed_2fa_pin"
            })
          }).catch((err) => console.error("Failed to log PIN attempt:", err));
        }
      } else {
        // Normal User Login - Save session info and redirect
        localStorage.setItem("user_name", data.name);
        localStorage.setItem("username", email);
        window.location.href = "/user_page.html";
      }
    }
  })
  .catch(err => {
    console.error(err);
    alert("Login failed: Server error");
  });
}

// =====================
// Registration Functionality (register.html)
// =====================

function registerUser() {
  // Get values from registration form fields
  const name = document.getElementById("name").value;
  const last_name = document.getElementById("last_name").value;
  const username = document.getElementById("username").value;
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const ssn = document.getElementById("ssn").value;

  // Validate form fields
  if (!name || !last_name || !username || !email || !password || !ssn) {
    alert("Please fill out all fields.");
    return;
  }

  // Send registration request to the backend
  fetch("http://127.0.0.1:5000/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, last_name, username, email, password, ssn })
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

// =====================
// Load User Dashboard Data (user_page.html)
// =====================

function loadDashboard() {
  // Exit if not on the user dashboard page
  if (!window.location.href.includes("user_page.html")) return;

  const username = localStorage.getItem("username");

  if (!username) {
    alert("No user logged in.");
    window.location.href = "/";
    return;
  }

  // Request dashboard data from Flask
  fetch(`/dashboard/${username}`)
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        alert(data.error);
        return;
      }

      // Display user's name
      const nameSpan = document.getElementById("username");
      if (nameSpan) nameSpan.textContent = data.name;

      // Display balance
      const balanceSpan = document.getElementById("balance");
      if (balanceSpan) balanceSpan.textContent = "$" + parseFloat(data.balance).toFixed(2);

      // Display transaction history
      const tbody = document.getElementById("transaction-list");
      if (tbody) {
        tbody.innerHTML = "";

        if (data.transactions.length === 0) {
          const row = document.createElement("tr");
          row.innerHTML = `<td colspan="3" style="text-align:center; color: #999;">No transactions yet</td>`;
          tbody.appendChild(row);
        } else {
          data.transactions.forEach(tx => {
            const row = document.createElement("tr");
            row.innerHTML = `
              <td>${tx.date}</td>
              <td>${tx.description}</td>
              <td>${tx.amount >= 0 ? '-' : '-'}$${Math.abs(tx.amount).toFixed(2)}</td>
            `;
            tbody.appendChild(row);
          });
        }
      }
    })
    .catch(err => {
      console.error(err);
      alert("Error loading dashboard.");
    });
}