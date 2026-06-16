#!/usr/bin/env python3
"""
Basic Browser Automation Agent (Phase 1 Starter)

Demonstrates core capabilities required for the project:
- Navigation to any URL
- Screenshot capture (full page)
- Basic text / heading extraction

This script serves as the foundation. Extensive comments and TODO sections
indicate how to extend it for email login, forgot-password + OTP flows,
Google sign-in, natural language command handling, and LLM integration.

Run with: python browser_agent.py --url "https://example.com"

Safety: Only use on sites where you have explicit authorization.
"""

import argparse
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env if present

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
except ImportError:
    print("Playwright not installed. Run: pip install -r requirements.txt && playwright install chromium")
    raise


def run_agent(
    url: str,
    take_screenshot: bool = True,
    extract_text: bool = True,
    headless: bool = False,
) -> None:
    """
    Launch a browser, navigate to the target URL, perform requested actions,
    and cleanly close the browser.

    Args:
        url: Target website URL (must include protocol, e.g. https://)
        take_screenshot: Whether to capture a full-page screenshot
        extract_text: Whether to extract page title, main heading, and body snippet
        headless: Run browser without visible window (useful for automation)
    """
    print(f"Starting browser automation agent...")
    print(f"Target URL: {url}")

    with sync_playwright() as p:
        # Launch Chromium. Use firefox or webkit if preferred.
        browser = p.chromium.launch(
            headless=headless,
            args=["--disable-blink-features=AutomationControlled"]  # Basic anti-detection hint
        )

        # Create a new browser context with realistic settings
        context = browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            locale="en-US",
            timezone_id="Asia/Kolkata",  # Adjust to your location if desired
        )

        page = context.new_page()

        try:
            print("Navigating to page...")
            page.goto(url, wait_until="domcontentloaded", timeout=45000)

            # Wait for network to be mostly idle (helps with dynamic sites)
            try:
                page.wait_for_load_state("networkidle", timeout=10000)
            except PlaywrightTimeoutError:
                pass  # Non-critical

            print(f"Page loaded successfully. Title: {page.title()}")

            if take_screenshot:
                os.makedirs("artifacts", exist_ok=True)
                screenshot_path = os.path.join("artifacts", "screenshot.png")
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"Full-page screenshot saved to: {screenshot_path}")

            if extract_text:
                print("\n=== Extracted Page Information ===")

                # Page title
                title = page.title()
                print(f"Page Title: {title}")

                # Main heading (first h1)
                h1_locator = page.locator("h1").first
                if h1_locator.count() > 0:
                    heading = h1_locator.inner_text()
                    print(f"Main Heading (H1): {heading}")
                else:
                    print("No H1 heading found on page.")

                # Body text snippet (first ~800 characters)
                body_text = page.locator("body").inner_text()[:800].strip()
                print(f"\nBody text snippet (first 800 chars):\n{body_text}...")

                # TODO: Add more sophisticated extraction here, e.g.:
                # - page.locator("table").all_inner_texts() for tabular data
                # - Custom locators for specific sections ("recent transactions", "invoice list")
                # - Structured output using JSON schema (future LLM-assisted)

            # ============================================================
            # TODO: LOGIN & AUTHENTICATION MODULE (Phase 2)
            # ============================================================
            # Example skeleton for email login (uncomment and adapt):
            #
            # email = "your-email@example.com"  # Load from env or secure input
            # password = os.getenv("TARGET_SITE_PASSWORD")
            #
            # email_field = page.get_by_label("Email") or page.get_by_placeholder("Email")
            # email_field.fill(email)
            #
            # password_field = page.get_by_label("Password")
            # password_field.fill(password)
            #
            # page.get_by_role("button", name="Log in").click()
            # page.wait_for_load_state("networkidle")
            # print("Login attempt completed.")

            # ------------------------------------------------------------
            # Forgot password + OTP flow example:
            # 1. Click "Forgot password?" link
            # 2. Enter email and submit to trigger OTP
            # 3. User provides OTP via console / UI / API
            # 4. Enter OTP and submit
            #
            # page.get_by_text("Forgot password").click()
            # page.get_by_label("Email").fill(email)
            # page.get_by_role("button", name="Submit").click()
            # print("OTP triggered. Please check your email/SMS.")
            #
            # otp = input("Enter the OTP you received: ").strip()
            # page.get_by_label("OTP Code").fill(otp)
            # page.get_by_role("button", name="Verify").click()

            # ------------------------------------------------------------
            # Google sign-in example:
            # page.get_by_role("button", name="Continue with Google").click()
            # # Handle popup or redirect. For full automation, combine with
            # # persistent context or user confirmation ("yes" input).
            # # Often requires human-in-the-loop for security prompts.

            print("\n=== Agent run completed successfully ===")

        except PlaywrightTimeoutError as e:
            print(f"Timeout error: {e}. The page may be slow or blocked.")
        except Exception as e:
            print(f"Unexpected error occurred: {e}")
            # In production agent: log error, take failure screenshot, retry logic
        finally:
            print("Closing browser...")
            browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Basic Web Automation Agent - Phase 1",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  python browser_agent.py --url "https://example.com"
  python browser_agent.py --url "https://the-internet.herokuapp.com/login" --no-headless
        """,
    )
    parser.add_argument(
        "--url", required=True, help="Target URL (include https://)"
    )
    parser.add_argument(
        "--no-screenshot", action="store_true", help="Disable screenshot capture"
    )
    parser.add_argument(
        "--no-extract", action="store_true", help="Disable text extraction"
    )
    parser.add_argument(
        "--headless", action="store_true", help="Run browser in headless mode (no visible window)"
    )

    args = parser.parse_args()

    run_agent(
        url=args.url,
        take_screenshot=not args.no_screenshot,
        extract_text=not args.no_extract,
        headless=args.headless,
    )
