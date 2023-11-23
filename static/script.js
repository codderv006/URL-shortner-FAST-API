async function shortenUrl() {
    const originalUrl = document.getElementById("originalUrl").value;
    const response = await fetch("http://127.0.0.1:8000/shorten", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ original_url: originalUrl }),
    });
    const data = await response.json();
    document.getElementById("shortenedUrl").innerText = `Shortened URL: ${data.short_url}`;
}
