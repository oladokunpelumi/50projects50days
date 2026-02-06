from config.personas import select_persona


def test_persona_auto_selection_professional():
    persona = select_persona("Macro risk and institutional liquidity flows look fragile")
    assert persona == "professional_analyst"


def test_persona_auto_selection_casual_degen():
    persona = select_persona("gm degens wen moon this meme coin")
    assert persona == "casual_degen"


def test_persona_manual_override():
    persona = select_persona("any text", override="neutral_researcher")
    assert persona == "neutral_researcher"
