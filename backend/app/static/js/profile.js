const API = "http://127.0.0.1:8000"
const token = localStorage.getItem("token")

const headers = {
    "Authorization": "Bearer " + token
}

async function loadProfile() {

    const res = await fetch(`${API}/me`, { headers })
    const data = await res.json()

    document.getElementById("name").value = data.name || ""
}

async function saveProfile() {

    const name = document.getElementById("name").value

    const res = await fetch(`${API}/profile`, {
        method: "PUT",
        headers: {
            ...headers,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ name })
    })

    if (res.ok) {
        alert("Profile updated")
    } else {
        alert("Error updating profile")
    }
}

loadProfile()