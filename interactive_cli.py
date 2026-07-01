#!/usr/bin/env python3
"""
interactive_cli.py

Main entry point for the interactive AI Web Automation Agent.

Features implemented in this iteration:
- Persistent browser context with cookie / storage state saving & loading
- Reusable auth flows (email login, forgot-password + OTP, Google sign-in)
- Improved structured extraction (tables as JSON, section text)
- Interactive command loop accepting natural-language-style instructions
- Hybrid command parser: robust keyword matching + optional LiteLLM integration
- Session persistence across commands without repeated re-authentication

Usage:
  python interactive_cli.py                     # Interactive mode
  python interactive_cli.py --command "navigate to https://example.com and take screenshot"

Then type commands such as:
  login with email user@example.com password MyPass123
  trigger forgot password for user@example.com
  enter otp 123456
  click sign in with google
  take screenshot
  extract main table as json
  go to dashboard and show summary
  navigate to https://example.com/billing
  save session
  exit
"""

import os
import json
import argparse
from dotenv import load_dotenv

load_dotenv()

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
except ImportError:
    print("Playwright is required. Install with: pip install -r requirements.txt")
    raise

# Local modules
from auth import (
    perform_email_login,
    trigger_forgot_password_otp,
    enter_otp,
    perform_google_signin,
)
from extraction import (
    extract_table_as_json,
    extract_section_text,
    extract_page_summary,
)


STORAGE_STATE_PATH = "storage_state.json"


def get_persistent_context(p, headless: bool = False):
    """Create or restore a browser context with saved cookies/storage."""
    if os.path.exists(STORAGE_STATE_PATH):
        print(f"[cli] Loading existing session from {STORAGE_STATE_PATH}")
        context = p.chromium.launch_persistent_context(
            user_data_dir="./browser_data",
            storage_state=STORAGE_STATE_PATH,
            headless=headless,
            viewport={"width": 1366, "height": 768},
        )
    else:
        print("[cli] Starting fresh browser session (no saved state found)")
        context = p.chromium.launch_persistent_context(
            user_data_dir="./browser_data",
            headless=headless,
            viewport={"width": 1366, "height": 768},
        )
    return context


def save_session(context):
    """Save current storage state (cookies, localStorage, etc.)."""
    try:
        context.storage_state(path=STORAGE_STATE_PATH)
        print(f"[cli] Session saved to {STORAGE_STATE_PATH}")
    except Exception as e:
        print(f"[cli] Failed to save session: {e}")


def parse_command(command: str) -> dict:
    """
    Hybrid parser: tries LiteLLM first (if configured), falls back to keyword rules.
    """
    cmd_lower = command.lower().strip()

    model = os.getenv("LITELLM_MODEL")
    if model:
        try:
            import litellm
            system_prompt = (
                "You are a precise browser automation command parser. "
                "Convert the user's natural language instruction into a single JSON object "
                "with keys: action (one of: login, trigger_otp, enter_otp, google_signin, "
                "screenshot, extract_table, extract_section, navigate, save_session, exit), "
                "plus any required parameters (email, password, otp, url, description). "
                "Respond with ONLY valid JSON. No extra text."
            )
            response = litellm.completion(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": command},
                ],
                temperature=0.0,
                max_tokens=300,
            )
            content = response.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content.split("```json")[1].split("```")[0].strip()
            parsed = json.loads(content)
            if isinstance(parsed, dict) and "action" in parsed:
                print("[cli] Parsed via LLM")
                return parsed
        except Exception as e:
            print(f"[cli] LLM parsing failed, falling back to rules: {e}")

    # Rule-based fallback
    if "login" in cmd_lower and "email" in cmd_lower:
        import re
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}", command)
        email = email_match.group(0) if email_match else ""
        pw_match = re.search(r"password\s+([\w@#$%^&*!]+)", cmd_lower)
        password = pw_match.group(1) if pw_match else ""
        return {"action": "login", "email": email, "password": password}

    if "forgot password" in cmd_lower or "trigger otp" in cmd_lower:
        import re
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}", command)
        email = email_match.group(0) if email_match else ""
        return {"action": "trigger_otp", "email": email}

    if "enter otp" in cmd_lower or "otp" in cmd_lower:
        import re
        otp_match = re.search(r"\b(\d{4,8})\b", command)
        otp = otp_match.group(1) if otp_match else ""
        return {"action": "enter_otp", "otp": otp}

    if "google" in cmd_lower and ("sign" in cmd_lower or "login" in cmd_lower or "continue" in cmd_lower):
        return {"action": "google_signin"}

    if "screenshot" in cmd_lower or "take ss" in cmd_lower:
        return {"action": "screenshot"}

    if "extract" in cmd_lower and "table" in cmd_lower:
        return {"action": "extract_table"}

    if "extract" in cmd_lower and ("section" in cmd_lower or "summary" in cmd_lower):
        desc = command.split("extract")[-1].strip() if "extract" in cmd_lower else "main content"
        return {"action": "extract_section", "description": desc}

    if "navigate" in cmd_lower or "go to" in cmd_lower:
        import re
        url_match = re.search(r"https?://[^\s]+", command)
        url = url_match.group(0) if url_match else ""
        return {"action": "navigate", "url": url}

    if "save session" in cmd_lower or "save cookies" in cmd_lower:
        return {"action": "save_session"}

    if cmd_lower in ("exit", "quit", "q"):
        return {"action": "exit"}

    return {"action": "unknown", "raw": command}


def dispatch_action(page, action: dict, context):
    """Execute the parsed action on the current page/context."""
    act = action.get("action")

    if act == "login":
        email = action.get("email", "")
        password = action.get("password", "")
        if email and password:
            perform_email_login(page, email, password)
        else:
            print("[cli] Please provide both email and password in the command.")

    elif act == "trigger_otp":
        email = action.get("email", "")
        if email:
            trigger_forgot_password_otp(page, email)
        else:
            print("[cli] Please include the email address for OTP trigger.")

    elif act == "enter_otp":
        otp = action.get("otp", "")
        if otp:
            enter_otp(page, otp)
        else:
            print("[cli] Please provide the OTP code.")

    elif act == "google_signin":
        perform_google_signin(page)

    elif act == "screenshot":
        os.makedirs("artifacts", exist_ok=True)
        path = "artifacts/screenshot.png"
        page.screenshot(path=path, full_page=True)
        print(f"[cli] Screenshot saved to {path}")

    elif act == "extract_table":
        data = extract_table_as_json(page)
        if data:
            print(json.dumps(data, indent=2))
            with open("artifacts/extracted_table.json", "w") as f:
                json.dump(data, f, indent=2)
            print("[cli] Table also saved to artifacts/extracted_table.json")

    elif act == "extract_section":
        desc = action.get("description", "main content")
        text = extract_section_text(page, section_description=desc)
        print(f"\n--- {desc} ---\n{text[:1500]}\n")

    elif act == "navigate":
        url = action.get("url")
        if url:
            print(f"[cli] Navigating to {url}...")
            page.goto(url, wait_until="domcontentloaded")
            print(f"[cli] Current page title: {page.title()}")
        else:
            print("[cli] No URL found in command.")

    elif act == "save_session":
        save_session(context)

    elif act == "exit":
        save_session(context)
        print("[cli] Session saved. Goodbye!")
        return "exit"

    elif act == "unknown":
        print(f"[cli] Unrecognized command: {action.get('raw')}")
        print("Try: login, forgot password, enter otp, google, screenshot, extract table, navigate https://..., save session, exit")

    return None


def run_single_command(command: str, headless: bool = False):
    """Run a single command non-interactively and exit (useful for scripting and deployment)."""
    print(f"[cli] Running single command: {command}")

    with sync_playwright() as p:
        context = get_persistent_context(p, headless=headless)
        page = context.new_page()

        action = parse_command(command)
        result = dispatch_action(page, action, context)

        if action.get("action") not in ("exit", "save_session"):
            try:
                summary = extract_page_summary(page)
                print(f"[page] {summary.get('title', '')} | {summary.get('url', '')[:60]}...")
            except:
                pass

        if result != "exit":
            save_session(context)

        context.close()
        print("[cli] Single command completed.")


def run_interactive_cli():
    parser = argparse.ArgumentParser(description="Interactive AI Web Automation Agent CLI")
    parser.add_argument("--headless", action="store_true", help="Run browser headless")
    parser.add_argument("--command", help="Run a single command non-interactively and exit")
    args = parser.parse_args()

    if args.command:
        run_single_command(args.command, headless=args.headless)
        return

    # Interactive mode (original behavior)
    print("=== AI Web Automation Agent - Interactive CLI ===")
    print("Type natural-language commands. Type 'exit' to quit and save session.\n")

    with sync_playwright() as p:
        context = get_persistent_context(p, headless=args.headless)
        page = context.new_page()

        print("Browser ready. Current page:", page.url or "about:blank")

        while True:
            try:
                user_input = input("\n> ").strip()
                if not user_input:
                    continue

                action = parse_command(user_input)
                result = dispatch_action(page, action, context)

                if result == "exit":
                    break

                if action.get("action") not in ("exit", "save_session"):
                    try:
                        summary = extract_page_summary(page)
                        print(f"[page] {summary.get('title', '')} | {summary.get('url', '')[:60]}...")
                    except:
                        pass

            except KeyboardInterrupt:
                print("\n[cli] Interrupted by user. Saving session...")
                save_session(context)
                break
            except Exception as e:
                print(f"[cli] Error: {e}")

        context.close()
        print("Browser closed.")


if __name__ == "__main__":
    run_interactive_cli()
