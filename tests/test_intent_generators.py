from app.services.intent.static_intent_generator import StaticIntentGenerator


def test_static_intent_generator_returns_questions():
    result = StaticIntentGenerator().generate("BCBA mock exam")

    assert result.source == "static"
    assert result.questions
    assert result.questions[0].question
    assert result.questions[0].intent
