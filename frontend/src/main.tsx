import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { ErrorBoundary } from "./components/ErrorBoundary";
import "./styles.css";

const rootElement = document.getElementById("root");
if (!rootElement) {
  throw new Error("Root element not found");
}

try {
  createRoot(rootElement).render(
    <StrictMode>
      <ErrorBoundary>
        <App />
      </ErrorBoundary>
    </StrictMode>,
  );
} catch (error) {
  const message = error instanceof Error ? error.message : "Unknown startup error";
  rootElement.replaceChildren();
  const shell = document.createElement("main");
  shell.className = "fatal-error";
  const heading = document.createElement("h1");
  heading.textContent = "Dairy Shop POS could not start";
  const detail = document.createElement("p");
  detail.textContent = message;
  shell.append(heading, detail);
  rootElement.appendChild(shell);
  throw error;
}
