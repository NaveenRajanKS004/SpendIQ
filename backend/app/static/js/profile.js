// =========================
// CONFIG & AUTH
// =========================

const API = "http://127.0.0.1:8000"
const token = localStorage.getItem("token")

const headers = {
    "Authorization": "Bearer " + token
}


// =========================
// LOAD PROFILE
// =========================

async function loadProfile() {

    const res = await fetch(`${API}/me`, { headers })

    if (!res.ok) {
        alert("Failed to load profile")
        return
    }

    const data = await res.json()

    // Basic info
    document.getElementById("name").innerText = data.name
    document.getElementById("email").innerText = data.email
    document.getElementById("phone").innerText = data.phone || "-"

    // Profile picture
    if (data.profile_picture) {
        document.getElementById("profilePic").src = data.profile_picture
    }

    // Age calculation from DOB
    if (data.date_of_birth) {
        const dob = new Date(data.date_of_birth)
        const age = new Date().getFullYear() - dob.getFullYear()
        document.getElementById("age").innerText = age
    } else {
        document.getElementById("age").innerText = "-"
    }
}


// =========================
// UPDATE PROFILE
// =========================

async function updateProfile() {

    const name = document.getElementById("newName").value
    const phone = document.getElementById("newPhone").value
    const dob = document.getElementById("newDob").value

    const res = await fetch(`${API}/profile`, {
        method: "PUT",
        headers: {
            ...headers,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            name,
            phone,
            date_of_birth: dob
        })
    })

    const data = await res.json()

    if (res.ok) {
        alert("Profile updated")
        loadProfile()
    } else {
        alert(data.detail || "Update failed")
    }
}


// =========================
// PROFILE PICTURE UPLOAD
// =========================

function triggerUpload() {
    document.getElementById("picUpload").click()
}

document.getElementById("picUpload").addEventListener("change", async function () {

    const file = this.files[0]
    if (!file) return

    // Instant preview (UX improvement)
    const preview = URL.createObjectURL(file)
    document.getElementById("profilePic").src = preview

    const formData = new FormData()
    formData.append("file", file)

    const res = await fetch(`${API}/profile/upload-picture`, {
        method: "POST",
        headers,
        body: formData
    })

    const data = await res.json()

    if (!res.ok) {
        alert("Upload failed")
    }
})


// =========================
// CHANGE PASSWORD
// =========================

async function changePassword() {

    const old_password = document.getElementById("oldPassword").value
    const new_password = document.getElementById("newPassword").value

    const res = await fetch(`${API}/change-password`, {
        method: "PUT",
        headers: {
            ...headers,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            old_password,
            new_password
        })
    })

    const data = await res.json()

    if (res.ok) {
        alert("Password changed successfully")
    } else {
        alert(data.detail || "Failed to change password")
    }
}


// =========================
// INITIAL LOAD
// =========================

loadProfile()