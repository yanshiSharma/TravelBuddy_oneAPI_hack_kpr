var userResponses = {};
var currentMessageIndex = 0;
var userChoice = null;

function sendMessage() {
    var input = document.getElementById("messageInput");
    var message = input.value;

    if (message.trim() === "") {
        return; // Prevent sending empty message
    }

    addOutgoingMessage(message);
    input.value = ""; // Clear input

    fetch('/chatbot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            user_choice: userChoice,
            user_input: message
        }),
    })
        .then(response => response.json())
        .then(data => {
            addIncomingMessage(data.response);
            if (data.next_question) {
                addIncomingMessage(data.next_question);
            } else {
                document.getElementById('messageInput').style.display = 'none'; // Hide input if no question
            }
        })
        .catch(error => console.error('Error:', error));
}

function addOutgoingMessage(message) {
    var chatContainer = document.getElementById("chatContainer");
    var outgoingMessage = document.createElement("div");
    outgoingMessage.classList.add("message", "outgoing");
    outgoingMessage.innerHTML = `
        <img src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhwj8E__pXohJ70JOQlvENXnPedGn7SDArF0nA84pOfDxqicmX8iwdelVCIAB023O-Fo7ieKgCdNvwo1BT7u8-Q25os-9jOTcMTTNanPwwXbq-cuZEmkP0tuzy8nb17o94doiIFGm2sVkPwf8Wcb6Y-Gl0RaGK2qvweuoiH8363o9_bxHaQ5FrJ1USMwWY/s320/IMG_20240201_092300.jpg" alt="Avatar" class="message
