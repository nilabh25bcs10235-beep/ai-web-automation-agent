# AI Web Automation Agent

**A custom AI-powered browser automation agent for login flows, OTP handling, natural language navigation, screenshots, and structured text/data extraction.**

This project is a learning-oriented implementation inspired by [Skyvern](https://github.com/Skyvern-AI/skyvern). It is designed to fulfill requirements such as:

- Logging into websites using a provided email address.
- Navigating to "forgot password" flows and triggering OTP delivery.
- Accepting user-supplied OTP codes or confirmations for Google sign-in / OAuth flows.
- Executing post-authentication navigation and tasks based on natural language or structured instructions.
- Capturing screenshots and extracting specific lines of text or tabular data.

**Important**: This tool is intended exclusively for use on websites and accounts where you have explicit authorization. Always comply with applicable terms of service, robots.txt, rate limits, and legal requirements. Unauthorized access or misuse may violate laws and platform policies. The project maintainers assume no responsibility for improper use.

## Current Status (June 2026)

**Major update completed**: Dedicated authentication module, interactive CLI with hybrid command parsing, persistent sessions, and improved structured extraction are now implemented.

### What is Working Now

- `auth.py` — Reusable functions for email login, forgot-password + OTP trigger, OTP entry, and Google sign-in (with popup handling).
- `extraction.py` — Table extraction to clean JSON, section text extraction, and page summary utilities.
- `interactive_cli.py` — Full interactive command-line agent featuring:
  - Persistent browser context + cookie/storage state saving & loading (`storage_state.json` + `browser_data/` folder).
  - Natural-language-style command input loop.
  - Hybrid parser: robust rule-based matching + optional LiteLLM integration for true natural language understanding.
  - Direct integration of auth and extraction modules.
  - Session persistence across multiple commands without re-authentication.

You can now run a single long-lived browser session and issue commands sequentially (e.g., trigger OTP → enter the code you received → navigate → extract table).

## Project Phases

1. **Phase 1 (Complete)**: Core Playwright navigation, screenshots, basic extraction.
2. **Phase 2 (Complete)**: Reusable auth flows + interactive CLI + persistence + structured extraction.
3. **Phase 3 (In Progress)**: Full LLM-driven planning and more robust natural language understanding (LiteLLM / Grok / Ollama ready).
4. **Phase 4+**: Error recovery, advanced stealth, UI layer, production hardening.

## Getting Started

### 1. Installation

```bash
git clone https://github.com/nilabh25bcs10235-beep/ai-web-automation-agent.git
cd ai-web-automation-agent

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### 2. (Optional but Recommended) Enable LLM Parsing

```bash
pip install litellm
```

Create a `.env` file (or export variables):

```env
LITELLM_MODEL=ollama/llama3.2          # Local via Ollama (recommended for privacy)
# LITELLM_MODEL=xai/grok-2               # xAI Grok (set XAI_API_KEY)
# LITELLM_MODEL=gpt-4o-mini
```

Start Ollama (if using local models) before running the CLI.

### 3. Run the Interactive Agent

```bash
python interactive_cli.py
```

The agent will open a browser window and present a prompt (`>`). Type commands in natural language.

### Example Commands You Can Try

```text
> navigate to https://example.com
> login with email test@example.com password MySecret123
> trigger forgot password for test@example.com
> enter otp 456789
> click sign in with google
> take screenshot
> extract the main table as json
> go to dashboard and show summary
> navigate to https://the-internet.herokuapp.com/tables
> extract table
> save session
> exit
```

After most actions the agent prints a quick page summary (title + URL).

Type `exit` (or Ctrl+C) to cleanly save the session and close.

### Session Persistence

- Cookies, localStorage, and some site data are saved automatically on exit or `save session` command.
- On next run the browser re-opens with the previous session (no need to log in again for many sites).
- Delete `storage_state.json` and the `browser_data/` folder to start fresh.

## Module Overview

- `auth.py` — All authentication logic (email, OTP, Google). Import and call the functions directly from your own scripts if preferred.
- `extraction.py` — Clean table → JSON, section extraction, page summaries.
- `interactive_cli.py` — The full interactive experience (recommended entry point).
- `browser_agent.py` — Original simple non-interactive starter (still useful for one-off scripts).

## Safety & Best Practices

- Never commit credentials, OTPs, or `storage_state.json`.
- For Google OAuth, the current implementation handles the initial click and popup; full automated completion usually benefits from user presence or pre-saved sessions.
- Always verify the current page state after login/OTP steps.
- Use the `save session` command before exiting long-running tasks.

## Next Development Priorities

- Improve LLM prompt engineering and structured output reliability.
- Add more robust entity extraction (email, OTP, target URLs) in the rule-based parser.
- Support for multi-step workflows defined in a single command.
- Optional richer CLI (Rich library) or simple web UI.
- Better error recovery and retry logic.

## References

- [Skyvern](https://github.com/Skyvern-AI/skyvern)
- Playwright Python docs

---

*Use responsibly and only on authorized sites.*