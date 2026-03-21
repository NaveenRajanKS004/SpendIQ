const API = "http://127.0.0.1:8000"

async function register() {

    const name = document.getElementById("name").value
    const email = document.getElementById("email").value
    const password = document.getElementById("password").value

    const res = await fetch(`${API}/register`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            name,
            email,
            password
        })
    })

    if (res.status === 200) {
        alert("Account created. Please login.")
        window.location.href = "/login-page"
    } else {
        alert("Registration failed")
    }
}