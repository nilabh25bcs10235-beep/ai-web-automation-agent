# AI Web Automation Agent

**A custom AI-powered browser automation agent for login flows, OTP handling, natural language navigation, screenshots, and structured text/data extraction.**

This project is a learning-oriented implementation inspired by [Skyvern](https://github.com/Skyvern-AI/skyvern). It is designed to fulfill requirements such as:

- Logging into websites using a provided email address.
- Navigating to "forgot password" flows and triggering OTP delivery.
- Accepting user-supplied OTP codes or confirmations for Google sign-in / OAuth flows.
- Executing post-authentication navigation and tasks based on natural language or structured instructions.
- Capturing screenshots and extracting specific lines of text or tabular data.

**Important**: This tool is intended exclusively for use on websites and accounts where you have explicit authorization. Always comply with applicable terms of service, robots.txt, rate limits, and legal requirements. Unauthorized access or misuse may violate laws and platform policies. The project maintainers assume no responsibility for improper use.

## Project Status

- Repository initialized with core structure.
- Phase 1 (Core browser control with Playwright) started.
- LLM integration, advanced login/OTP modules, and persistent session management planned for subsequent phases.

## Proposed Development Phases

1. **Phase 1: Foundational Browser Automation**  
   Reliable navigation, screenshot capture, basic DOM-based text extraction, and element interaction using Playwright. Interactive command examples.

2. **Phase 2: Login & Authentication Flows**  
   Modular functions for email/password login, forgot-password + OTP trigger + entry (user provides OTP), and Google "Continue with" button handling with popup/session support.

3. **Phase 3: LLM-Driven Agent**  
   Integration of a large language model (Grok API, Ollama local models, or compatible provider via LiteLLM) to interpret natural language instructions, plan multi-step actions, observe page state, and execute or suggest next steps. Human-in-the-loop support for sensitive actions (e.g., OTP entry confirmation).

4. **Phase 4: Robustness & Advanced Features**  
   Error recovery, retry logic, stealth techniques, persistent browser contexts/cookies, structured data extraction with JSON schemas, file downloads, and support for complex multi-page workflows.

5. **Phase 5: Interface & Deployment (Optional)**  
   CLI enhancements, simple web UI (FastAPI + React), Docker packaging, or integration into larger personal productivity tools. Exploration of local LLM deployment on resource-constrained environments.

## Tech Stack (Current & Planned)

- **Core**: Python 3.11+, Playwright (browser automation)
- **Configuration**: python-dotenv
- **Future LLM Layer**: LiteLLM (unified interface), direct Grok / OpenAI / Anthropic clients, or Ollama for local models
- **Optional Backend/UI**: FastAPI, React (for dashboard or command interface)
- **Data Handling**: JSON schema validation for extraction, Pillow (if image processing required)

## Getting Started

### Prerequisites
- Python 3.11 or higher
- Git
- A modern browser (Chromium recommended)

### Installation

```bash
git clone https://github.com/nilabh25bcs10235-beep/ai-web-automation-agent.git
cd ai-web-automation-agent

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (first time only)
playwright install chromium
```

### Running the Starter Agent

The initial `browser_agent.py` demonstrates navigation to any URL, full-page screenshot capture, and basic text extraction.

```bash
python browser_agent.py --url "https://example.com" --headless
```

- Omit `--headless` to see the browser window (useful during development).
- Use `--no-screenshot` or `--no-extract` to disable specific features.
- Screenshots are saved to the `artifacts/` directory.

### Next Steps After Running the Example

1. Review the extensive comments and TODOs inside `browser_agent.py`.
2. Extend the `run_agent` function or add new modules (e.g., `auth.py`) for login logic using Playwright locators such as `page.get_by_label("Email").fill(...)` and `page.get_by_role("button", name=...).click()`.
3. Implement an interactive loop that accepts commands like "trigger forgot password", "enter OTP: 123456", or "navigate to billing and extract table data".
4. Add LLM planning once comfortable with the Playwright layer.

## Safety, Security & Best Practices

- Never hard-code credentials or OTPs in source code. Use environment variables or secure vaults.
- For Google OAuth flows, prefer persistent contexts or user-confirmed steps rather than fully automated credential entry.
- Test on non-production or demo sites first.
- Monitor for CAPTCHAs, rate limits, and anti-automation measures; implement appropriate delays and randomization where needed.
- Review and respect each website’s robots.txt and terms of service.

## References & Inspiration

- [Skyvern](https://github.com/Skyvern-AI/skyvern) — Mature open-source LLM + computer vision browser agent (strongly recommended for production use or as a reference implementation).
- [Playwright Documentation](https://playwright.dev/python/)
- Browser automation best practices and ethical guidelines.

## Contributing / Iteration

This is an active learning project. Suggestions for improvements, new modules (e.g., OTP handler, Google auth helper, LLM action planner), bug reports, or pull requests are welcome. Please open an issue to discuss significant changes.

---

*Built as a personal learning and productivity project. Use responsibly.*