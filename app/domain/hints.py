from app.domain.ruleset import RULE_TO_WCAG

HINTS = {
    "color-contrast": {
        "fix_hint": "Increase text/background contrast. Normal text must be at least 4.5:1; large text at least 3:1.",
        "code_snippet": "/* Example */\n.button{ color:#111; background:#fff; }",
    },
    "image-alt": {
        "fix_hint": "Add meaningful alt text to informative images. Use empty alt (alt=\"\" ) for decorative images.",
        "code_snippet": '<img src="..." alt="Describe the image meaningfully" />',
    },
    "label": {
        "fix_hint": "Ensure every form control has an associated <label> or an accessible name (aria-label/aria-labelledby).",
        "code_snippet": '<label for="email">Email</label>\n<input id="email" name="email" type="email" />',
    },
    "button-name": {
        "fix_hint": "Buttons must have an accessible name (visible text, aria-label, or aria-labelledby).",
        "code_snippet": '<button aria-label="Open menu">\n  <svg ...></svg>\n</button>',
    },
    "link-name": {
        "fix_hint": "Links must have a clear accessible name. Avoid empty links or icon-only links without aria-label.",
        "code_snippet": '<a href="/help" aria-label="Help">\n  <svg ...></svg>\n</a>',
    },
    "document-title": {
        "fix_hint": "Add a unique, descriptive <title> in the <head> so users can identify the page.",
        "code_snippet": "<head>\n  <title>Checkout – Example Shop</title>\n</head>",
    },
    "html-has-lang": {
        "fix_hint": "Set the document language on the <html> element.",
        "code_snippet": '<html lang="de">\n  ...\n</html>',
    },
    "landmark-one-main": {
        "fix_hint": "Ensure there is exactly one <main> landmark to help screen reader navigation.",
        "code_snippet": "<main>\n  ...\n</main>",
    },
}

def enrich(rule_id: str) -> dict:
    wcag = RULE_TO_WCAG.get(rule_id, [])
    hint = HINTS.get(rule_id, {})
    return {
        "wcag": wcag,
        "fix_hint": hint.get("fix_hint"),
        "code_snippet": hint.get("code_snippet"),
    }
