"""Word lists used by the rule-based extractor.

Kept in one file so they are easy to read, review and extend. All entries are
lower case. Matching is on whole words unless noted.
"""

# Phrases that introduce the patient's presenting problem.
PRESENTATION_CUES = (
    "complains of", "complaining of", "complaint of", "complains", "presents with", "presented with",
    "reports", "reported", "brought with", "patient has", "has had", "c/o",
)
# "<person> with ..." at the start of a clause, e.g. "Elderly male with ankle swelling".
PERSON_WORDS = (
    "patient", "male", "female", "man", "woman", "child", "toddler", "teenager", "boy", "girl",
    "infant", "baby", "adult", "lady", "gentleman",
)

SYMPTOMS = (
    "pain", "ache", "aches", "fever", "cough", "breath", "breathless", "breathlessness", "wheezing",
    "nausea", "vomiting", "headache", "dizziness", "giddiness", "fatigue", "tiredness", "weakness",
    "rash", "itching", "itchy", "swelling", "sore throat", "redness", "watering", "discharge",
    "loose stools", "diarrhoea", "diarrhea", "constipation", "cramps", "bleeding", "palpitations",
    "anxiety", "insomnia", "thirst", "urination", "burning", "toothache", "sneezing", "runny nose",
    "congestion", "acne", "weight gain", "weight loss", "numbness", "tingling", "chills", "body ache",
)

# Words that mark a clause as the clinician's conclusion.
DIAGNOSIS_CUES = (
    "diagnosed", "diagnosis", "impression", "assessment", "suspected", "likely", "probable",
    "possible", "consistent with", "suggestive of", "working diagnosis", "differential",
)
# Condition names and endings that indicate a diagnosis even without a cue word.
CONDITIONS = (
    "infection", "disease", "syndrome", "disorder", "diabetes", "hypertension", "asthma",
    "migraine", "gout", "anaemia", "anemia", "sprain", "strain", "dengue", "malaria", "typhoid",
    "hypothyroidism", "hyperthyroidism", "pneumonia", "bronchitis", "reflux", "food poisoning",
    "abscess", "fracture", "copd", "allergy", "allergic", "eczema", "psoriasis", "acne vulgaris",
    "sleep disturbance", "depression", "obesity", "exacerbation",
)
CONDITION_SUFFIXES = ("itis", "osis", "emia", "aemia", "algia", "pathy")

# Common outpatient drugs (generic names). Not exhaustive: a word directly
# before a dose ("xyzomab 20 mg") is also treated as a drug name.
DRUGS = (
    "paracetamol", "acetaminophen", "ibuprofen", "diclofenac", "naproxen", "aspirin", "aceclofenac",
    "amoxicillin", "amoxiclav", "azithromycin", "ciprofloxacin", "levofloxacin", "moxifloxacin",
    "doxycycline", "cefixime", "cefuroxime", "cephalexin", "metronidazole", "nitrofurantoin",
    "clarithromycin", "fluconazole", "clotrimazole", "acyclovir", "albendazole", "ivermectin",
    "metformin", "glimepiride", "gliclazide", "sitagliptin", "vildagliptin", "insulin",
    "amlodipine", "telmisartan", "losartan", "olmesartan", "enalapril", "ramipril", "lisinopril",
    "atenolol", "metoprolol", "propranolol", "bisoprolol", "hydrochlorothiazide", "chlorthalidone",
    "furosemide", "spironolactone", "atorvastatin", "rosuvastatin", "clopidogrel", "warfarin",
    "levothyroxine", "thyroxine", "carbimazole", "prednisolone", "methylprednisolone",
    "dexamethasone", "hydrocortisone", "salbutamol", "budesonide", "formoterol", "montelukast",
    "fluticasone", "levocetirizine", "cetirizine", "fexofenadine", "loratadine", "chlorpheniramine",
    "pantoprazole", "omeprazole", "rabeprazole", "esomeprazole", "ranitidine", "famotidine",
    "domperidone", "ondansetron", "metoclopramide", "loperamide", "lactulose", "bisacodyl",
    "sumatriptan", "rizatriptan", "gabapentin", "pregabalin", "amitriptyline", "sertraline",
    "escitalopram", "fluoxetine", "alprazolam", "clonazepam", "melatonin", "colchicine",
    "allopurinol", "febuxostat", "ferrous sulphate", "ferrous sulfate", "folic acid",
    "vitamin d3", "cholecalciferol", "calcium carbonate", "adapalene", "benzoyl peroxide",
    "mupirocin", "fusidic acid", "permethrin", "calamine", "antacid", "oral rehydration solution",
    "ors", "tramadol", "zinc",
)
FORMULATIONS = (
    "tablet", "tablets", "tab", "capsule", "capsules", "cap", "syrup", "suspension", "gel", "cream",
    "ointment", "lotion", "drops", "eye drops", "ear drops", "inhaler", "spray", "nasal spray",
    "injection", "solution", "sachet", "patch",
)
# Verbs that introduce a medication instruction.
MEDICATION_VERBS = (
    "prescribed", "started", "start", "starting", "continue", "continued", "increase", "increased",
    "decrease", "reduce", "switch to", "switched to", "change to", "add", "added", "stop", "stopped",
    "discontinue", "discontinued", "give", "given",
)
STOP_VERBS = ("stop", "stopped", "discontinue", "discontinued", "hold")
MEDICATION_WORDS = ("medication", "medications", "medicine", "medicines", "drug", "antibiotic")

# Phrases that introduce a follow-up instruction.
FOLLOW_UP_CUES = (
    "follow up", "follow-up", "followup", "review", "revisit", "return", "come back", "recheck",
    "re-check", "repeat", "next visit", "refer", "referred", "monitor", "reassess", "see again",
)

# Lifestyle and general advice (kept separate from medications and follow-up).
ADVICE_CUES = (
    "avoid", "advised", "advice", "rest", "diet", "plenty of", "maintain", "exercise", "exercises",
    "stretching", "hydration", "lifestyle", "counselling given", "elevation", "ice",
)

# Negation cues at the start of a clause ("No fever", "Denies chest pain").
NEGATION_START = ("no", "denies", "denied", "without", "negative for", "not", "nil", "absence of")
# Negation inside a clause ("X-ray shows no fracture").
NEGATION_INNER = ("shows no", "showed no", "reveals no", "revealed no", "with no", "no evidence of")
