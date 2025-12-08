
// Use the prject by:
//      1. Enable the Python backend by running "py detection.py" in your powershell terminal
//      2. Open index.html file in a new browser (preferrably Chrome)
//      3. An error will happen if the server isn't running or if there is an issue with the API which I doubt. btw ctrl+c to close the server

document.getElementById("uploadForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const file = document.getElementById("imageFile").files[0];
    if (!file) return;

    addMessage("user", "Locating your image...");

    let formData = new FormData();
    formData.append("image", file);

    try{
        const res = await fetch("http://127.0.0.1:5000/analyze", {
            method: "POST",
            body: formData
        });

        let data = await res.json();

        if (data.error) {
            addMessage("assistant", "Server error: " + data.error);
            return;
        }

        addMessage("assistant", data.result);
        addMessage("assistant", `Estimated coords: ${data.latitude}, ${data.longitude}`);

    }
    catch (err){
        addMessage("assistant", "Something went wrong.");
        console.error(err, "Request/Server Error. Ensure the server is running before testing.");
    }
});

function addMessage(role, text){
    const msgArea = document.getElementById("messageArea");
    const div = document.createElement("div");

    div.className = `msg ${role}`;
    div.textContent = text;
    
    msgArea.appendChild(div);
}
