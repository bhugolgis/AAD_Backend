def check_disease_suspected(questions):
    """
    This function checks if any question's answer is both not empty and contains 'Yes'.
    """
    return any(question.get('answer', []) and 'No' not in question.get('answer', []) for question in questions)

def get_suspected_disease_counts(questionnaire_queryset):
    """
    This functions checks the various questions and returns the suspected disease counts.
    """
    suspected_diseases = {
        "other_communicable_dieases":0,
        "copd":0,
        "ent_disorder":0,
        "leprosy":0,
        "tb":0,
        "eye_disorder":0,
        "diabetes":0,
        "breast_cancer":0,
        "oral_Cancer":0,
        "cervical_cancer":0,
        "Alzheimers":0,
        "asthama":0
    }

    for record in questionnaire_queryset:
        part_b = record.Questionnaire.get('part_b', [])
        part_c = record.Questionnaire.get('part_c', [])
        part_e = record.Questionnaire.get('part_e', [])

        # Check for part E
        if check_disease_suspected(part_e[0:]):
            suspected_diseases["other_communicable_dieases"] += 1

        # Check for part C
        if check_disease_suspected(part_c[0:]):
            suspected_diseases["copd"] += 1

        # Check for part B
        if check_disease_suspected(part_b[15:16]):
            suspected_diseases["ent_disorder"] += 1

        if check_disease_suspected(part_b[24:32]):
            suspected_diseases["leprosy"] += 1

        if check_disease_suspected(part_b[1:9]):
            suspected_diseases["tb"] += 1

        if check_disease_suspected(part_b[11:15]):
            suspected_diseases["eye_disorder"] += 1

        if check_disease_suspected(part_b[9:11]):
            suspected_diseases["diabetes"] += 1

        if check_disease_suspected(part_b[32:35]):
            suspected_diseases["breast_cancer"] += 1

        if check_disease_suspected(part_b[17:24]):
            suspected_diseases["oral_Cancer"] += 1

        if check_disease_suspected(part_b[35:39]):
            suspected_diseases["cervical_cancer"] += 1

        if check_disease_suspected(part_b[39:43]):
            suspected_diseases["Alzheimers"] += 1

        if check_disease_suspected(part_b[:1]):
            suspected_diseases["asthama"] += 1

    return suspected_diseases