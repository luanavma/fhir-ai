#!/usr/bin/env python3
"""
seed.py

Generate synthetic FHIR R4 transaction Bundles for the FHIR Clinical Heatmap RAG project.

Focus:
- COVID-19
- Ebola virus disease
- Hantavirus infection
- Yellow fever
- Scorpion sting
- Dengue
- Gastrointestinal symptom reports: diarrhea, vomiting, abdominal pain, nausea, fever

Install:
    pip install faker

Run:
    python seed.py --patients 500 --output ./data --days 45 --seed 42

Output:
    data/patient-bundle-00001.json
    data/patient-bundle-00002.json
    ...

FHIR resources generated per patient:
- Patient
- Location
- Encounter
- Condition
- Observation
- DiagnosticReport

Terminology notes:
- SNOMED CT is used for clinical concepts in Condition.code and symptom Observation.code.
- ICD-10 is included as secondary coding for Conditions.
- LOINC is used for vital signs such as body temperature.
- UCUM is used for units.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from faker import Faker


fake = Faker("pt_BR")

FHIR_BASE_URL = "http://example.org/fhir"

SYSTEM_SNOMED = "http://snomed.info/sct"
SYSTEM_ICD10 = "http://hl7.org/fhir/sid/icd-10"
SYSTEM_LOINC = "http://loinc.org"
SYSTEM_UCUM = "http://unitsofmeasure.org"
SYSTEM_OBS_CATEGORY = "http://terminology.hl7.org/CodeSystem/observation-category"
SYSTEM_CONDITION_CLINICAL = "http://terminology.hl7.org/CodeSystem/condition-clinical"
SYSTEM_CONDITION_VERIFICATION = "http://terminology.hl7.org/CodeSystem/condition-ver-status"
SYSTEM_ENCOUNTER_CLASS = "http://terminology.hl7.org/CodeSystem/v3-ActCode"


@dataclass(frozen=True)
class Code:
    system: str
    code: str
    display: str


# Common symptom concepts.
# These are intentionally represented as Observations, not Conditions.
SYMPTOMS: dict[str, dict[str, Any]] = {
    "fever": {
        "pt": "febre",
        "snomed": Code(SYSTEM_SNOMED, "386661006", "Fever"),
        "phrases": [
            "Paciente relata febre alta há {days} dias.",
            "Paciente refere febre persistente com início há {days} dias.",
            "Paciente informa temperatura elevada e mal-estar há {days} dias.",
        ],
    },
    "diarrhea": {
        "pt": "diarreia",
        "snomed": Code(SYSTEM_SNOMED, "62315008", "Diarrhea"),
        "phrases": [
            "Paciente relata diarreia intensa há {days} dias.",
            "Paciente refere evacuações líquidas frequentes há {days} dias.",
            "Paciente informa fezes líquidas e aumento do número de evacuações há {days} dias.",
        ],
    },
    "vomiting": {
        "pt": "vômito",
        "snomed": Code(SYSTEM_SNOMED, "422400008", "Vomiting"),
        "phrases": [
            "Paciente relata episódios de vômito há {days} dias.",
            "Paciente refere náuseas com vômitos recorrentes há {days} dias.",
            "Paciente informa vômitos associados a mal-estar há {days} dias.",
        ],
    },
    "abdominal_pain": {
        "pt": "dor abdominal",
        "snomed": Code(SYSTEM_SNOMED, "21522001", "Abdominal pain"),
        "phrases": [
            "Paciente relata dor abdominal há {days} dias.",
            "Paciente refere dor de barriga e desconforto abdominal há {days} dias.",
            "Paciente informa cólica abdominal com piora progressiva há {days} dias.",
        ],
    },
    "nausea": {
        "pt": "náusea",
        "snomed": Code(SYSTEM_SNOMED, "422587007", "Nausea"),
        "phrases": [
            "Paciente relata náusea há {days} dias.",
            "Paciente refere enjoo persistente há {days} dias.",
            "Paciente informa náusea associada a inapetência há {days} dias.",
        ],
    },
    "cough": {
        "pt": "tosse",
        "snomed": Code(SYSTEM_SNOMED, "49727002", "Cough"),
        "phrases": [
            "Paciente relata tosse há {days} dias.",
            "Paciente refere tosse seca persistente há {days} dias.",
        ],
    },
    "dyspnea": {
        "pt": "dispneia",
        "snomed": Code(SYSTEM_SNOMED, "267036007", "Dyspnea"),
        "phrases": [
            "Paciente relata falta de ar há {days} dias.",
            "Paciente refere dispneia aos esforços há {days} dias.",
        ],
    },
    "myalgia": {
        "pt": "mialgia",
        "snomed": Code(SYSTEM_SNOMED, "68962001", "Myalgia"),
        "phrases": [
            "Paciente relata dor no corpo há {days} dias.",
            "Paciente refere mialgia difusa há {days} dias.",
        ],
    },
    "headache": {
        "pt": "cefaleia",
        "snomed": Code(SYSTEM_SNOMED, "25064002", "Headache"),
        "phrases": [
            "Paciente relata dor de cabeça há {days} dias.",
            "Paciente refere cefaleia persistente há {days} dias.",
        ],
    },
    "rash": {
        "pt": "exantema",
        "snomed": Code(SYSTEM_SNOMED, "271807003", "Eruption of skin"),
        "phrases": [
            "Paciente relata manchas vermelhas na pele há {days} dias.",
            "Paciente apresenta exantema de início recente há {days} dias.",
        ],
    },
    "bleeding": {
        "pt": "sangramento",
        "snomed": Code(SYSTEM_SNOMED, "131148009", "Bleeding"),
        "phrases": [
            "Paciente relata sangramento incomum há {days} dias.",
            "Paciente apresenta queixa de sangramento associado a febre há {days} dias.",
        ],
    },
    "fatigue": {
        "pt": "fadiga",
        "snomed": Code(SYSTEM_SNOMED, "84229001", "Fatigue"),
        "phrases": [
            "Paciente relata fadiga intensa há {days} dias.",
            "Paciente refere fraqueza e cansaço importante há {days} dias.",
        ],
    },
    "jaundice": {
        "pt": "icterícia",
        "snomed": Code(SYSTEM_SNOMED, "18165001", "Jaundice"),
        "phrases": [
            "Paciente apresenta pele e olhos amarelados há {days} dias.",
            "Paciente relata icterícia associada a febre há {days} dias.",
        ],
    },
    "sting_pain": {
        "pt": "dor por picada",
        "snomed": Code(SYSTEM_SNOMED, "22253000", "Pain"),
        "phrases": [
            "Paciente relata dor intensa no local da picada há {days} dias.",
            "Paciente refere dor local importante após possível picada de escorpião há {days} dias.",
        ],
    },
    "edema": {
        "pt": "edema",
        "snomed": Code(SYSTEM_SNOMED, "267038008", "Edema"),
        "phrases": [
            "Paciente apresenta edema no local da picada há {days} dias.",
            "Paciente relata inchaço local após picada há {days} dias.",
        ],
    },
    "paresthesia": {
        "pt": "formigamento",
        "snomed": Code(SYSTEM_SNOMED, "91019004", "Paresthesia"),
        "phrases": [
            "Paciente relata formigamento no local da picada há {days} dias.",
            "Paciente refere parestesia local há {days} dias.",
        ],
    },
    "sweating": {
        "pt": "sudorese",
        "snomed": Code(SYSTEM_SNOMED, "415690000", "Sweating"),
        "phrases": [
            "Paciente relata sudorese intensa há {days} dias.",
            "Paciente apresenta suor excessivo associado ao quadro há {days} dias.",
        ],
    },
    "tachycardia": {
        "pt": "taquicardia",
        "snomed": Code(SYSTEM_SNOMED, "3424008", "Tachycardia"),
        "phrases": [
            "Paciente relata palpitações e taquicardia há {days} dias.",
            "Paciente apresenta frequência cardíaca elevada há {days} dias.",
        ],
    },
}


# Disease/syndrome concepts represented as Condition resources.
# SNOMED CT is primary; ICD-10 is secondary.
DISEASES: dict[str, dict[str, Any]] = {
    "covid19": {
        "label": "COVID-19",
        "condition": Code(SYSTEM_SNOMED, "840539006", "Disease caused by Severe acute respiratory syndrome coronavirus 2"),
        "icd10": Code(SYSTEM_ICD10, "U07.1", "COVID-19, virus identified"),
        "symptoms": ["fever", "cough", "dyspnea", "fatigue", "headache", "myalgia"],
        "min_symptoms": 3,
        "max_symptoms": 5,
    },
    "ebola": {
        "label": "Ebola virus disease",
        # Verify in your terminology server if your SNOMED edition uses a different active concept.
        "condition": Code(SYSTEM_SNOMED, "37109004", "Ebola virus disease"),
        "icd10": Code(SYSTEM_ICD10, "A98.4", "Ebola virus disease"),
        "symptoms": ["fever", "fatigue", "vomiting", "diarrhea", "abdominal_pain", "bleeding"],
        "min_symptoms": 4,
        "max_symptoms": 6,
        "rare": True,
    },
    "hantavirus": {
        "label": "Hantavirus infection",
        # Verify in your terminology server if your SNOMED edition uses a different active concept.
        "condition": Code(SYSTEM_SNOMED, "233765002", "Hantavirus infection"),
        "icd10": Code(SYSTEM_ICD10, "B33.4", "Hantavirus pulmonary syndrome"),
        "symptoms": ["fever", "dyspnea", "fatigue", "myalgia", "headache", "nausea", "vomiting"],
        "min_symptoms": 3,
        "max_symptoms": 5,
        "rare": True,
    },
    "yellow_fever": {
        "label": "Yellow fever",
        # Verify in your terminology server if your SNOMED edition uses a different active concept.
        "condition": Code(SYSTEM_SNOMED, "16541001", "Yellow fever"),
        "icd10": Code(SYSTEM_ICD10, "A95.9", "Yellow fever, unspecified"),
        "symptoms": ["fever", "headache", "myalgia", "nausea", "vomiting", "abdominal_pain", "jaundice"],
        "min_symptoms": 3,
        "max_symptoms": 6,
        "rare": True,
    },
    "scorpion_sting": {
        "label": "Scorpion sting",
        # Injury/accident concept; keep as suspected/provisional condition for synthetic reports.
        "condition": Code(SYSTEM_SNOMED, "262552005", "Scorpion sting"),
        "icd10": Code(SYSTEM_ICD10, "T63.2", "Toxic effect of venom of scorpion"),
        "symptoms": ["sting_pain", "edema", "paresthesia", "sweating", "tachycardia", "nausea", "vomiting"],
        "min_symptoms": 2,
        "max_symptoms": 5,
    },
    "dengue": {
        "label": "Dengue",
        "condition": Code(SYSTEM_SNOMED, "38362002", "Dengue"),
        "icd10": Code(SYSTEM_ICD10, "A90", "Dengue fever"),
        "symptoms": ["fever", "headache", "myalgia", "rash", "nausea", "vomiting", "abdominal_pain"],
        "min_symptoms": 3,
        "max_symptoms": 6,
    },
    "gastrointestinal_report": {
        "label": "Gastrointestinal symptom report",
        # This is not a definitive disease; use provisional condition.
        "condition": Code(SYSTEM_SNOMED, "25374005", "Gastroenteritis"),
        "icd10": Code(SYSTEM_ICD10, "A09", "Infectious gastroenteritis and colitis, unspecified"),
        "symptoms": ["diarrhea", "vomiting", "abdominal_pain", "nausea", "fever"],
        "min_symptoms": 2,
        "max_symptoms": 5,
    },
}


BRAZIL_REGIONS: list[dict[str, Any]] = [
    {
        "city": "São José do Rio Preto",
        "state": "SP",
        "lat": -20.8113,
        "lng": -49.3758,
        "weights": {
            "covid19": 0.8,
            "ebola": 0.02,
            "hantavirus": 0.15,
            "yellow_fever": 0.20,
            "scorpion_sting": 2.7,
            "dengue": 1.4,
            "gastrointestinal_report": 1.3,
        },
    },
    {
        "city": "Ribeirão Preto",
        "state": "SP",
        "lat": -21.1775,
        "lng": -47.8103,
        "weights": {
            "covid19": 0.9,
            "ebola": 0.01,
            "hantavirus": 0.10,
            "yellow_fever": 0.25,
            "scorpion_sting": 1.8,
            "dengue": 1.6,
            "gastrointestinal_report": 1.1,
        },
    },
    {
        "city": "Campinas",
        "state": "SP",
        "lat": -22.9056,
        "lng": -47.0608,
        "weights": {
            "covid19": 1.2,
            "ebola": 0.01,
            "hantavirus": 0.06,
            "yellow_fever": 0.10,
            "scorpion_sting": 0.7,
            "dengue": 1.1,
            "gastrointestinal_report": 2.4,
        },
    },
    {
        "city": "São Paulo",
        "state": "SP",
        "lat": -23.5505,
        "lng": -46.6333,
        "weights": {
            "covid19": 2.6,
            "ebola": 0.02,
            "hantavirus": 0.05,
            "yellow_fever": 0.10,
            "scorpion_sting": 0.4,
            "dengue": 0.8,
            "gastrointestinal_report": 1.2,
        },
    },
    {
        "city": "Belo Horizonte",
        "state": "MG",
        "lat": -19.9167,
        "lng": -43.9345,
        "weights": {
            "covid19": 1.0,
            "ebola": 0.01,
            "hantavirus": 0.10,
            "yellow_fever": 0.7,
            "scorpion_sting": 1.3,
            "dengue": 1.8,
            "gastrointestinal_report": 1.1,
        },
    },
    {
        "city": "Uberlândia",
        "state": "MG",
        "lat": -18.9128,
        "lng": -48.2755,
        "weights": {
            "covid19": 0.8,
            "ebola": 0.01,
            "hantavirus": 1.7,
            "yellow_fever": 0.35,
            "scorpion_sting": 1.6,
            "dengue": 1.2,
            "gastrointestinal_report": 0.9,
        },
    },
    {
        "city": "Rio de Janeiro",
        "state": "RJ",
        "lat": -22.9068,
        "lng": -43.1729,
        "weights": {
            "covid19": 1.4,
            "ebola": 0.02,
            "hantavirus": 0.04,
            "yellow_fever": 0.18,
            "scorpion_sting": 0.4,
            "dengue": 1.5,
            "gastrointestinal_report": 1.0,
        },
    },
    {
        "city": "Recife",
        "state": "PE",
        "lat": -8.0476,
        "lng": -34.8770,
        "weights": {
            "covid19": 0.9,
            "ebola": 0.01,
            "hantavirus": 0.03,
            "yellow_fever": 0.08,
            "scorpion_sting": 0.9,
            "dengue": 3.0,
            "gastrointestinal_report": 1.2,
        },
    },
    {
        "city": "Salvador",
        "state": "BA",
        "lat": -12.9777,
        "lng": -38.5016,
        "weights": {
            "covid19": 0.9,
            "ebola": 0.01,
            "hantavirus": 0.03,
            "yellow_fever": 0.18,
            "scorpion_sting": 1.0,
            "dengue": 2.1,
            "gastrointestinal_report": 1.3,
        },
    },
    {
        "city": "Manaus",
        "state": "AM",
        "lat": -3.1190,
        "lng": -60.0217,
        "weights": {
            "covid19": 1.0,
            "ebola": 0.01,
            "hantavirus": 0.20,
            "yellow_fever": 1.2,
            "scorpion_sting": 0.8,
            "dengue": 1.8,
            "gastrointestinal_report": 1.0,
        },
    },
]


# Synthetic outbreak windows make heatmaps visually interesting.
# day_start/day_end are offsets from start_date.
OUTBREAKS: list[dict[str, Any]] = [
    {"city": "São Paulo", "disease": "covid19", "day_start": 10, "day_end": 25, "multiplier": 3.5},
    {"city": "Recife", "disease": "dengue", "day_start": 5, "day_end": 35, "multiplier": 3.8},
    {"city": "Campinas", "disease": "gastrointestinal_report", "day_start": 15, "day_end": 34, "multiplier": 4.2},
    {"city": "São José do Rio Preto", "disease": "scorpion_sting", "day_start": 8, "day_end": 40, "multiplier": 3.0},
    {"city": "Manaus", "disease": "yellow_fever", "day_start": 18, "day_end": 42, "multiplier": 2.4},
    {"city": "Uberlândia", "disease": "hantavirus", "day_start": 20, "day_end": 39, "multiplier": 2.2},
]


def fhir_datetime(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def safe_slug(text: str) -> str:
    text = text.lower()
    replacements = {
        "ã": "a", "á": "a", "à": "a", "â": "a",
        "é": "e", "ê": "e",
        "í": "i",
        "ó": "o", "ô": "o", "õ": "o",
        "ú": "u",
        "ç": "c",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text


def coding(code: Code) -> dict[str, str]:
    return {"system": code.system, "code": code.code, "display": code.display}


def reference(resource_type: str, resource_id: str) -> dict[str, str]:
    return {"reference": f"{resource_type}/{resource_id}"}


def weighted_choice(weights: dict[str, float]) -> str:
    keys = list(weights.keys())
    values = list(weights.values())
    return random.choices(keys, weights=values, k=1)[0]


def choose_region() -> dict[str, Any]:
    # Higher total weights generate denser regions in the synthetic dataset.
    region_weights = [sum(region["weights"].values()) for region in BRAZIL_REGIONS]
    return random.choices(BRAZIL_REGIONS, weights=region_weights, k=1)[0]


def outbreak_multiplier(region: dict[str, Any], disease_key: str, event_day: int) -> float:
    multiplier = 1.0
    for outbreak in OUTBREAKS:
        if (
            outbreak["city"] == region["city"]
            and outbreak["disease"] == disease_key
            and outbreak["day_start"] <= event_day <= outbreak["day_end"]
        ):
            multiplier *= float(outbreak["multiplier"])
    return multiplier


def choose_disease(region: dict[str, Any], event_day: int) -> str:
    weights = dict(region["weights"])

    for disease_key in weights:
        weights[disease_key] *= outbreak_multiplier(region, disease_key, event_day)

    return weighted_choice(weights)


def make_patient(patient_id: str, region: dict[str, Any]) -> dict[str, Any]:
    gender = random.choice(["male", "female"])
    birth_date = fake.date_of_birth(minimum_age=1, maximum_age=92)

    return {
        "resourceType": "Patient",
        "id": patient_id,
        "identifier": [
            {
                "system": "http://example.org/fhir/sid/synthetic-patient",
                "value": patient_id,
            }
        ],
        "gender": gender,
        "birthDate": birth_date.isoformat(),
        "address": [
            {
                "use": "home",
                "type": "physical",
                "city": region["city"],
                "state": region["state"],
                "country": "BR",
            }
        ],
    }


def make_location(location_id: str, region: dict[str, Any]) -> dict[str, Any]:
    return {
        "resourceType": "Location",
        "id": location_id,
        "status": "active",
        "name": f"Unidade Sentinela - {region['city']}",
        "address": {
            "city": region["city"],
            "state": region["state"],
            "country": "BR",
        },
        "position": {
            "longitude": region["lng"],
            "latitude": region["lat"],
        },
    }


def make_encounter(
    encounter_id: str,
    patient_id: str,
    location_id: str,
    start: datetime,
) -> dict[str, Any]:
    class_code = random.choice([
        ("AMB", "ambulatory"),
        ("EMER", "emergency"),
        ("HH", "home health"),
        ("VR", "virtual"),
    ])

    return {
        "resourceType": "Encounter",
        "id": encounter_id,
        "status": "finished",
        "class": {
            "system": SYSTEM_ENCOUNTER_CLASS,
            "code": class_code[0],
            "display": class_code[1],
        },
        "subject": reference("Patient", patient_id),
        "period": {
            "start": fhir_datetime(start),
            "end": fhir_datetime(start + timedelta(minutes=random.randint(20, 240))),
        },
        "location": [
            {
                "location": reference("Location", location_id),
            }
        ],
    }


def make_condition(
    condition_id: str,
    patient_id: str,
    encounter_id: str,
    disease_key: str,
    recorded_date: datetime,
) -> dict[str, Any]:
    disease = DISEASES[disease_key]

    return {
        "resourceType": "Condition",
        "id": condition_id,
        "clinicalStatus": {
            "coding": [
                {
                    "system": SYSTEM_CONDITION_CLINICAL,
                    "code": "active",
                    "display": "Active",
                }
            ]
        },
        "verificationStatus": {
            "coding": [
                {
                    "system": SYSTEM_CONDITION_VERIFICATION,
                    "code": "provisional",
                    "display": "Provisional",
                }
            ]
        },
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                        "code": "encounter-diagnosis",
                        "display": "Encounter Diagnosis",
                    }
                ]
            }
        ],
        "code": {
            "coding": [
                coding(disease["condition"]),
                coding(disease["icd10"]),
            ],
            "text": disease["label"],
        },
        "subject": reference("Patient", patient_id),
        "encounter": reference("Encounter", encounter_id),
        "recordedDate": recorded_date.date().isoformat(),
    }


def make_symptom_observation(
    obs_id: str,
    patient_id: str,
    encounter_id: str,
    symptom_key: str,
    effective: datetime,
) -> dict[str, Any]:
    symptom = SYMPTOMS[symptom_key]
    severity = random.choice(["mild", "moderate", "severe"])
    duration_days = random.randint(1, 7)
    text = random.choice(symptom["phrases"]).format(days=duration_days)

    return {
        "resourceType": "Observation",
        "id": obs_id,
        "status": "final",
        "category": [
            {
                "coding": [
                    {
                        "system": SYSTEM_OBS_CATEGORY,
                        "code": "survey",
                        "display": "Survey",
                    }
                ]
            }
        ],
        "code": {
            "coding": [coding(symptom["snomed"])],
            "text": symptom["pt"],
        },
        "subject": reference("Patient", patient_id),
        "encounter": reference("Encounter", encounter_id),
        "effectiveDateTime": fhir_datetime(effective),
        "valueString": text,
        "component": [
            {
                "code": {"text": "severity"},
                "valueString": severity,
            },
            {
                "code": {"text": "duration_days"},
                "valueInteger": duration_days,
            },
        ],
    }


def make_temperature_observation(
    obs_id: str,
    patient_id: str,
    encounter_id: str,
    effective: datetime,
) -> dict[str, Any]:
    temperature = round(random.uniform(37.5, 40.3), 1)

    return {
        "resourceType": "Observation",
        "id": obs_id,
        "status": "final",
        "category": [
            {
                "coding": [
                    {
                        "system": SYSTEM_OBS_CATEGORY,
                        "code": "vital-signs",
                        "display": "Vital Signs",
                    }
                ]
            }
        ],
        "code": {
            "coding": [
                {
                    "system": SYSTEM_LOINC,
                    "code": "8310-5",
                    "display": "Body temperature",
                }
            ],
            "text": "Body temperature",
        },
        "subject": reference("Patient", patient_id),
        "encounter": reference("Encounter", encounter_id),
        "effectiveDateTime": fhir_datetime(effective),
        "valueQuantity": {
            "value": temperature,
            "unit": "Cel",
            "system": SYSTEM_UCUM,
            "code": "Cel",
        },
    }


def make_heart_rate_observation(
    obs_id: str,
    patient_id: str,
    encounter_id: str,
    effective: datetime,
) -> dict[str, Any]:
    heart_rate = random.randint(96, 145)

    return {
        "resourceType": "Observation",
        "id": obs_id,
        "status": "final",
        "category": [
            {
                "coding": [
                    {
                        "system": SYSTEM_OBS_CATEGORY,
                        "code": "vital-signs",
                        "display": "Vital Signs",
                    }
                ]
            }
        ],
        "code": {
            "coding": [
                {
                    "system": SYSTEM_LOINC,
                    "code": "8867-4",
                    "display": "Heart rate",
                }
            ],
            "text": "Heart rate",
        },
        "subject": reference("Patient", patient_id),
        "encounter": reference("Encounter", encounter_id),
        "effectiveDateTime": fhir_datetime(effective),
        "valueQuantity": {
            "value": heart_rate,
            "unit": "beats/minute",
            "system": SYSTEM_UCUM,
            "code": "/min",
        },
    }


def make_oxygen_saturation_observation(
    obs_id: str,
    patient_id: str,
    encounter_id: str,
    effective: datetime,
) -> dict[str, Any]:
    saturation = random.randint(88, 97)

    return {
        "resourceType": "Observation",
        "id": obs_id,
        "status": "final",
        "category": [
            {
                "coding": [
                    {
                        "system": SYSTEM_OBS_CATEGORY,
                        "code": "vital-signs",
                        "display": "Vital Signs",
                    }
                ]
            }
        ],
        "code": {
            "coding": [
                {
                    "system": SYSTEM_LOINC,
                    "code": "2708-6",
                    "display": "Oxygen saturation in Arterial blood",
                }
            ],
            "text": "Oxygen saturation",
        },
        "subject": reference("Patient", patient_id),
        "encounter": reference("Encounter", encounter_id),
        "effectiveDateTime": fhir_datetime(effective),
        "valueQuantity": {
            "value": saturation,
            "unit": "%",
            "system": SYSTEM_UCUM,
            "code": "%",
        },
    }


def make_diagnostic_report(
    report_id: str,
    patient_id: str,
    encounter_id: str,
    disease_key: str,
    issued: datetime,
    observation_ids: list[str],
) -> dict[str, Any]:
    disease = DISEASES[disease_key]

    return {
        "resourceType": "DiagnosticReport",
        "id": report_id,
        "status": "final",
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
                        "code": "OTH",
                        "display": "Other",
                    }
                ]
            }
        ],
        "code": {
            "text": f"Synthetic clinical surveillance report - {disease['label']}",
        },
        "subject": reference("Patient", patient_id),
        "encounter": reference("Encounter", encounter_id),
        "issued": fhir_datetime(issued),
        "result": [reference("Observation", obs_id) for obs_id in observation_ids],
        "conclusion": (
            f"Report clínico sintético para vigilância regional, com quadro "
            f"compatível/provisório com {disease['label']}."
        ),
    }


def bundle_entry(resource: dict[str, Any]) -> dict[str, Any]:
    resource_type = resource["resourceType"]
    resource_id = resource["id"]

    return {
        "fullUrl": f"{FHIR_BASE_URL}/{resource_type}/{resource_id}",
        "resource": resource,
        "request": {
            "method": "PUT",
            "url": f"{resource_type}/{resource_id}",
        },
    }


def make_patient_bundle(index: int, start_date: datetime, days: int) -> dict[str, Any]:
    region = choose_region()
    event_day = random.randint(0, days)
    encounter_date = start_date + timedelta(
        days=event_day,
        hours=random.randint(7, 22),
        minutes=random.randint(0, 59),
    )

    disease_key = choose_disease(region, event_day)
    disease = DISEASES[disease_key]

    patient_id = new_id("patient")
    location_id = f"location-{safe_slug(region['city'])}-{region['state'].lower()}"

    resources: list[dict[str, Any]] = [
        make_patient(patient_id, region),
        make_location(location_id, region),
    ]

    encounters_count = random.randint(1, 3)

    for encounter_index in range(encounters_count):
        encounter_id = new_id("encounter")
        current_encounter_date = encounter_date + timedelta(days=encounter_index * random.randint(1, 4))

        resources.append(
            make_encounter(
                encounter_id=encounter_id,
                patient_id=patient_id,
                location_id=location_id,
                start=current_encounter_date,
            )
        )

        condition_id = new_id("condition")
        resources.append(
            make_condition(
                condition_id=condition_id,
                patient_id=patient_id,
                encounter_id=encounter_id,
                disease_key=disease_key,
                recorded_date=current_encounter_date,
            )
        )

        symptom_pool = disease["symptoms"]
        selected_symptoms = random.sample(
            symptom_pool,
            k=random.randint(disease["min_symptoms"], min(disease["max_symptoms"], len(symptom_pool))),
        )

        observation_ids: list[str] = []

        for symptom_key in selected_symptoms:
            obs_id = new_id("obs")
            observation_ids.append(obs_id)
            resources.append(
                make_symptom_observation(
                    obs_id=obs_id,
                    patient_id=patient_id,
                    encounter_id=encounter_id,
                    symptom_key=symptom_key,
                    effective=current_encounter_date,
                )
            )

        if "fever" in selected_symptoms:
            temp_obs_id = new_id("obs-temp")
            observation_ids.append(temp_obs_id)
            resources.append(
                make_temperature_observation(
                    obs_id=temp_obs_id,
                    patient_id=patient_id,
                    encounter_id=encounter_id,
                    effective=current_encounter_date,
                )
            )

        if "tachycardia" in selected_symptoms:
            hr_obs_id = new_id("obs-hr")
            observation_ids.append(hr_obs_id)
            resources.append(
                make_heart_rate_observation(
                    obs_id=hr_obs_id,
                    patient_id=patient_id,
                    encounter_id=encounter_id,
                    effective=current_encounter_date,
                )
            )

        if disease_key in {"covid19", "hantavirus"} and random.random() < 0.6:
            spo2_obs_id = new_id("obs-spo2")
            observation_ids.append(spo2_obs_id)
            resources.append(
                make_oxygen_saturation_observation(
                    obs_id=spo2_obs_id,
                    patient_id=patient_id,
                    encounter_id=encounter_id,
                    effective=current_encounter_date,
                )
            )

        report_id = new_id("diagnostic-report")
        resources.append(
            make_diagnostic_report(
                report_id=report_id,
                patient_id=patient_id,
                encounter_id=encounter_id,
                disease_key=disease_key,
                issued=current_encounter_date + timedelta(minutes=30),
                observation_ids=observation_ids,
            )
        )

    return {
        "resourceType": "Bundle",
        "id": f"bundle-{index:05d}",
        "type": "transaction",
        "timestamp": fhir_datetime(datetime.now(timezone.utc)),
        "entry": [bundle_entry(resource) for resource in resources],
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def write_manifest(output_dir: Path, patients: int, days: int, seed: int) -> None:
    manifest = {
        "generatedAt": fhir_datetime(datetime.now(timezone.utc)),
        "patients": patients,
        "days": days,
        "seed": seed,
        "diseases": {
            key: {
                "label": value["label"],
                "conditionSnomed": {
                    "system": value["condition"].system,
                    "code": value["condition"].code,
                    "display": value["condition"].display,
                },
                "icd10": {
                    "system": value["icd10"].system,
                    "code": value["icd10"].code,
                    "display": value["icd10"].display,
                },
                "symptoms": value["symptoms"],
            }
            for key, value in DISEASES.items()
        },
        "symptoms": {
            key: {
                "pt": value["pt"],
                "snomed": {
                    "system": value["snomed"].system,
                    "code": value["snomed"].code,
                    "display": value["snomed"].display,
                },
            }
            for key, value in SYMPTOMS.items()
        },
        "regions": BRAZIL_REGIONS,
        "outbreaks": OUTBREAKS,
        "notes": [
            "Synthetic dataset for demos only. Do not use as clinical truth.",
            "Validate SNOMED CT codes against your licensed terminology server/edition before production use.",
            "Condition resources represent provisional/suspected clinical surveillance reports.",
        ],
    }
    write_json(output_dir / "manifest.json", manifest)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate synthetic FHIR R4 transaction Bundles for Clinical Heatmap RAG."
    )
    parser.add_argument("--patients", type=int, default=100)
    parser.add_argument("--output", type=str, default="./data/fhir/raw")
    parser.add_argument("--days", type=int, default=45)
    parser.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()

    random.seed(args.seed)
    Faker.seed(args.seed)

    output_dir = Path(args.output)
    start_date = datetime.now(timezone.utc) - timedelta(days=args.days)

    for index in range(1, args.patients + 1):
        bundle = make_patient_bundle(
            index=index,
            start_date=start_date,
            days=args.days,
        )
        file_path = output_dir / f"patient-bundle-{index:05d}.json"
        write_json(file_path, bundle)

    write_manifest(output_dir, args.patients, args.days, args.seed)

    print(f"Generated {args.patients} FHIR transaction Bundles in {output_dir}")
    print(f"Generated manifest in {output_dir / 'manifest.json'}")


if __name__ == "__main__":
    main()
