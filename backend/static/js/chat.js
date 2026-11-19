// 와인 챗봇 화면 : /api/chat, /api/chat/history 호출

const messagesEl = document.getElementById("messages");
const emptyEl = document.getElementById("chat-empty");
const formEl = document.getElementById("chat-form");
const inputEl = document.getElementById("chat-input");
const sendButton = document.getElementById("send-button");
const resetButton = document.getElementById("reset-button");

const TOOL_LABELS = {
    search_wine: "와인 DB 검색",
    youtube_search: "YouTube 검색",
};

function scrollToBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
}

function addBubble(role) {
    emptyEl.hidden = true;
    const bubble = document.createElement("div");
    bubble.className = `bubble bubble-${role}`;
    messagesEl.appendChild(bubble);
    return bubble;
}

function addUserMessage(text) {
    const bubble = addBubble("user");
    bubble.textContent = text;
    scrollToBottom();
    return bubble;
}

// html 은 서버에서 원본 HTML을 이스케이프한 마크다운 변환 결과
function addAssistantMessage(html, toolsUsed = []) {
    const bubble = addBubble("assistant");
    bubble.classList.add("markdown");
    bubble.innerHTML = html;

    bubble.querySelectorAll("a").forEach((link) => {
        link.target = "_blank";
        link.rel = "noopener noreferrer";
    });

    if (toolsUsed.length > 0) {
        const tools = document.createElement("div");
        tools.className = "bubble-tools";
        toolsUsed.forEach((name) => {
            const tool = document.createElement("span");
            tool.className = "tool-tag";
            tool.textContent = TOOL_LABELS[name] || name;
            tools.appendChild(tool);
        });
        bubble.appendChild(tools);
    }
    scrollToBottom();
}

function addErrorMessage(text) {
    const bubble = addBubble("error");
    bubble.setAttribute("role", "alert");
    bubble.textContent = text;
    scrollToBottom();
}

function addLoading() {
    const bubble = addBubble("assistant");
    bubble.classList.add("bubble-loading");
    bubble.textContent = "답변 생성 중";
    scrollToBottom();
    return bubble;
}

function setBusy(isBusy) {
    sendButton.disabled = isBusy;
    resetButton.disabled = isBusy;
}

async function sendMessage(text) {
    const userBubble = addUserMessage(text);
    setBusy(true);
    const loading = addLoading();

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text }),
        });
        const data = await response.json();
        loading.remove();

        if (response.ok) {
            addAssistantMessage(data.html, data.tools_used);
            // 답변이 길어도 질문과 답변의 시작 부분부터 읽을 수 있도록 함
            userBubble.scrollIntoView({ block: "start" });
        } else {
            addErrorMessage(typeof data.detail === "string" ? data.detail : "요청을 처리하지 못했습니다.");
        }
    } catch (error) {
        loading.remove();
        addErrorMessage("서버에 연결하지 못했습니다. 잠시 후 다시 시도해 주세요.");
    } finally {
        setBusy(false);
        inputEl.focus();
    }
}

function submitInput() {
    const text = inputEl.value.trim();
    if (!text || sendButton.disabled) {
        return;
    }
    inputEl.value = "";
    resizeInput();
    sendMessage(text);
}

function resizeInput() {
    inputEl.style.height = "auto";
    inputEl.style.height = `${inputEl.scrollHeight}px`;
}

async function loadHistory() {
    const response = await fetch("/api/chat/history");
    if (!response.ok) {
        return;
    }
    const history = await response.json();
    history.forEach((message) => {
        if (message.role === "user") {
            addUserMessage(message.content);
        } else {
            addAssistantMessage(message.html);
        }
    });
}

async function resetChat() {
    setBusy(true);
    try {
        const response = await fetch("/api/chat/history", { method: "DELETE" });
        if (!response.ok) {
            throw new Error("reset failed");
        }
        messagesEl.querySelectorAll(".bubble").forEach((bubble) => bubble.remove());
        emptyEl.hidden = false;
    } catch (error) {
        addErrorMessage("대화를 초기화하지 못했습니다.");
    } finally {
        setBusy(false);
        inputEl.focus();
    }
}

formEl.addEventListener("submit", (event) => {
    event.preventDefault();
    submitInput();
});

inputEl.addEventListener("input", resizeInput);

inputEl.addEventListener("keydown", (event) => {
    // 한글 조합 중 Enter는 글자 확정이므로 전송하지 않음
    if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
        event.preventDefault();
        submitInput();
    }
});

resetButton.addEventListener("click", resetChat);

messagesEl.addEventListener("click", (event) => {
    const example = event.target.closest("[data-example]");
    if (example && !sendButton.disabled) {
        sendMessage(example.textContent);
    }
});

loadHistory();
