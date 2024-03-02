import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import io from "socket.io-client";

const root = ReactDOM.createRoot(document.getElementById("root"));

export const SERVER_URL = "llm-agent.onrender.com"

const socket = io("wss://"+SERVER_URL);
// const socket = io("ws://127.0.0.1:8000");

root.render(<App socket={socket} />);
