import re
from typing import List, Dict, Optional, Tuple
from fuzzywuzzy import fuzz
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LabTestAnalysisService:
    """Service for analyzing text and extracting lab test results"""

    # Common lab tests with their normal ranges
    TEST_DEFINITIONS = {
        "Hemoglobin": {"min": 13.0, "max": 17.0, "unit": "g/dL", "aliases": ["Hb", "HGB", "HAEMOGLOBIN"]},
        "White Blood Cell Count": {"min": 4000, "max": 11000, "unit": "cells/μL", "aliases": ["WBC", "TLC", "TOTAL LEUCOCYTE COUNT", "TOTAL LEUKOCYTE COUNT", "Leucocyte Count"]},
        "Platelet Count": {"min": 150000, "max": 450000, "unit": "cells/μL", "aliases": ["PLT", "Platelets", "PLATELET COUNT"]},
        "Red Blood Cell Count": {"min": 4.5, "max": 5.5, "unit": "million cells/μL", "aliases": ["RBC", "ERYTHROCYTE COUNT", "RED BLOOD CELL COUNT"]},
        "Hematocrit": {"min": 38.0, "max": 50.0, "unit": "%", "aliases": ["HCT", "PCV", "PACKED CELL VOLUME"]},
        "MCV": {"min": 80.0, "max": 100.0, "unit": "fL", "aliases": ["Mean Corpuscular Volume"]},
        "MCH": {"min": 27.0, "max": 33.0, "unit": "pg", "aliases": ["Mean Corpuscular Hemoglobin"]},
        "MCHC": {"min": 32.0, "max": 36.0, "unit": "g/dL", "aliases": ["Mean Corpuscular Hemoglobin Concentration"]},
        "RDW": {"min": 11.5, "max": 14.5, "unit": "%", "aliases": ["R.D.W", "RDW-CV", "Red Cell Distribution Width"]},
        "Neutrophils": {"min": 40.0, "max": 80.0, "unit": "%", "aliases": ["NEUTROPHILS", "Neutrophil"]},
        "Lymphocytes": {"min": 20.0, "max": 40.0, "unit": "%", "aliases": ["LYMPHOCYTES", "Lymphocyte"]},
        "Eosinophils": {"min": 1.0, "max": 6.0, "unit": "%", "aliases": ["EOSINOPHILS", "Eosinophil"]},
        "Monocytes": {"min": 2.0, "max": 10.0, "unit": "%", "aliases": ["MONOCYTES", "Monocyte"]},
        "Basophils": {"min": 0.0, "max": 2.0, "unit": "%", "aliases": ["BASOPHILS", "Basophil"]},
        "Neutrophil Lymphocyte Ratio": {"min": 0.78, "max": 3.53, "unit": "ratio", "aliases": ["NLR", "Neutrophil lymphocyte ratio"]},
        "MPV": {"min": 7.0, "max": 13.0, "unit": "fL", "aliases": ["Mean Platelet Volume"]},

        # Liver Function Tests
        "SGOT": {"min": 5.0, "max": 40.0, "unit": "U/L", "aliases": ["AST", "Aspartate Aminotransferase"]},
        "SGPT": {"min": 5.0, "max": 40.0, "unit": "U/L", "aliases": ["ALT", "Alanine Aminotransferase"]},
        "Alkaline Phosphatase": {"min": 30.0, "max": 120.0, "unit": "U/L", "aliases": ["ALP", "Alk Phos"]},
        "Total Bilirubin": {"min": 0.1, "max": 1.2, "unit": "mg/dL", "aliases": ["Bilirubin Total"]},
        "Direct Bilirubin": {"min": 0.0, "max": 0.3, "unit": "mg/dL", "aliases": ["Conjugated Bilirubin"]},
        "Total Protein": {"min": 6.0, "max": 8.3, "unit": "g/dL", "aliases": ["Serum Protein"]},
        "Albumin": {"min": 3.5, "max": 5.5, "unit": "g/dL", "aliases": ["Serum Albumin"]},
        "Globulin": {"min": 2.0, "max": 3.5, "unit": "g/dL", "aliases": ["Serum Globulin"]},

        # Kidney Function Tests
        "Blood Urea": {"min": 7.0, "max": 20.0, "unit": "mg/dL", "aliases": ["BUN", "Urea", "Blood Urea Nitrogen", "Urea Nitrogen", "Urea N", "BLOODUREA", "TESTBLOODUREA"]},
        "Creatinine": {"min": 0.6, "max": 1.2, "unit": "mg/dL", "aliases": ["Serum Creatinine", "Creatinine Serum", "S Creatinine", "Creat", "CREATININE"]},
        "Uric Acid": {"min": 3.5, "max": 7.2, "unit": "mg/dL", "aliases": ["Urate", "Serum Uric Acid", "S Uric Acid", "URICACID"]},
        "eGFR": {"min": 90.0, "max": 120.0, "unit": "mL/min", "aliases": ["GFR", "Glomerular Filtration Rate", "EGFR"]},
        "BUN/Creatinine Ratio": {"min": 10.0, "max": 20.0, "unit": "ratio", "aliases": ["BUN Creatinine Ratio", "Urea Creatinine Ratio"]},

        # Lipid Profile
        "Total Cholesterol": {"min": 0.0, "max": 200.0, "unit": "mg/dL", "aliases": ["Cholesterol"]},
        "Triglycerides": {"min": 0.0, "max": 150.0, "unit": "mg/dL", "aliases": ["TG"]},
        "HDL Cholesterol": {"min": 40.0, "max": 60.0, "unit": "mg/dL", "aliases": ["HDL", "Good Cholesterol"]},
        "LDL Cholesterol": {"min": 0.0, "max": 100.0, "unit": "mg/dL", "aliases": ["LDL", "Bad Cholesterol"]},
        "VLDL": {"min": 5.0, "max": 40.0, "unit": "mg/dL", "aliases": ["VLDL Cholesterol"]},

        # Diabetes Tests
        "Glucose Fasting": {"min": 70.0, "max": 100.0, "unit": "mg/dL", "aliases": ["FBS", "Fasting Blood Sugar", "Fasting Glucose"]},
        "HbA1c": {"min": 4.0, "max": 5.7, "unit": "%", "aliases": ["Glycated Hemoglobin", "A1C"]},

        # Thyroid Tests
        "TSH": {"min": 0.4, "max": 4.0, "unit": "mIU/L", "aliases": ["Thyroid Stimulating Hormone"]},
        "T3": {"min": 80.0, "max": 200.0, "unit": "ng/dL", "aliases": ["Triiodothyronine"]},
        "T4": {"min": 5.0, "max": 12.0, "unit": "μg/dL", "aliases": ["Thyroxine"]},
    }

    @staticmethod
    def extract_lab_tests(text: str) -> List[Dict]:
        """Extract lab tests from common pathology-report layouts.

        PDF text extraction often puts a result row on one line without a
        colon (for example: ``HAEMOGLOBIN 12.7 g/dL 12-15``).  The old
        parser only looked for ``name:value`` or concatenated ALL-CAPS
        tokens, which caused valid rows to be ignored.  This parser first
        scans every line for known test names/aliases and then falls back to
        the legacy regexes.
        """
        logger.info("=" * 80)
        logger.info("STARTING LAB TEST EXTRACTION")
        logger.info(f"Text length: {len(text)} characters")

        seen_tests: Dict[str, Dict] = {}

        def add_result(raw_name: str, value_str: str, unit_raw: str = "",
                       source_confidence: float = 0.85) -> None:
            matched_test = LabTestAnalysisService._find_matching_test(raw_name)
            if not matched_test:
                return

            test_name, test_info = matched_test
            try:
                value = float(value_str.replace(",", ""))
            except (ValueError, TypeError):
                return

            if not LabTestAnalysisService._is_reasonable_value(
                value, test_info["min"], test_info["max"]
            ):
                return

            unit = LabTestAnalysisService._validate_unit(unit_raw.strip(), test_info["unit"])
            confidence = source_confidence
            if not unit:
                unit = test_info["unit"]
                confidence = min(confidence, 0.70)
            elif unit.lower() == test_info["unit"].lower():
                confidence = min(0.95, confidence + 0.05)
            else:
                confidence = min(confidence, 0.75)

            status, deviation = LabTestAnalysisService._calculate_status(
                value, test_info["min"], test_info["max"]
            )
            result = {
                "test_id": str(uuid.uuid4()),
                "test_name": test_name,
                "value": value,
                "unit": unit,
                "normal_range_min": test_info["min"],
                "normal_range_max": test_info["max"],
                "status": status,
                "deviation_percentage": deviation,
                "confidence_score": round(confidence, 2),
                "source": "extracted"
            }

            existing = seen_tests.get(test_name)
            if existing is None or result["confidence_score"] > existing["confidence_score"]:
                seen_tests[test_name] = result

        # 1) Robust line-based parsing.  Match the known test name itself,
        # then look for the first numeric result immediately after it.
        lines = [re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines() if ln.strip()]
        logger.info(f"Scanning {len(lines)} extracted text lines for known tests")

        definitions = []
        for known_name, info in LabTestAnalysisService.TEST_DEFINITIONS.items():
            names = [known_name] + info.get("aliases", [])
            for name in names:
                # Longest names first so "HDL Cholesterol" wins over "HDL".
                clean = re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()
                if clean:
                    definitions.append((clean, known_name))

        definitions.sort(key=lambda x: len(x[0]), reverse=True)

        # Numeric result + optional unit.  Commas are accepted for CBC counts.
        number_re = r"([<>]?\s*\d[\d,]*(?:\.\d+)?)"
        for line in lines:
            lower = line.lower()
            for clean_name, known_name in definitions:
                # Word-ish boundary around normalized test name.  Also allow
                # OCR punctuation/spaces between words.
                parts = clean_name.split()
                name_pattern = r"\s*[\W_]*".join(re.escape(p) for p in parts)
                mname = re.search(r"(?<![a-z0-9])" + name_pattern + r"(?![a-z0-9])", lower)
                if not mname:
                    continue

                remainder = line[mname.end():]
                mval = re.search(number_re, remainder)
                if not mval:
                    # Some PDFs put the value on the next physical line.
                    continue

                value_str = mval.group(1).replace(" ", "")
                after = remainder[mval.end():].strip()
                # Unit is the token(s) before the reference range.  We only
                # need a short prefix; validation below rejects garbage.
                unit_match = re.match(
                    r"([A-Za-zμµ%]+(?:\s*/\s*[A-Za-zμµ]+)?(?:\s+cells?\/(?:cu\.?mm|μL|uL))?)",
                    after,
                    re.IGNORECASE
                )
                unit_raw = unit_match.group(1) if unit_match else ""
                add_result(known_name, value_str, unit_raw, 0.90)
                # One known test per line is normally correct.
                break

        # 2) Legacy separator/concatenated parsing as a fallback for reports
        # that use "Test: value unit" or "TESTNAME12.3".
        pattern1 = r'([A-Za-z][A-Za-z0-9\s\(\)\-]{2,50}?)\s*[:=]\s*([0-9]+\.?[0-9]*)\s*([a-zA-Zμµ/%]{1,15}(?:\/[a-zA-Zμµ]+)?)?'
        pattern2 = r'([A-Z]{3,}(?:\([A-Z]+\))?)([0-9]+\.?[0-9]*)'

        for match in list(re.finditer(pattern1, text)) + list(re.finditer(pattern2, text)):
            raw = match.group(1).strip()
            value = match.group(2).strip()
            unit = ""
            if match.lastindex and match.lastindex >= 3:
                unit = (match.group(3) or "").strip()
            add_result(raw, value, unit, 0.75)

        results = list(seen_tests.values())
        logger.info("=" * 80)
        logger.info(f"EXTRACTION COMPLETE: {len(results)} unique tests extracted")
        for test in results:
            logger.info(
                f"  - {test['test_name']}: {test['value']} {test['unit']} ({test['status']})"
            )
        logger.info("=" * 80)
        return results

    @staticmethod
    def _find_matching_test(test_name: str) -> Optional[Tuple[str, Dict]]:
        """Find matching test from known tests using fuzzy matching"""
        test_name_lower = test_name.lower().strip()

        # Extract alias from parentheses if present (e.g., "HEMOGLOBIN(HB)" -> "HEMOGLOBIN", "HB")
        alias_in_name = None
        test_name_clean = test_name_lower
        if '(' in test_name_lower and ')' in test_name_lower:
            import re
            match = re.match(r'(.+?)\((.+?)\)', test_name_lower)
            if match:
                test_name_clean = match.group(1).strip()
                alias_in_name = match.group(2).strip()
                logger.info(f"  Extracted: name='{test_name_clean}', alias='{alias_in_name}'")

        best_match = None
        best_score = 0

        for known_test, info in LabTestAnalysisService.TEST_DEFINITIONS.items():
            # Check exact match on clean name (highest priority)
            if test_name_clean == known_test.lower():
                logger.info(f"  EXACT match: '{test_name_clean}' == '{known_test.lower()}'")
                return (known_test, info)

            # Check if extracted alias matches any known alias exactly
            if alias_in_name:
                for alias in info["aliases"]:
                    if alias_in_name == alias.lower():
                        logger.info(f"  ALIAS match: '{alias_in_name}' == '{alias.lower()}'")
                        return (known_test, info)

            # Check aliases exact match on full test name
            for alias in info["aliases"]:
                if test_name_lower == alias.lower():
                    logger.info(f"  ALIAS match: '{test_name_lower}' == '{alias.lower()}'")
                    return (known_test, info)

            # Fuzzy matching on clean test name (threshold 75 for better matching)
            score = fuzz.ratio(test_name_clean, known_test.lower())
            if score > best_score and score >= 75:
                best_score = score
                best_match = (known_test, info)
                logger.info(f"  Fuzzy match: '{test_name_clean}' vs '{known_test.lower()}' = {score}")

            # Check against aliases with fuzzy matching
            for alias in info["aliases"]:
                score = fuzz.ratio(test_name_clean, alias.lower())
                if score > best_score and score >= 75:
                    best_score = score
                    best_match = (known_test, info)
                    logger.info(f"  Fuzzy alias match: '{test_name_clean}' vs '{alias.lower()}' = {score}")

        if best_match:
            logger.info(f"  Best match: {best_match[0]} (score: {best_score})")
        return best_match

    @staticmethod
    def _calculate_status(value: float, min_val: float, max_val: float) -> Tuple[str, float]:
        """Calculate test status and deviation percentage"""
        if min_val <= value <= max_val:
            return "Normal", 0.0

        if value < min_val:
            deviation = ((min_val - value) / min_val) * 100
            if deviation > 50:
                return "Critical Low", -deviation
            elif deviation > 20:
                return "Low", -deviation
            else:
                return "Slightly Low", -deviation

        if value > max_val:
            deviation = ((value - max_val) / max_val) * 100
            if deviation > 50:
                return "Critical High", deviation
            elif deviation > 20:
                return "High", deviation
            else:
                return "Slightly High", deviation

        return "Normal", 0.0

    @staticmethod
    def _is_reasonable_value(value: float, min_val: float, max_val: float) -> bool:
        """Check if value is within reasonable bounds (not obviously garbage)"""
        # Allow values within 10x of the normal range (both high and low)
        reasonable_min = min_val * 0.1
        reasonable_max = max_val * 10.0

        return reasonable_min <= value <= reasonable_max

    @staticmethod
    def _validate_unit(extracted_unit: str, expected_unit: str) -> Optional[str]:
        """Validate and normalize the extracted unit"""
        if not extracted_unit:
            return expected_unit

        # Check if extracted unit matches expected unit (case insensitive)
        if extracted_unit.lower() == expected_unit.lower():
            return expected_unit

        # Common unit variations and normalizations
        unit_mappings = {
            "gdl": "g/dL",
            "mgdl": "mg/dL",
            "ul": "μL",
            "u/l": "U/L",
            "ul": "U/L",
            "ngdl": "ng/dL",
            "μgdl": "μg/dL",
            "miuml": "mIU/L",
            "fl": "fL",
            "pg": "pg",
            "%": "%",
        }

        normalized = extracted_unit.lower().replace("/", "").replace(" ", "")
        if normalized in unit_mappings:
            return unit_mappings[normalized]

        # If unit is too long or contains non-unit characters, it's likely garbage
        if len(extracted_unit) > 15 or any(c.isdigit() for c in extracted_unit):
            return None

        # Check if extracted unit is a reasonable substring of expected unit
        if extracted_unit.lower() in expected_unit.lower() or expected_unit.lower() in extracted_unit.lower():
            return expected_unit

        # If we can't validate it, reject it
        return None

    @staticmethod
    def add_manual_test(test_name: str, value: float, unit: str) -> Dict:
        """Add a manually entered test"""
        # Try to find matching test
        matched_test = LabTestAnalysisService._find_matching_test(test_name)

        if matched_test:
            test_name, test_info = matched_test
            status, deviation = LabTestAnalysisService._calculate_status(
                value, test_info["min"], test_info["max"]
            )
            normal_range_min = test_info["min"]
            normal_range_max = test_info["max"]
        else:
            status = "Normal"
            deviation = 0.0
            normal_range_min = None
            normal_range_max = None

        return {
            "test_id": str(uuid.uuid4()),
            "test_name": test_name,
            "value": value,
            "unit": unit,
            "normal_range_min": normal_range_min,
            "normal_range_max": normal_range_max,
            "status": status,
            "deviation_percentage": deviation,
            "confidence_score": 1.0,  # Manual entry
            "source": "manual"
        }
