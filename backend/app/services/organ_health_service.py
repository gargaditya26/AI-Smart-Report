from typing import List, Dict
import uuid


class OrganHealthService:
    """Service for calculating organ health scores and generating recommendations"""

    # Mapping of tests to organs
    ORGAN_TEST_MAPPING = {
        "Heart": ["Total Cholesterol", "LDL Cholesterol", "HDL Cholesterol", "Triglycerides"],
        "Liver": ["SGOT", "SGPT", "Alkaline Phosphatase", "Total Bilirubin", "Direct Bilirubin",
                  "Total Protein", "Albumin", "Globulin"],
        "Kidneys": ["Blood Urea", "Creatinine", "Uric Acid", "eGFR", "BUN/Creatinine Ratio"],
        "Pancreas": ["Glucose Fasting", "HbA1c"],
        "Thyroid": ["TSH", "T3", "T4"],
        "Blood": ["Hemoglobin", "White Blood Cell Count", "Platelet Count", "Red Blood Cell Count",
                  "Hematocrit", "MCV", "MCH", "MCHC"],
    }

    # Organ descriptions
    ORGAN_DESCRIPTIONS = {
        "Heart": "Cardiovascular system responsible for pumping blood throughout the body",
        "Liver": "Vital organ that filters blood, processes nutrients, and produces proteins",
        "Kidneys": "Filter waste products from blood and regulate fluid balance",
        "Pancreas": "Produces insulin and enzymes for digestion and blood sugar regulation",
        "Thyroid": "Controls metabolism, energy, and hormone production",
        "Blood": "Transports oxygen, nutrients, and fights infections",
    }

    @staticmethod
    def calculate_organ_scores(lab_results: List[Dict]) -> Dict:
        """Calculate health scores for each organ based on lab results"""
        organ_scores = []
        recommendations = []

        for organ_name, related_tests in OrganHealthService.ORGAN_TEST_MAPPING.items():
            # Find tests related to this organ
            organ_test_results = [
                test for test in lab_results
                if test["test_name"] in related_tests
            ]

            if not organ_test_results:
                continue  # Skip organs with no tests

            # Calculate organ health score
            organ_score_data = OrganHealthService._calculate_single_organ_score(
                organ_name, organ_test_results
            )
            organ_scores.append(organ_score_data)

            # Generate recommendations for this organ
            organ_recommendations = OrganHealthService._generate_organ_recommendations(
                organ_name, organ_test_results
            )
            recommendations.extend(organ_recommendations)

        # Calculate overall health score
        if organ_scores:
            overall_score = sum(o["health_score"] for o in organ_scores) // len(organ_scores)
        else:
            overall_score = 0

        return {
            "overall_health_score": overall_score,
            "organ_scores": organ_scores,
            "recommendations": recommendations
        }

    @staticmethod
    def _calculate_single_organ_score(organ_name: str, test_results: List[Dict]) -> Dict:
        """Calculate health score for a single organ"""
        total_tests = len(test_results)
        abnormal_tests = [t for t in test_results if t["status"] != "Normal"]
        abnormal_count = len(abnormal_tests)

        # Calculate score based on normal tests ratio
        normal_ratio = (total_tests - abnormal_count) / total_tests if total_tests > 0 else 0

        # Adjust score based on severity of abnormalities
        severity_penalty = 0
        for test in abnormal_tests:
            if "Critical" in test["status"]:
                severity_penalty += 30
            elif "High" in test["status"] or "Low" in test["status"]:
                severity_penalty += 15
            else:  # Slightly high/low
                severity_penalty += 5

        base_score = int(normal_ratio * 100)
        final_score = max(0, base_score - severity_penalty)

        # Determine status
        if final_score >= 90:
            status = "Excellent"
            color = "green"
        elif final_score >= 70:
            status = "Good"
            color = "yellow"
        elif final_score >= 50:
            status = "Attention Needed"
            color = "orange"
        else:
            status = "Concerning"
            color = "red"

        # Format related tests
        related_tests = [
            {
                "test_name": test["test_name"],
                "value": test["value"],
                "unit": test["unit"],
                "status": test["status"]
            }
            for test in test_results
        ]

        return {
            "organ_id": str(uuid.uuid4()),
            "organ_name": organ_name,
            "health_score": final_score,
            "status": status,
            "color": color,
            "test_count": total_tests,
            "abnormal_test_count": abnormal_count,
            "related_tests": related_tests,
            "description": OrganHealthService.ORGAN_DESCRIPTIONS.get(organ_name, "")
        }

    @staticmethod
    def _generate_organ_recommendations(organ_name: str, test_results: List[Dict]) -> List[Dict]:
        """Generate health recommendations for an organ"""
        recommendations = []
        abnormal_tests = [t for t in test_results if t["status"] != "Normal"]

        if not abnormal_tests:
            return recommendations

        # Organ-specific recommendations
        if organ_name == "Heart":
            if any(t["test_name"] in ["LDL Cholesterol", "Total Cholesterol"] and "High" in t["status"]
                   for t in abnormal_tests):
                recommendations.append({
                    "recommendation_id": str(uuid.uuid4()),
                    "organ_name": organ_name,
                    "text": "Your cholesterol levels are elevated. Consider reducing saturated fat intake and increasing physical activity.",
                    "category": "lifestyle",
                    "priority": 2,
                    "severity": "important",
                    "related_tests": ["Total Cholesterol", "LDL Cholesterol"]
                })

            if any(t["test_name"] == "Triglycerides" and "High" in t["status"] for t in abnormal_tests):
                recommendations.append({
                    "recommendation_id": str(uuid.uuid4()),
                    "organ_name": organ_name,
                    "text": "Elevated triglycerides detected. Limit sugar and refined carbohydrates in your diet.",
                    "category": "dietary",
                    "priority": 2,
                    "severity": "important",
                    "related_tests": ["Triglycerides"]
                })

        elif organ_name == "Liver":
            if any(t["test_name"] in ["SGOT", "SGPT"] and "High" in t["status"] for t in abnormal_tests):
                recommendations.append({
                    "recommendation_id": str(uuid.uuid4()),
                    "organ_name": organ_name,
                    "text": "Liver enzyme levels are elevated. Consult your doctor for further evaluation. Avoid alcohol and maintain a healthy diet.",
                    "category": "consult_doctor",
                    "priority": 1,
                    "severity": "important",
                    "related_tests": ["SGOT", "SGPT"]
                })

        elif organ_name == "Kidneys":
            if any(t["test_name"] in ["Creatinine", "Blood Urea"] and "High" in t["status"]
                   for t in abnormal_tests):
                recommendations.append({
                    "recommendation_id": str(uuid.uuid4()),
                    "organ_name": organ_name,
                    "text": "Kidney function markers are abnormal. Please consult a nephrologist for detailed assessment.",
                    "category": "consult_doctor",
                    "priority": 1,
                    "severity": "critical",
                    "related_tests": ["Creatinine", "Blood Urea"]
                })

        elif organ_name == "Pancreas":
            if any(t["test_name"] in ["Glucose Fasting", "HbA1c"] and "High" in t["status"]
                   for t in abnormal_tests):
                recommendations.append({
                    "recommendation_id": str(uuid.uuid4()),
                    "organ_name": organ_name,
                    "text": "Blood sugar levels are elevated. Consider lifestyle modifications and consult your doctor for diabetes screening.",
                    "category": "consult_doctor",
                    "priority": 1,
                    "severity": "important",
                    "related_tests": ["Glucose Fasting", "HbA1c"]
                })

        elif organ_name == "Thyroid":
            if any("TSH" == t["test_name"] and t["status"] != "Normal" for t in abnormal_tests):
                recommendations.append({
                    "recommendation_id": str(uuid.uuid4()),
                    "organ_name": organ_name,
                    "text": "Thyroid hormone levels are abnormal. Consult an endocrinologist for proper evaluation and treatment.",
                    "category": "consult_doctor",
                    "priority": 1,
                    "severity": "important",
                    "related_tests": ["TSH"]
                })

        elif organ_name == "Blood":
            if any(t["test_name"] == "Hemoglobin" and "Low" in t["status"] for t in abnormal_tests):
                recommendations.append({
                    "recommendation_id": str(uuid.uuid4()),
                    "organ_name": organ_name,
                    "text": "Hemoglobin levels are low. Increase iron-rich foods in your diet and consult your doctor.",
                    "category": "dietary",
                    "priority": 2,
                    "severity": "important",
                    "related_tests": ["Hemoglobin"]
                })

        return recommendations
