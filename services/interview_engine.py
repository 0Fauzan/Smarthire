import random


def evaluate_interview(answers):
    """
    Mock AI interview evaluation logic.
    Later replace this with ML / NLP models.
    """

    technical = random.randint(60, 90)
    communication = random.randint(55, 85)
    confidence = random.randint(50, 80)

    final_score = round((technical + communication + confidence) / 3)

    return {
        "technical_score": technical,
        "communication_score": communication,
        "confidence_score": confidence,
        "final_score": final_score
    }

