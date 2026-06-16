#!/usr/bin/env python3
"""
auth.py

Reusable authentication module for the AI Web Automation Agent.

Provides clean, composable functions for:
- Email / password login
- Forgot password flow + OTP triggering
- OTP entry
- Google sign-in (with popup handling support)

All functions operate on an existing Playwright Page object.
They are designed to be called from an interactive CLI or LLM-orchestrated agent.

Best practices followed:
- Prefer semantic locators (get_by_label, get_by_role, get_by_text)
- Explicit waits where necessary
- Clear return values / exceptions for caller control
- Comments for common UI variations
"""

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
import time


def perform_email_login(
    page: Page,
    email: str,
    password: str,
    email_label: str = "Email",
    password_label: str = "Password",
    login_button_text: str = "Log in",
    timeout: int = 15000,
) -> bool:
    """
    Perform email/password login on the current page.

    Returns True on apparent success (no immediate error), False otherwise.
    Caller should verify post-login state (e.g. URL change or welcome text).
    """
    try:
        # Try multiple common locator strategies
        email_field = (
            page.get_by_label(email_label, exact=False)
            .or_(page.get_by_placeholder(email_label))
            .or_(page.locator("input[type='email']"))
        )
        email_field.first.fill(email, timeout=timeout)

        password_field = (
            page.get_by_label(password_label, exact=False)
            .or_(page.get_by_placeholder(password_label))
            .or_(page.locator("input[type='password']"))
        )
        password_field.first.fill(password, timeout=timeout)

        # Click login button
        login_btn = (
            page.get_by_role("button", name=login_button_text, exact=False)
            .or_(page.get_by_text(login_button_text, exact=False))
        )
        login_btn.first.click(timeout=timeout)

        # Wait for navigation or network idle after submit
        page.wait_for_load_state("networkidle", timeout=timeout)
        print("[auth] Email login form submitted.")
        return True

    except PlaywrightTimeoutError:
        print("[auth] Timeout during email login. Check selectors or page state.")
        return False
    except Exception as e:
        print(f"[auth] Error during email login: {e}")
        return False


def trigger_forgot_password_otp(
    page: Page,
    email: str,
    forgot_link_text: str = "Forgot password",
    email_field_label: str = "Email",
    submit_button_text: str = "Submit",
    timeout: int = 15000,
) -> bool:
    """
    Navigate to forgot-password flow and trigger OTP delivery for the given email.

    Returns True if the trigger appears successful.
    The actual OTP will be sent to the user's email/SMS.
    """
    try:
        # Click forgot password link / button
        forgot_link = (
            page.get_by_text(forgot_link_text, exact=False)
            .or_(page.get_by_role("link", name=forgot_link_text, exact=False))
        )
        if forgot_link.count() > 0:
            forgot_link.first.click(timeout=timeout)
        else:
            print("[auth] 'Forgot password' link not found on current page.")
            return False

        page.wait_for_load_state("domcontentloaded", timeout=timeout)

        # Fill email on the reset form
        email_field = (
            page.get_by_label(email_field_label, exact=False)
            .or_(page.get_by_placeholder(email_field_label))
            .or_(page.locator("input[type='email']"))
        )
        email_field.first.fill(email, timeout=timeout)

        # Submit the form to trigger OTP
        submit_btn = (
            page.get_by_role("button", name=submit_button_text, exact=False)
            .or_(page.get_by_text(submit_button_text, exact=False))
        )
        submit_btn.first.click(timeout=timeout)

        page.wait_for_load_state("networkidle", timeout=timeout)
        print(f"[auth] Forgot password form submitted for {email}. OTP should have been sent.")
        return True

    except PlaywrightTimeoutError:
        print("[auth] Timeout while triggering OTP.")
        return False
    except Exception as e:
        print(f"[auth] Error triggering forgot-password OTP: {e}")
        return False


def enter_otp(
    page: Page,
    otp: str,
    otp_label: str = "OTP",
    verify_button_text: str = "Verify",
    timeout: int = 15000,
) -> bool:
    """
    Enter the user-provided OTP and submit verification.

    Call this after the user has received and supplied the OTP code.
    """
    try:
        otp_field = (
            page.get_by_label(otp_label, exact=False)
            .or_(page.get_by_placeholder(otp_label))
            .or_(page.locator("input[autocomplete*='one-time-code']"))
            .or_(page.locator("input[name*='otp']"))
        )
        otp_field.first.fill(otp, timeout=timeout)

        verify_btn = (
            page.get_by_role("button", name=verify_button_text, exact=False)
            .or_(page.get_by_text(verify_button_text, exact=False))
        )
        verify_btn.first.click(timeout=timeout)

        page.wait_for_load_state("networkidle", timeout=timeout)
        print("[auth] OTP submitted.")
        return True

    except PlaywrightTimeoutError:
        print("[auth] Timeout while entering OTP.")
        return False
    except Exception as e:
        print(f"[auth] Error entering OTP: {e}")
        return False


def perform_google_signin(
    page: Page,
    button_text: str = "Continue with Google",
    timeout: int = 20000,
) -> bool:
    """
    Click the Google sign-in button and handle the resulting popup or redirect.

    Note: Full automated completion of Google OAuth often requires
    user confirmation or pre-existing session. This function handles
    the initial click and basic popup detection.
    For production use, combine with persistent context and optional
    human-in-the-loop confirmation.
    """
    try:
        google_btn = (
            page.get_by_role("button", name=button_text, exact=False)
            .or_(page.get_by_text(button_text, exact=False))
        )

        if google_btn.count() == 0:
            print("[auth] Google sign-in button not found.")
            return False

        # Click and wait for popup
        with page.expect_popup() as popup_info:
            google_btn.first.click(timeout=timeout)

        popup_page = popup_info.value
        print("[auth] Google popup opened. Waiting for user interaction or redirect...")

        # Give time for user to complete Google auth or for redirect to happen
        # In a real agent this can be improved with LLM observation or explicit wait
        popup_page.wait_for_load_state("domcontentloaded", timeout=timeout)

        # Optional: close popup if it redirects back automatically
        # Many flows close the popup themselves after successful auth
        print("[auth] Google sign-in flow initiated. Check browser for completion.")
        return True

    except PlaywrightTimeoutError:
        print("[auth] Timeout during Google sign-in popup handling.")
        return False
    except Exception as e:
        print(f"[auth] Error during Google sign-in: {e}")
        return False
