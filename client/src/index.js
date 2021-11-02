import React from "react";
import ReactDOM from "react-dom";
import logo from "./logo.svg";
import "./index.css";


function App() {
  return (
    <div className="App">
      <img src={logo} className="App-logo" alt="logo" />
    </div>
  );
}


ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById("root")
);
