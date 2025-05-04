function isSuspicious(input) {
  const patterns = ["'", "--", ";", "/*", "OR 1=1"];
  return patterns.some(p => input.includes(p));
}

function logSuspiciousActivity(username, type) {
  fetch('http://127.0.0.1:5000/log_suspicious', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, log_type: type })
  });
}

function loginUser() {
  const email = document.getElementById('login-email').value;
  const password = document.getElementById('login-password').value;

  if (isSuspicious(email) || isSuspicious(password)) {
    logSuspiciousActivity(email, "sql_injection_attempt");
  }

  fetch('http://127.0.0.1:5000/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: email, password: password })
  })
  .then(res => res.json())
  .then(data => {
    if (data.error) {
      logSuspiciousActivity(email, "failed_login");
      alert("Login failed: " + data.error);
    } else {
      if (data.message === "admin") {
        const pin = prompt("Enter Admin PIN for 2FA:");
        if (pin === "111") {
          localStorage.setItem("user_name", data.name);
          localStorage.setItem("username", email);
          window.location.href = "/admin_dashboard.html";
        } else {
          alert("Incorrect PIN. Access denied.");
      
          // Log failed PIN attempt
          fetch("/log_suspicious", {
            method: "POST",
            headers: {
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              username: email,
              log_type: "failed_2fa_pin"
            })
          }).catch((err) => console.error("Failed to log PIN attempt:", err));
        }
      } else {
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

  function registerUser() {
    const name = document.getElementById("name").value;
    const last_name = document.getElementById("last_name").value;
    const username = document.getElementById("username").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const ssn = document.getElementById("ssn").value;

    if (!name || !last_name || !username || !email || !password || !ssn) {
      alert("Please fill out all fields.");
      return;
    }

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


  function loadDashboard() {
  // Only run on user_page.html to avoid admin dashboard conflict
  if (!window.location.href.includes("user_page.html")) return;
    const username = localStorage.getItem("username");
  
    if (!username) {
      alert("No user logged in.");
      window.location.href = "/";
      return;
    }
  
    fetch(`/dashboard/${username}`)
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          alert(data.error);
          return;
        }
  
        // Show name
        const nameSpan = document.getElementById("username");
        if (nameSpan) nameSpan.textContent = data.name;
  
        // Show balance
        const balanceSpan = document.getElementById("balance");
        if (balanceSpan) balanceSpan.textContent = "$" + parseFloat(data.balance).toFixed(2);
  
        // Show transactions
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