import html
import re
import unicodedata


def sanitize_text(text: str) -> str:
    """Normalize AI text for safe display/export."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
        "\u00a0": " ",
        "\u2022": "-",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.strip()


def pdf_safe_text(text: str) -> str:
    """Make text safe for built-in FPDF fonts."""
    text = sanitize_text(text)
    return text.encode("latin-1", errors="replace").decode("latin-1")


def terms_list(terms: str) -> list[str]:
    return [item.strip() for item in terms.split(";") if item.strip()]


def html_preview(text: str) -> str:
    """Convert plain legal text into escaped HTML with simple heading support."""
    safe = html.escape(sanitize_text(text))
    blocks = []
    for raw in safe.split("\n"):
        line = raw.strip()
        if not line:
            blocks.append("<div class='spacer'></div>")
            continue
        if re.match(r"^\d+[\.\)]\s+", line) or line.upper() == line and len(line) < 100:
            blocks.append(f"<h3>{line}</h3>")
        else:
            blocks.append(f"<p>{line}</p>")
    return "\n".join(blocks)
