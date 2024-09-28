from django.db.models import Count, Q
from django.utils import timezone


def check_disease_suspected(questions):
    """
    This function checks if any question's answer is both not empty and doesn't contains 'No'.

    Parameter:
    - question: A list consisting of various questions with their respective answers.

    Returns:
    - Boolean: A Boolean flag stating if the disease is suspected or not.
    """
    return any(
        'answer' in question and question['answer']
        and all(word.lower() not in map(str.lower, question['answer']) for word in ['no', 'lpg'])
        for question in questions
    )


def get_suspected_disease_counts(questionnaire_queryset):
    """
    This functions checks the various questions and returns the suspected disease counts.

    Parameters:
    - questionare_queryset: A queryset consisting of objects that containes the CBAC form.

    Returns:
    - Dict: A dictionary consisting of various disease counts.
    """
    suspected_diseases = {
        "other_communicable_dieases": 0,
        "copd": 0,
        "ent_disorder": 0,
        "leprosy": 0,
        "tb": 0,
        "eye_disorder": 0,
        "diabetes": 0,
        "breast_cancer": 0,
        "oral_Cancer": 0,
        "cervical_cancer": 0,
        "Alzheimers": 0,
        "asthama": 0
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


def get_aggregated_data(family_member_queryset, family_head_queryset, aggregate_type="dashboard"):
    """
    Aggregates various statistics for a given queryset based on the specified aggregation type.

    Parameters:
    - family_member_queryset: Django queryset, sometimes filtered based on ward or healthpost, to
                            perform the aggregation.
    - family_head_queryset: Django queryset, containing family head details, to perform the aggregation.
    - aggregate_type: A string representing the type of aggregation to perform.
                    Options are "dashboard", "export", or "tab".
    Returns:
    - Dict/List: A dictionary or a list conataining the aggregated counts based on the specified type.
    """
    today = timezone.now().date()

    if aggregate_type == "dashboard":

        # Survey Data
        survey_data = family_member_queryset.aggregate(
            total_AbhaCreated=Count('id', filter=Q(
                isAbhaCreated=True), distinct=True),
            total_citizen_count=Count('id', distinct=True),
            todays_citizen_count=Count('id', filter=Q(
                created_date__date=today), distinct=True),
            total_cbac_count=Count('id', filter=Q(
                age__gte=30, cbacRequired=True), distinct=True),
            male=Count('id', filter=Q(gender="M"), distinct=True),
            female=Count('id', filter=Q(gender="F"), distinct=True),
            transgender=Count('id', filter=Q(gender="O"), distinct=True),
            citizen_above_60=Count('id', filter=Q(age__gte=60), distinct=True),
            citizen_above_30=Count('id', filter=Q(age__gte=30), distinct=True),
            total_vulnerable=Count('id', filter=Q(
                vulnerable=True), distinct=True),
            vulnerable_70_Years=Count('id', filter=Q(
                vulnerable_choices__choice='70+ Years'), distinct=True),
            vulnerable_Physically_handicapped=Count('id', filter=Q(
                vulnerable_choices__choice='Physically Handicapped'), distinct=True),
            vulnerable_completely_paralyzed_or_on_bed=Count('id', filter=Q(
                vulnerable_choices__choice='Completely Paralyzed or On bed'), distinct=True),
            vulnerable_elderly_and_alone_at_home=Count('id', filter=Q(
                vulnerable_choices__choice='Elderly and alone at home'), distinct=True),
            vulnerable_any_other_reason=Count('id', filter=Q(
                vulnerable_choices__choice='Any other reason'), distinct=True),
            blood_collected_home=Count('id', filter=Q(
                bloodCollectionLocation='Home'), distinct=True),
            blood_collected_center=Count('id', filter=Q(
                bloodCollectionLocation='Center'), distinct=True),
            denied_by_mo_count=Count('id', filter=Q(
                bloodCollectionLocation='AMO'), distinct=True),
            denied_by_mo_individual=Count('id', filter=Q(
                bloodCollectionLocation='Individual Itself'), distinct=True),
            Referral_choice_Referral_to_Mun_Dispensary=Count('id', filter=Q(
                referels__choice='Referral to Mun. Dispensary / HBT for Blood Test / Confirmation / Treatment'), distinct=True),
            Referral_choice_Referral_to_HBT_polyclinic=Count('id', filter=Q(
                referels__choice='Referral to HBT polyclinic for physician consultation'), distinct=True),
            Referral_choice_Referral_to_Peripheral_Hospital=Count('id', filter=Q(
                referels__choice='Referral to Peripheral Hospital / Special Hospital for management of Complication'), distinct=True),
            Referral_choice_Referral_to_Medical_College=Count('id', filter=Q(
                referels__choice='Referral to Medical College for management of Complication'), distinct=True),
            Referral_choice_Referral_to_Private_facility=Count('id', filter=Q(
                referels__choice='Referral to Private facility'), distinct=True),
            hypertension=Count('id', filter=Q(
                is_hypertensive=True), distinct=True),
            total_LabTestAdded=Count('id', filter=Q(
                isLabTestAdded=True), distinct=True),
            TestReportGenerated=Count('id', filter=Q(
                isLabTestReportGenerated=True), distinct=True)
        )

        # Aggregate counts for familyHead_queryset
        familyHead_data = family_head_queryset.aggregate(
            partial_survey_count=Count('id', filter=Q(
                partialSubmit=True), distinct=True),
            total_family_count=Count('id', distinct=True),
            today_family_count=Count('id', filter=Q(
                created_date__date=today), distinct=True)
        )

        # Aggregated survey data of various types
        combined_survey_data = {**survey_data, **familyHead_data}

        # Suspected Disease Counts
        Questionnaire_queryset = family_member_queryset.filter(
            Questionnaire__isnull=False)
        suspected_disease_counts = get_suspected_disease_counts(
            Questionnaire_queryset)

        return {
            'total_count': combined_survey_data["total_citizen_count"],
            'todays_count': combined_survey_data["todays_citizen_count"],
            'partial_survey_count': combined_survey_data["partial_survey_count"],
            'total_family_count': combined_survey_data["total_family_count"],
            'today_family_count': combined_survey_data["today_family_count"],
            'total_cbac_count': combined_survey_data["total_cbac_count"],
            'citizen_above_60': combined_survey_data["citizen_above_60"],
            'citizen_above_30': combined_survey_data["citizen_above_30"],
            'TestReportGenerated': combined_survey_data["TestReportGenerated"],
            'total_LabTestAdded': combined_survey_data["total_LabTestAdded"],
            'total_AbhaCreated': combined_survey_data["total_AbhaCreated"],
            "male": combined_survey_data["male"],
            "female": combined_survey_data["female"],
            "transgender": combined_survey_data["transgender"],
            'hypertension': combined_survey_data["hypertension"],
            **suspected_disease_counts,
            'blood_collected_home': combined_survey_data["blood_collected_home"],
            'blood_collected_center': combined_survey_data["blood_collected_center"],
            'denied_by_mo_count': combined_survey_data["denied_by_mo_count"],
            'denied_by_mo_individual': combined_survey_data["denied_by_mo_individual"],
            'Referral_choice_Referral_to_Mun_Dispensary': combined_survey_data["Referral_choice_Referral_to_Mun_Dispensary"],
            'Referral_choice_Referral_to_HBT_polyclinic': combined_survey_data["Referral_choice_Referral_to_HBT_polyclinic"],
            'Referral_choice_Referral_to_Peripheral_Hospital': combined_survey_data["Referral_choice_Referral_to_Peripheral_Hospital"],
            'Referral_choice_Referral_to_Medical_College': combined_survey_data["Referral_choice_Referral_to_Medical_College"],
            'Referral_choice_Referral_to_Private_facility': combined_survey_data["Referral_choice_Referral_to_Private_facility"],
            'total_vulnerable': combined_survey_data["total_vulnerable"],
            'vulnerable_70_Years': combined_survey_data["vulnerable_70_Years"],
            'vulnerable_Physically_handicapped': combined_survey_data["vulnerable_Physically_handicapped"],
            'vulnerable_completely_paralyzed_or_on_bed': combined_survey_data["vulnerable_completely_paralyzed_or_on_bed"],
            'vulnerable_elderly_and_alone_at_home': combined_survey_data["vulnerable_elderly_and_alone_at_home"],
            'vulnerable_any_other_reason': combined_survey_data["vulnerable_any_other_reason"]
        }
    elif aggregate_type == "export" or aggregate_type == "tab":
        # Survey Data
        survey_data = family_member_queryset.aggregate(
            total_AbhaCreated=Count('id', filter=Q(
                isAbhaCreated=True), distinct=True),
            total_citizen_count=Count('id', distinct=True),
            total_cbac_count=Count('id', filter=Q(
                age__gte=30, cbacRequired=True), distinct=True),
            male=Count('id', filter=Q(gender="M"), distinct=True),
            female=Count('id', filter=Q(gender="F"), distinct=True),
            transgender=Count('id', filter=Q(gender="O"), distinct=True),
            citizen_above_60=Count('id', filter=Q(age__gte=60), distinct=True),
            citizen_above_30=Count('id', filter=Q(age__gte=30), distinct=True),
            total_vulnerable=Count('id', filter=Q(
                vulnerable=True), distinct=True),
            blood_collected_home=Count('id', filter=Q(
                bloodCollectionLocation='Home'), distinct=True),
            blood_collected_center=Count('id', filter=Q(
                bloodCollectionLocation='Center'), distinct=True),
            denied_by_mo_count=Count('id', filter=Q(
                bloodCollectionLocation='AMO'), distinct=True),
            denied_by_mo_individual=Count('id', filter=Q(
                bloodCollectionLocation='Individual Itself'), distinct=True),
            Referral_choice_Referral_to_Mun_Dispensary=Count('id', filter=Q(
                referels__choice='Referral to Mun. Dispensary / HBT for Blood Test / Confirmation / Treatment'), distinct=True),
            Referral_choice_Referral_to_HBT_polyclinic=Count('id', filter=Q(
                referels__choice='Referral to HBT polyclinic for physician consultation'), distinct=True),
            Referral_choice_Referral_to_Peripheral_Hospital=Count('id', filter=Q(
                referels__choice='Referral to Peripheral Hospital / Special Hospital for management of Complication'), distinct=True),
            Referral_choice_Referral_to_Medical_College=Count('id', filter=Q(
                referels__choice='Referral to Medical College for management of Complication'), distinct=True),
            Referral_choice_Referral_to_Private_facility=Count('id', filter=Q(
                referels__choice='Referral to Private facility'), distinct=True),
            hypertension=Count('id', filter=Q(
                is_hypertensive=True), distinct=True),
            total_LabTestAdded=Count('id', filter=Q(
                isLabTestAdded=True), distinct=True),
            TestReportGenerated=Count('id', filter=Q(
                isLabTestReportGenerated=True), distinct=True)
        )

        # Aggregate counts for familyHead_queryset
        familyHead_data = family_head_queryset.aggregate(
            total_family_count=Count('id', distinct=True),
        )

        # Aggregated survey data of various types
        combined_survey_data = {**survey_data, **familyHead_data}

        # Suspected Disease Counts
        Questionnaire_queryset = family_member_queryset.filter(
            Questionnaire__isnull=False)
        suspected_disease_counts = get_suspected_disease_counts(
            Questionnaire_queryset)

        if aggregate_type == "export":
            return [combined_survey_data["total_family_count"], combined_survey_data["total_citizen_count"],
                    combined_survey_data["total_cbac_count"], combined_survey_data["citizen_above_60"],
                    combined_survey_data["citizen_above_30"], combined_survey_data["male"],
                    combined_survey_data["female"], combined_survey_data["transgender"],
                    combined_survey_data["total_AbhaCreated"], combined_survey_data["total_vulnerable"],
                    suspected_disease_counts["diabetes"], combined_survey_data["hypertension"],
                    suspected_disease_counts["oral_Cancer"], suspected_disease_counts["cervical_cancer"],
                    suspected_disease_counts["copd"], suspected_disease_counts["eye_disorder"],
                    suspected_disease_counts["ent_disorder"], suspected_disease_counts["asthama"],
                    suspected_disease_counts["Alzheimers"], suspected_disease_counts["tb"],
                    suspected_disease_counts["leprosy"], suspected_disease_counts["breast_cancer"],
                    suspected_disease_counts["other_communicable_dieases"],
                    combined_survey_data["blood_collected_home"], combined_survey_data["blood_collected_center"],
                    combined_survey_data["denied_by_mo_count"], combined_survey_data["denied_by_mo_individual"],
                    combined_survey_data["TestReportGenerated"], combined_survey_data["total_LabTestAdded"],
                    combined_survey_data["Referral_choice_Referral_to_Mun_Dispensary"],
                    combined_survey_data["Referral_choice_Referral_to_HBT_polyclinic"],
                    combined_survey_data["Referral_choice_Referral_to_Peripheral_Hospital"],
                    combined_survey_data["Referral_choice_Referral_to_Medical_College"],
                    combined_survey_data["Referral_choice_Referral_to_Private_facility"]]
        else:
            return {"total_family_count": combined_survey_data["total_family_count"], "total_citizen_count": combined_survey_data["total_citizen_count"],
                    "total_cbac_count": combined_survey_data["total_cbac_count"], "citizen_above_60": combined_survey_data["citizen_above_60"],
                    "citizen_above_30": combined_survey_data["citizen_above_30"], "male": combined_survey_data["male"],
                    "female": combined_survey_data["female"], "transgender": combined_survey_data["transgender"], "total_AbhaCreated": combined_survey_data["total_AbhaCreated"],
                    "total_diabetes": suspected_disease_counts["diabetes"], "hypertension": combined_survey_data["hypertension"], "total_oral_cancer": suspected_disease_counts["oral_Cancer"],
                    "total_cervical_cancer": suspected_disease_counts["cervical_cancer"], "total_COPD_count": suspected_disease_counts["copd"],
                    "total_eye_problem": suspected_disease_counts["eye_disorder"], "total_ent_disorder": suspected_disease_counts["ent_disorder"],
                    "total_asthma": suspected_disease_counts["asthama"], "total_Alzheimers": suspected_disease_counts["Alzheimers"],
                    "total_tb_count": suspected_disease_counts["tb"], "total_leprosy": suspected_disease_counts["leprosy"],
                    "total_breast_cancer": suspected_disease_counts["breast_cancer"], "total_communicable": suspected_disease_counts["other_communicable_dieases"],
                    "blood_collected_home": combined_survey_data["blood_collected_home"], "blood_collected_center": combined_survey_data["blood_collected_center"],
                    "denied_by_mo_count": combined_survey_data["denied_by_mo_count"], "denied_by_mo_individual": combined_survey_data["denied_by_mo_individual"],
                    "TestReportGenerated": combined_survey_data["TestReportGenerated"], "total_LabTestAdded": combined_survey_data["total_LabTestAdded"],
                    "Referral_choice_Referral_to_Mun_Dispensary": combined_survey_data["Referral_choice_Referral_to_Mun_Dispensary"],
                    "Referral_choice_Referral_to_HBT_polyclinic": combined_survey_data["Referral_choice_Referral_to_HBT_polyclinic"],
                    "Referral_choice_Referral_to_Peripheral_Hospital": combined_survey_data["Referral_choice_Referral_to_Peripheral_Hospital"],
                    "Referral_choice_Referral_to_Medical_College": combined_survey_data["Referral_choice_Referral_to_Medical_College"],
                    "Referral_choice_Referral_to_Private_facility": combined_survey_data["Referral_choice_Referral_to_Private_facility"],
                    "total_vulnerable": combined_survey_data["total_vulnerable"]
                    }
    else:
        raise ValueError(
            f"Invalid aggregate_type '{aggregate_type}'. Valid options are 'dashboard', 'export', or 'tab'.")
