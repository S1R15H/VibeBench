# Project Guidelines: AI Coding Assistant Comparator

## 1. Project Lifecycle
The development and execution of this project will follow the **Iterative Waterfall Model**, ensuring distinct phases for framework building and actual data analysis.

### Phase A: Framework Development
1.  **Requirement Analysis:** Confirming the 8 specific tasks (a-h) and the 5 quality metrics.
2.  **System Design:** Designing the GUI and the "Test Harness" that runs generated code safely.
3.  **Implementation:** Building the orchestrator, sandbox environments (Docker), and reporting engine.
4.  **Verification:** Testing the framework itself to ensure it captures metrics accurately.

### Phase B: Experimentation & Analysis
1.  **Data Collection:** generating the code snippets using the selected AIs (e.g., Copilot, ChatGPT, Claude, Gemini).
2.  **Automated Testing:** Running the framework to compile, execute, and scan the snippets.
3.  **Manual Review:** Assessing "Code Readability" (which is subjective) and validating automated findings.
4.  **Final Reporting:** Generating the comparative matrix.

## 2. Coding Standards (for the Framework)
* **Language:** Python 3.10+ (Recommended for its rich ecosystem of text processing and testing libraries).
* **Style:** Follow PEP 8 guidelines.
* **Documentation:** All functions must have Docstrings explaining inputs and return values.
* **Error Handling:** The framework must be robust; if an AI-generated snippet crashes, the framework must *catch* it, log it, and move to the next task without exiting.

## 3. Safety Protocols
* **Sandboxing:** AI-generated code **MUST** be executed inside isolated containers (e.g., Docker) to prevent accidental damage (like infinite loops or file system deletion) to the host machine.
* **API Keys:** Never hardcode API keys for the AI tools. Use environment variables (`.env`).