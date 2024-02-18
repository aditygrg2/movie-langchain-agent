import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import io from "socket.io-client";

const root = ReactDOM.createRoot(document.getElementById("root"));

const socket = io("wss://llm-agent.onrender.com");

root.render(<App socket={socket} />);
