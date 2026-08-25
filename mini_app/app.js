const tg = window.Telegram.WebApp;

tg.ready();
tg.expand();

const API_URL = "https://assurance-provincial-abs-oclc.trycloudflare.com";

const keyInput = document.getElementById("accessKey");
const continueBtn = document.getElementById("continueBtn");
const statusBox = document.getElementById("status");

const user = tg.initDataUnsafe?.user;

function showStatus(message, type) {
    statusBox.textContent = message;
    statusBox.className = "status " + type;
}

async function verifyAccess() {
    const key = keyInput.value.trim();

    if (!key) {
        showStatus("Please enter your access key.", "error");
        keyInput.focus();
        return;
    }

    if (!tg.initData) {
        console.log("CYSTERIONX DEBUG: Telegram initData is EMPTY");
        showStatus("Telegram authentication data missing. Re-open this panel from the Telegram bot.", "error");
        return;
    }

    console.log("CYSTERIONX DEBUG: Telegram initData received, length:", tg.initData.length);

    continueBtn.disabled = true;
    showStatus("Verifying secure access...", "loading");

    try {
        const response = await fetch(`${API_URL}/api/verify-key`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                initData: tg.initData,
                key: key
            })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            showStatus(data.message || "Access denied.", "error");
            return;
        }

        showStatus("Access verified. Welcome to CYSTERIONX.", "success");

        // Panel screen will be connected here next.
        console.log("Authenticated user:", data.user_id);

    } catch (error) {
        console.error(error);
        showStatus("Unable to connect to the secure server.", "error");
    } finally {
        continueBtn.disabled = false;
    }
}

keyInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        verifyAccess();
    }
});

if (!user || !tg.initData) {
    showStatus("Please open this panel from Telegram.", "error");
}
