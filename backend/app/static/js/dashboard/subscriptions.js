async function loadSubscriptions(){

    const list = document.getElementById("subscriptionList")

    try{

        const res = await fetch(`${API}/subscriptions`,{headers})

        if(!res.ok) return

        const data = await res.json()

        list.innerHTML = ""

        data.forEach(sub=>{

            const li = document.createElement("li")

            li.innerText = `🔁 ${sub.description} — ${formatINR(sub.amount)}`

            list.appendChild(li)

        })

    }catch(err){

        console.log("Subscription endpoint unavailable")

    }

}