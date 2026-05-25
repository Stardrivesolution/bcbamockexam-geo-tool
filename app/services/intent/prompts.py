INTENT_GENERATOR_VERSION = "intent-generator-llm-v0.1"

SYSTEM_PROMPT = """You are a GEO and SEO search-intent strategist.
Generate realistic English user questions for evaluating whether a web page
fully covers a topic. Return only valid JSON."""

USER_PROMPT_TEMPLATE = """Target website:
- Brand: {brand_name}
- Domain: {domain}
- Target language: {language}
- Target region: {region}
- Target keyword/topic: {target_keyword}

Known benchmark competitors:
{competitors}

Generate 15 user questions that a BCBA exam candidate might ask before buying
or using this product. The questions should help evaluate GEO readiness for AI
answers.

Return this JSON object:
{{
  "questions": [
    {{
      "id": "q01",
      "question": "question text",
      "intent": "definition|benefit|format|coverage|explanations|scoring|pricing|sample|difficulty|study_plan|updates|access|review|audience|trust|comparison",
      "priority": 1
    }}
  ]
}}

Rules:
- Use natural English.
- Make questions specific to BCBA mock exams and exam prep.
- Include buyer-intent and trust questions, not only definitions.
- Do not mention competitors by name unless the intent is comparison.
- Use priority 1 for high-value buyer questions and 2 for supporting questions.
"""
