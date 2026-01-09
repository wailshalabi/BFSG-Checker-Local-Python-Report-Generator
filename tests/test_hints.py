from app.domain.hints import enrich

def test_enrich_known_rule():
    e = enrich("color-contrast")
    assert "1.4.3" in e["wcag"]
    assert e["fix_hint"]

def test_enrich_unknown_rule():
    e = enrich("unknown-rule")
    assert isinstance(e["wcag"], list)
