import "./App.css";

function App() {
  return (
    <div className="app">

      <div className="left-panel">
        <h2>Rue</h2>

        <div className="card">
          <h3>Character</h3>
          <p>Close Friend</p>
          <p>Trust: 79</p>
        </div>

        <div className="card">
          <h3>Memories</h3>
          <ul>
            <li>Shared Secret</li>
            <li>Mission Complete</li>
            <li>Gift Given</li>
          </ul>
        </div>
      </div>

      <div className="chat-panel">

        <div className="chat-header">
          RUE
        </div>

        <div className="chat-window">

          <div className="message rue">
            Welcome back, Jared.
          </div>

          <div className="message user">
            How are things at Gorza's Den?
          </div>

          <div className="message rue">
            The espresso machine is plotting something.
          </div>

        </div>

        <div className="chat-input">
          <input
            type="text"
            placeholder="Message Rue..."
          />

          <button>
            Send
          </button>
        </div>

      </div>

      <div className="right-panel">

        <div className="card">
          <h3>Story State</h3>

          <p>
            <strong>Location:</strong>
            {" "}Gorza's Den
          </p>

          <p>
            <strong>Scene:</strong>
            {" "}Sharing drinks while discussing RUE
          </p>
        </div>

        <div className="card">
          <h3>Quest</h3>

          <ul>
            <li>Create Shared History</li>
            <li>Improve Memory Consistency</li>
          </ul>
        </div>

        <div className="card">
          <h3>Initiatives</h3>

          <ul>
            <li>Meet At Gorza's Den</li>
          </ul>
        </div>

      </div>

    </div>
  );
}

export default App;
