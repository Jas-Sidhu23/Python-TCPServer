const ws = true;
let socket = null;

function initWS() {
    // Establish a WebSocket connection with the server
    socket = new WebSocket('ws://' + window.location.host + '/websocket');

    // Called whenever data is received from the server over the WebSocket connection
    socket.onmessage = function (ws_message) {
        const message = JSON.parse(ws_message.data);
        const messageType = message.messageType;
        if (messageType === 'chatMessage') {
            addMessageToChat(message);
        } else if (messageType === "userListUpdate") {
            updateUserList(message.users);  // Corrected variable name here
        } else {
            // send message to WebRTC
            processMessageAsWebRTC(message, messageType);
        }
    }
}

function updateUserList(users) {
    const userListElement = document.getElementById('user-list');
    userListElement.innerHTML = '';  // Clear the current list
    users.forEach(function(user) {
        let li = document.createElement('li');
        li.textContent = user;
        userListElement.appendChild(li);
    });
}

function deleteMessage(messageId) {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            console.log(this.response);
        }
    }
    request.open("DELETE", "/chat-messages/" + messageId);
    request.send();
}

function chatMessageHTML(messageJSON) {
    const username = messageJSON.username;
    const message = messageJSON.message;
    const messageId = messageJSON.id;
    const messageFormat = messageJSON.message_format
    let messageHTML = "<br><button onclick='deleteMessage(\"" + messageId + "\")'>X</button> ";
    if (messageFormat == "image"){
        messageHTML += "<span id='message_" + messageId + "'><b>" + username + "</b>: <img src=" + message + " alt='Uploaded Image'></span";
    }else if (messageFormat == "video"){
        messageHTML += "<span id='message_" + messageId + "'><b>" + username + "</b>: <video src=" + message + " controls></video></span";
    }else{
        messageHTML += "<span id='message_" + messageId + "'><b>" + username + "</b>: " + message + "</span>";
    }
    return messageHTML;
}

function clearChat() {
    const chatMessages = document.getElementById("chat-messages");
    chatMessages.innerHTML = "";
}

function addMessageToChat(messageJSON) {
    const chatMessages = document.getElementById("chat-messages");
    chatMessages.innerHTML += chatMessageHTML(messageJSON);
    chatMessages.scrollIntoView(false);
    chatMessages.scrollTop = chatMessages.scrollHeight - chatMessages.clientHeight;
}

function sendChat() {
    const chatTextBox = document.getElementById("chat-text-box");
    const message = chatTextBox.value;
    chatTextBox.value = "";
    const xsrfToken = document.getElementById("xsrf-token").value;
    if (ws) {
        // Using WebSockets
        socket.send(JSON.stringify({'messageType': 'chatMessage', 'message': message, 'xsrf_token': xsrfToken}));
    } else {
        // Using AJAX
        const request = new XMLHttpRequest();
        request.onreadystatechange = function () {
            if (this.readyState === 4 && this.status === 200) {
                console.log(this.response);
            }
        }
        const messageJSON = {"message": message, "xsrf_token": xsrfToken};
        request.open("POST", "/chat-messages");
        //request.setRequestHeader("Content-Type", "application/json");
        request.send(JSON.stringify(messageJSON));
    }
    chatTextBox.focus();
}

function updateChat() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            clearChat();
            const messages = JSON.parse(this.response);
            for (const message of messages) {
                addMessageToChat(message);
            }
        }
    }
    request.open("GET", "/chat-messages");
    request.send();
}

function welcome() {
    document.addEventListener("keypress", function (event) {
        if (event.code === "Enter") {
            sendChat();
        }
    });


    document.getElementById("paragraph").innerHTML += "<br/>This text was added by JavaScript 😀";
    document.getElementById("chat-text-box").focus();

    updateChat();

    if (ws) {
        initWS();
    } else {
        const videoElem = document.getElementsByClassName('video-chat')[0];
        videoElem.parentElement.removeChild(videoElem);
        setInterval(updateChat, 5000);
    }

    // use this line to start your video without having to click a button. Helpful for debugging
    // startVideo();
}