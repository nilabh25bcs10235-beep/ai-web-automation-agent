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
    screenshot_path: str = None,
) -> dict:
    """
    Launch a browser, navigate to the target URL, perform requested actions,
    and cleanly close the browser.

    Returns a structured result dict (useful for API / scripting in future rounds).

    Args:
        url: Target website URL (must include protocol, e.g. https://)
        take_screenshot: Whether to capture a full-page screenshot
        extract_text: Whether to extract page title, main heading, and body snippet
        headless: Run browser without visible window (useful for automation)
        screenshot_path: Optional custom path for screenshot. Defaults to artifacts/screenshot.png
    """
    print(f"Starting browser automation agent...")
    print(f"Target URL: {url}")

    result = {
        "success": False,
        "url": url,
        "title": None,
        "heading": None,
        "body_snippet": None,
        "screenshot_path": None,
        "error": None,
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            locale="en-US",
            timezone_id="Asia/Kolkata",
        )

        page = context.new_page()

        try:
            print("Navigating to page...")
            page.goto(url, wait_until="domcontentloaded", timeout=45000)

            try:
                page.wait_for_load_state("networkidle", timeout=10000)
            except PlaywrightTimeoutError:
                pass

            result["title"] = page.title()
            print(f"Page loaded successfully. Title: {result['title']}")

            if take_screenshot:
                if screenshot_path is None:
                    os.makedirs("artifacts", exist_ok=True)
                    screenshot_path = os.path.join("artifacts", "screenshot.png")
                page.screenshot(path=screenshot_path, full_page=True)
                result["screenshot_path"] = screenshot_path
                print(f"Full-page screenshot saved to: {screenshot_path}")

            if extract_text:
                print("\n=== Extracted Page Information ===")

                title = page.title()
                result["title"] = title
                print(f"Page Title: {title}")

                h1_locator = page.locator("h1").first
                if h1_locator.count() > 0:
                    heading = h1_locator.inner_text()
                    result["heading"] = heading
                    print(f"Main Heading (H1): {heading}")
                else:
                    print("No H1 heading found on page.")

                body_text = page.locator("body").inner_text()[:800].strip()
                result["body_snippet"] = body_text
                print(f"\nBody text snippet (first 800 chars):\n{body_text}...")

            result["success"] = True
            print("\n=== Agent run completed successfully ===")

        except PlaywrightTimeoutError as e:
            result["error"] = f"Timeout error: {e}"
            print(result["error"])
        except Exception as e:
            result["error"] = str(e)
            print(f"Unexpected error occurred: {e}")
        finally:
            print("Closing browser...")
            browser.close()

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Basic Web Automation Agent - Phase 1",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  python browser_agent.py --url "https://example.com"
  python browser_agent.py --url "https://the-internet.herokuapp.com/login" --headless
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
    parser.add_argument(
        "--screenshot-path", help="Custom path to save screenshot (default: artifacts/screenshot.png)"
    )

    args = parser.parse_args()

    result = run_agent(
        url=args.url,
        take_screenshot=not args.no_screenshot,
        extract_text=not args.no_extract,
        headless=args.headless,
        screenshot_path=args.screenshot_path,
    )
    print("\n[Result]", result)
