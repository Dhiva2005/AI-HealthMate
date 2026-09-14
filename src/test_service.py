from service import HealthMateService


# ============================================================
# DISPLAY SUCCESSFUL TEST RESULT
# ============================================================

def print_result(test_name, result):
    """
    Display the result of a successful service test.
    """

    print("\n" + "=" * 70)
    print(test_name)
    print("=" * 70)

    print("\nPredicted Disease:")
    print(result["predicted_disease"])

    print("\nModel Score:")
    print(f'{result["model_score"]:.2f}%')

    print("\nConfidence Level:")
    print(result["confidence_level"])

    print("\nConfidence Warning:")
    print(result["confidence_warning"])

    print("\nRecognized Symptoms:")

    for symptom in result["recognized_symptoms"]:
        print(f"• {symptom}")

    print("\nUnrecognized Symptoms:")

    if result["unrecognized_symptoms"]:

        for symptom in result["unrecognized_symptoms"]:
            print(f"• {symptom}")

    else:

        print("None")

    print("\nSymptom Warning:")
    print(result["symptom_warning"])

    print("\nEmergency Warning:")
    print(result["emergency_warning"])

    print("\nTop Predictions:")

    for prediction in result["top_predictions"]:

        print(
            f'• {prediction["disease"]}: '
            f'{prediction["model_score"]:.2f}%'
        )


# ============================================================
# RUN VALID TEST
# ============================================================

def run_test(service, test_number, test_name, symptoms):
    """
    Run one test that is expected to succeed.
    """

    print("\n" + "#" * 70)
    print(f"TEST {test_number}: {test_name}")
    print("#" * 70)

    print("\nInput Symptoms:")

    for symptom in symptoms:
        print(f"• {symptom}")

    try:

        result = service.process_symptoms(
            symptoms
        )

        print_result(
            test_name,
            result
        )

        print("\nRESULT: PASS")

        return True

    except Exception as error:

        print("\nRESULT: FAIL")
        print(f"Error: {error}")

        return False


# ============================================================
# RUN INVALID TEST
# ============================================================

def run_invalid_test(service, test_number, test_name, symptoms):
    """
    Run a test that is expected to fail validation.
    """

    print("\n" + "#" * 70)
    print(f"TEST {test_number}: {test_name}")
    print("#" * 70)

    print("\nInput Symptoms:")

    if symptoms:

        for symptom in symptoms:
            print(f"• {symptom}")

    else:

        print("None")

    try:

        service.process_symptoms(
            symptoms
        )

        print("\nRESULT: FAIL")
        print(
            "Expected the service to reject the input, "
            "but it accepted it."
        )

        return False

    except ValueError as error:

        print("\nExpected Error:")
        print(error)

        print("\nRESULT: PASS")

        return True

    except Exception as error:

        print("\nRESULT: FAIL")
        print(f"Unexpected error: {error}")

        return False


# ============================================================
# MAIN TEST SUITE
# ============================================================

def main():

    print("=" * 70)
    print("AI HEALTHMATE - SERVICE TEST SUITE")
    print("=" * 70)

    # --------------------------------------------------------
    # Load service
    # --------------------------------------------------------

    try:

        print("\nLoading HealthMate service...")

        service = HealthMateService()

        print(
            "HealthMate service loaded successfully!"
        )

    except Exception as error:

        print(
            "\nERROR: Could not load HealthMate service."
        )

        print(error)

        return

    total_tests = 0
    passed_tests = 0

    # ========================================================
    # TEST 1
    # Normal valid symptoms
    # ========================================================

    total_tests += 1

    if run_test(
        service,
        1,
        "Normal Valid Symptoms",
        [
            "fever",
            "headache",
            "vomiting"
        ]
    ):

        passed_tests += 1

    # ========================================================
    # TEST 2
    # Completely invalid symptoms
    # ========================================================

    total_tests += 1

    if run_invalid_test(
        service,
        2,
        "Completely Invalid Symptoms",
        [
            "abc",
            "xyz"
        ]
    ):

        passed_tests += 1

    # ========================================================
    # TEST 3
    # Mixed valid and invalid symptoms
    # ========================================================

    total_tests += 1

    if run_test(
        service,
        3,
        "Mixed Valid and Invalid Symptoms",
        [
            "fever",
            "headache",
            "abc"
        ]
    ):

        passed_tests += 1

    # ========================================================
    # TEST 4
    # Symptom aliases
    # ========================================================

    total_tests += 1

    if run_test(
        service,
        4,
        "Symptom Aliases",
        [
            "head pain",
            "throwing up",
            "high temperature"
        ]
    ):

        passed_tests += 1

    # ========================================================
    # TEST 5
    # Duplicate symptoms
    # ========================================================

    total_tests += 1

    if run_test(
        service,
        5,
        "Duplicate Symptoms",
        [
            "fever",
            "fever",
            "headache",
            "headache",
            "vomiting",
            "vomiting"
        ]
    ):

        passed_tests += 1

    # ========================================================
    # TEST 6
    # Empty input
    # ========================================================

    total_tests += 1

    if run_invalid_test(
        service,
        6,
        "Empty Input",
        []
    ):

        passed_tests += 1

    # ========================================================
    # TEST SUMMARY
    # ========================================================

    failed_tests = total_tests - passed_tests

    print("\n\n" + "=" * 70)
    print("TEST SUITE SUMMARY")
    print("=" * 70)

    print(f"\nTotal Tests : {total_tests}")
    print(f"Passed      : {passed_tests}")
    print(f"Failed      : {failed_tests}")

    if passed_tests == total_tests:

        print("\nSTATUS: ALL TESTS PASSED")
        print(
            "AI HealthMate service is ready for API integration."
        )

    else:

        print("\nSTATUS: SOME TESTS FAILED")
        print(
            "Fix the failed tests before moving forward."
        )

    print("\n" + "=" * 70)


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()