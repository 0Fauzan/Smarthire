def confidence_from_face_percentage(face_percentage):
    """
    Simple, explainable mapping:
    Face presence ≈ confidence/attention
    """
    if face_percentage >= 80:
        return 90
    elif face_percentage >= 65:
        return 75
    elif face_percentage >= 50:
        return 60
    else:
        return 45
