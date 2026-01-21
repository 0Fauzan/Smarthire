def rule_based_language_help(text):
    suggestions = []
    improved = text

    replacements = {
        "little bit": "some experience",
        "i did": "I worked on",
        "i know": "I have experience with",
        "very good": "strong",
        "things": "aspects"
    }

    for bad, good in replacements.items():
        if bad in improved.lower():
            improved = improved.lower().replace(bad, good)
            suggestions.append(f"Replace '{bad}' with '{good}'")

    tips = [
        "Use confident verbs like 'developed', 'implemented', 'designed'",
        "Avoid filler words such as 'actually', 'basically'"
    ]

    return {
        "original": text,
        "suggested": improved.capitalize(),
        "suggestions": suggestions,
        "tips": tips,
        "communication_score": 60
    }
