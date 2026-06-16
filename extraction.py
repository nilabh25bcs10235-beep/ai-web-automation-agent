#!/usr/bin/env python3
"""
extraction.py

Improved structured data extraction utilities for the AI Web Automation Agent.

Focuses on reliable extraction of:
- Tables → list of dictionaries (JSON-ready)
- Specific sections by semantic description or locator
- General page text with optional truncation

These functions complement the basic extraction in browser_agent.py
and are designed to be called from the interactive CLI or LLM agent.
"""

from playwright.sync_api import Page
import json


def extract_table_as_json(
    page: Page,
    table_locator: str = "table",
    max_rows: int = 50,
) -> list[dict]:
    """
    Extract the first matching table on the page as a list of dictionaries.

    Assumes the first row is a header. Returns clean JSON-serializable data.
    """
    try:
        table = page.locator(table_locator).first
        if table.count() == 0:
            print("[extraction] No table found with the given locator.")
            return []

        # Get all rows
        rows = table.locator("tr").all()
        if len(rows) < 2:
            print("[extraction] Table has insufficient rows for header + data.")
            return []

        # Extract header
        header_cells = rows[0].locator("th, td").all_inner_texts()
        headers = [h.strip() for h in header_cells if h.strip()]

        data = []
        for row in rows[1 : 1 + max_rows]:
            cells = row.locator("td, th").all_inner_texts()
            if len(cells) == len(headers):
                row_dict = {headers[i]: cells[i].strip() for i in range(len(headers))}
                data.append(row_dict)

        print(f"[extraction] Extracted {len(data)} rows from table.")
        return data

    except Exception as e:
        print(f"[extraction] Error extracting table: {e}")
        return []


def extract_section_text(
    page: Page,
    section_description: str | None = None,
    section_locator: str | None = None,
    max_chars: int = 2000,
) -> str:
    """
    Extract text from a specific section of the page.

    You can provide either a semantic description (future LLM use) or a direct locator.
    """
    try:
        if section_locator:
            locator = page.locator(section_locator).first
        elif section_description:
            # Simple heuristic: try to find by text or common section containers
            locator = (
                page.get_by_text(section_description, exact=False)
                .or_(page.locator(f"[aria-label*='{section_description}']"))
                .or_(page.locator("main, section, div").filter(has_text=section_description))
                .first
            )
        else:
            locator = page.locator("main, article, .content, #content").first

        if locator.count() == 0:
            text = page.locator("body").inner_text()[:max_chars]
        else:
            text = locator.inner_text()[:max_chars]

        return text.strip()

    except Exception as e:
        print(f"[extraction] Error extracting section: {e}")
        return page.locator("body").inner_text()[:max_chars].strip()


def extract_page_summary(page: Page, max_chars: int = 1500) -> dict:
    """
    Return a compact summary of the current page state (title, url, headings, body snippet).
    Useful for LLM context or debugging.
    """
    try:
        title = page.title()
        url = page.url
        h1 = page.locator("h1").first.inner_text() if page.locator("h1").count() > 0 else ""
        body_snippet = page.locator("body").inner_text()[:max_chars].strip()

        return {
            "title": title,
            "url": url,
            "main_heading": h1,
            "body_snippet": body_snippet,
        }
    except Exception as e:
        return {"error": str(e)}
