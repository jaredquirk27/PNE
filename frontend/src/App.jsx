import { useState } from "react";
import "./App.css";

function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([
    {
      sender: "Rue",
      text: "Welcome back, Jared."
    }
  ]);

  async function sendMessage() {
    if (!message.trim()) return;

    const userMessage = {
      sender: "You",
      text: message
    };

    setMessages(prev => [...prev, userMessage]);

    const currentMessage = message;

    setMessage("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/chat",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            character: "Rue",
            message: currentMessage
          })
        }
      );

      const data = await response.json();

      setMessages(prev => [
        ...prev,
        {
          sender: "Rue",
          text: data.response
        }
      ]);
    } catch (error) {
      console.error(error);

      setMessages(prev => [
        ...prev,
        {
          sender: "System",
          text: "Unable to contact backend."
        }
      ]);
    }
  }

  return (
    <div className="app">

      <div className="header">
        <h1>RUE</h1>
      </div>

      <div className="chat-window">

        {messages.map((msg, index) => (
          <div
            key={index}
            className={
              msg.sender === "You"
                ? "user-message"
                : "rue-message"
            }
          >
            <strong>{msg.sender}: </strong>
            {msg.text}
          </div>
        ))}

      </div>

      <div className="input-area">

        <input
          value={message}
          onChange={(e) =>
            setMessage(e.target.value)
          }
          placeholder="Message Rue..."
        />

        <button
          onClick={sendMessage}
        >
          Send
        </button>

      </div>

    </div>
  );
}

export default App;