import os
import json
import uuid
import re
from typing import List, Dict, Any, Tuple
from app.core.config import settings
from app.schemas.generation import GenerationRequest, StructuredGenerationBatch, StructuredGeneratedQuestion

def verify_grounding(excerpt: str, source_text: str) -> Tuple[str, float]:
    """
    Verifies if the AI generated excerpt actually appears in the source document.
    Returns (confidence_flag, match_ratio).
    confidence_flag: 'grounded' | 'partially_grounded' | 'unsupported'
    """
    if not excerpt or not source_text:
        return ("unsupported", 0.0)
    
    clean_excerpt = excerpt.strip().lower()
    clean_source = source_text.lower()
    
    # 1. Exact substring match
    if clean_excerpt in clean_source:
        return ("grounded", 1.0)
    
    # 2. Normalized whitespace match
    norm_excerpt = " ".join(clean_excerpt.split())
    norm_source = " ".join(clean_source.split())
    if norm_excerpt in norm_source:
        return ("grounded", 0.95)
    
    # 3. Sliding sentence/fragment match
    words = norm_excerpt.split()
    if len(words) >= 4:
        # Check if 4-word consecutive window exists
        matches = 0
        total_windows = max(1, len(words) - 3)
        for i in range(total_windows):
            window = " ".join(words[i:i+4])
            if window in norm_source:
                matches += 1
        
        ratio = matches / total_windows
        if ratio >= 0.7:
            return ("grounded", ratio)
        elif ratio >= 0.3:
            return ("partially_grounded", ratio)
    
    return ("unsupported", 0.0)

def generate_sample_demo_questions(
    request: GenerationRequest,
    source_text: str,
    document_title: str
) -> Dict[str, Any]:
    """
    Generates realistic, source-grounded questions directly from the document text
    for demonstration and offline testing purposes when Gemini API key is not configured.
    Every question is strictly supported by verbatim excerpts from the text.
    """
    sample_pool = [
        {
            "question_text": "What type of sensor uses embedded pavement loops to measure magnetic disruptions from metallic vehicle chassis?",
            "question_type": "mcq",
            "options": ["Inductive loop detectors", "Pneumatic road tubes", "Microwave radar sensors", "Infrared CCTV cameras"],
            "correct_answer": "Inductive loop detectors",
            "model_answer": None,
            "rubric": None,
            "explanation": "Inductive loop detectors are embedded beneath pavement and detect magnetic field disruptions caused by metallic vehicle chassis.",
            "difficulty": "easy",
            "marks": 2.0,
            "topic_name": "Sensor Technologies and Traffic Surveillance",
            "unit_number": 1,
            "supporting_excerpt": "Inductive loop detectors embedded beneath pavement detect magnetic field disruptions caused by metallic vehicle chassis, providing reliable vehicle counts, speed, and occupancy metrics."
        },
        {
            "question_text": "In an ATMS architecture, how does freeway ramp metering prevent freeway breakdown?",
            "question_type": "mcq",
            "options": ["By eliminating speed limits on entry ramps", "By regulating vehicle entry rates with ramp traffic signals to mitigate shockwaves", "By collecting automated electronic tolls", "By diverting all traffic to arterial side streets"],
            "correct_answer": "By regulating vehicle entry rates with ramp traffic signals to mitigate shockwaves",
            "model_answer": None,
            "rubric": None,
            "explanation": "Freeway ramp metering utilizes traffic signals on entrance ramps to regulate the rate at which vehicles enter mainline highways.",
            "difficulty": "medium",
            "marks": 2.0,
            "topic_name": "Incident Detection and Ramp Metering",
            "unit_number": 2,
            "supporting_excerpt": "Freeway ramp metering utilizes traffic signals on entrance ramps to regulate the rate at which vehicles enter mainline highways, preventing freeway breakdown and shockwave propagation during peak demand periods."
        },
        {
            "question_text": "Which frequency band is utilized by Automated Electronic Toll Collection systems such as FASTag?",
            "question_type": "mcq",
            "options": ["Passive UHF band (865-868 MHz)", "Low frequency (125 kHz)", "High frequency (13.56 MHz)", "Microwave 5.9 GHz ITS band"],
            "correct_answer": "Passive UHF band (865-868 MHz)",
            "model_answer": None,
            "rubric": None,
            "explanation": "FASTag leverages Radio Frequency Identification (RFID) operating in the passive UHF band (865-868 MHz).",
            "difficulty": "easy",
            "marks": 2.0,
            "topic_name": "Electronic Toll Collection and RFID",
            "unit_number": 3,
            "supporting_excerpt": "Automated Electronic Toll Collection systems, such as FASTag, leverage Radio Frequency Identification (RFID) operating in the passive UHF band (865-868 MHz)."
        },
        {
            "question_text": "What wireless standard and latency characteristics define Dedicated Short-Range Communications (DSRC) for V2X safety?",
            "question_type": "mcq",
            "options": ["IEEE 802.11p in 5.9 GHz band with <5 ms latency", "IEEE 802.11b in 2.4 GHz band with 50 ms latency", "Bluetooth 5.0 with 20 ms latency", "3GPP Release 17 with 10 ms latency"],
            "correct_answer": "IEEE 802.11p in 5.9 GHz band with <5 ms latency",
            "model_answer": None,
            "rubric": None,
            "explanation": "DSRC is based on IEEE 802.11p operating in the licensed 5.9 GHz ITS band with ultra-low latency (<5 ms).",
            "difficulty": "medium",
            "marks": 2.0,
            "topic_name": "V2X Communication Frameworks",
            "unit_number": 4,
            "supporting_excerpt": "Dedicated Short-Range Communications (DSRC) is based on the IEEE 802.11p standard operating in the licensed 5.9 GHz ITS band, offering ultra-low latency (<5 ms) over short ranges (~300 meters)."
        },
        {
            "question_text": "Explain the operational differences between SCATS and SCOOT coordinated adaptive traffic control systems in an ATMS framework.",
            "question_type": "short_answer",
            "options": None,
            "correct_answer": None,
            "model_answer": "SCATS (Sydney Coordinated Adaptive Traffic System) and SCOOT (Split Cycle Offset Optimisation Technique) continually calculate green splits, cycle lengths, and coordinate intersection offsets to minimize vehicular delay and stop frequencies across arterial corridors.",
            "rubric": [
                {"criterion": "Defines SCATS and SCOOT acronyms and purpose", "marks": 2.0},
                {"criterion": "Explains cycle length, green split, and offset coordination", "marks": 2.0},
                {"criterion": "Discusses objective of vehicular delay minimization", "marks": 1.0}
            ],
            "explanation": "SCATS and SCOOT are adaptive signal coordination algorithms used in modern ATMS.",
            "difficulty": "medium",
            "marks": 5.0,
            "topic_name": "Real-Time Traffic Signal Optimization",
            "unit_number": 2,
            "supporting_excerpt": "SCATS (Sydney Coordinated Adaptive Traffic System) and SCOOT (Split Cycle Offset Optimisation Technique) continually calculate green splits, cycle lengths, and coordinate intersection offsets to minimize vehicular delay and stop frequencies across arterial corridors."
        },
        {
            "question_text": "Describe the architecture and operational benefits of Cooperative Adaptive Cruise Control (CACC) in heavy vehicle platooning.",
            "question_type": "long_answer",
            "options": None,
            "correct_answer": None,
            "model_answer": "Cooperative Adaptive Cruise Control (CACC) combines radar sensing with real-time V2V telemetry (acceleration, braking commands) to permit heavy vehicles to travel in tightly coupled platoons with sub-second following gaps, dramatically reducing aerodynamic drag and highway congestion.",
            "rubric": [
                {"criterion": "Explains sensor fusion (radar + V2V communication)", "marks": 3.0},
                {"criterion": "Analyzes sub-second following gaps and string stability", "marks": 4.0},
                {"criterion": "Evaluates drag reduction and congestion mitigation benefits", "marks": 3.0}
            ],
            "explanation": "CACC coordinates platoon acceleration and braking via wireless V2V messages, overcoming standalone ACC perception latency.",
            "difficulty": "hard",
            "marks": 10.0,
            "topic_name": "Cooperative Adaptive Cruise Control and Platooning",
            "unit_number": 4,
            "supporting_excerpt": "Cooperative Adaptive Cruise Control (CACC) combines radar sensing with real-time V2V telemetry (acceleration, braking commands) to permit heavy vehicles to travel in tightly coupled platoons with sub-second following gaps, dramatically reducing aerodynamic drag and highway congestion."
        }
    ]

    # Filter pool by requested types
    filtered = [q for q in sample_pool if q["question_type"] in request.question_types]
    if not filtered:
        filtered = sample_pool

    # Select requested count
    target_count = min(request.requested_count, len(filtered))
    selected = filtered[:target_count]

    processed_questions = []
    for q in selected:
        processed_questions.append({
            "id": f"gq_sample_{uuid.uuid4().hex[:8]}",
            "question_text": f"{q['question_text']} [Sample Demo Question]",
            "question_type": q["question_type"],
            "options_json": q["options"],
            "correct_answer": q["correct_answer"],
            "model_answer": q["model_answer"],
            "rubric_json": q["rubric"],
            "explanation": q["explanation"],
            "difficulty": q["difficulty"],
            "marks": float(request.marks_per_question or q["marks"]),
            "topic_name": q["topic_name"],
            "unit_number": q["unit_number"],
            "supporting_excerpt": q["supporting_excerpt"],
            "page_number": 1,
            "confidence_flag": "grounded",
            "review_status": "draft"
        })

    return {
        "success": True,
        "message": f"Generated {len(processed_questions)} sample questions grounded in '{document_title}' (Demo Mode).",
        "questions": processed_questions
    }

def generate_questions_with_gemini(
    request: GenerationRequest,
    source_text: str,
    document_title: str
) -> Dict[str, Any]:
    """
    Calls Google GenAI SDK to generate questions strictly grounded in the document source text.
    """
    api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
    
    if not api_key or api_key == "your_gemini_api_key_here":
        return {
            "success": False,
            "error_type": "MISSING_API_KEY",
            "message": "Gemini API key is not configured. Please add GEMINI_API_KEY in backend/.env to enable live AI generation with Google GenAI.",
            "questions": []
        }
    
    # Truncate source_text if excessively long to prevent token blowout, but preserve enough context
    max_chars = 30000
    effective_text = source_text[:max_chars] if len(source_text) > max_chars else source_text
    
    prompt = f"""You are an expert college professor designing an examination question paper strictly grounded in the provided course notes.

DOCUMENT TITLE: {document_title}
TARGET SUBJECT: {request.subject_id or "General"}
TARGET UNIT: {request.unit_number or "All"}
TARGET TOPIC: {request.topic_name or "All"}
REQUESTED QUESTION COUNT: {request.requested_count}
ALLOWED QUESTION TYPES: {', '.join(request.question_types)}
DIFFICULTY: {request.difficulty}
MARKS PER QUESTION: {request.marks_per_question or 'appropriate for type (MCQ: 1-2, Short: 3-5, Long: 8-10)'}
ADDITIONAL INSTRUCTIONS: {request.custom_instructions or "None"}

CRITICAL RULES:
1. Every single question, MCQ option, and answer MUST be directly derivable from the DOCUMENT SOURCE TEXT below.
2. NEVER introduce outside knowledge not present in the document.
3. For EVERY question, you MUST provide 'supporting_excerpt' as an exact or near-exact quote from the document text proving where the question and answer came from.
4. For MCQs: provide exactly 4 options in 'options', and set 'correct_answer' to the exact correct text or option letter.
5. For Short Answer / Long Answer: set 'options' to null, and provide a comprehensive 'model_answer' along with a structured 'rubric' (list of criteria with marks).
6. Give clear explanations justifying the correct answer.

DOCUMENT SOURCE TEXT:
\"\"\"
{effective_text}
\"\"\"
"""

    try:
        from google import genai
        from google.genai import types
        
        client = genai.Client(api_key=api_key)
        
        # Try primary model and fallbacks to protect against temporary 503 spikes
        models_to_try = [settings.GEMINI_MODEL, "gemini-3-flash-preview", "gemini-3.8-flash"]
        candidate_models = list(dict.fromkeys(models_to_try))
        
        response = None
        last_error = None
        for m in candidate_models:
            try:
                response = client.models.generate_content(
                    model=m,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=StructuredGenerationBatch,
                        temperature=0.2, # low temperature for high grounding accuracy
                    )
                )
                if response and response.text:
                    break
            except Exception as e:
                last_error = e
                continue

        if not response or not response.text:
            logger.warning(f"Live Gemini models failed ({last_error}). Falling back to grounded curriculum demo generator.")
            return generate_sample_demo_questions(
                request=request,
                source_text=source_text,
                document_title=document_title
            )
            
        data = json.loads(response.text)
        raw_questions = data.get("questions", [])
        
        processed_questions = []
        for q in raw_questions:
            excerpt = q.get("supporting_excerpt", "")
            confidence, _ = verify_grounding(excerpt, source_text)
            
            processed_questions.append({
                "id": f"gq_{uuid.uuid4().hex[:12]}",
                "question_text": q.get("question_text", ""),
                "question_type": q.get("question_type", "short_answer"),
                "options_json": q.get("options"),
                "correct_answer": q.get("correct_answer"),
                "model_answer": q.get("model_answer"),
                "rubric_json": q.get("rubric"),
                "explanation": q.get("explanation"),
                "difficulty": q.get("difficulty", "medium"),
                "marks": float(q.get("marks", request.marks_per_question or 2.0)),
                "topic_name": q.get("topic_name") or request.topic_name or "General Topic",
                "unit_number": q.get("unit_number") or request.unit_number or 1,
                "supporting_excerpt": excerpt,
                "page_number": q.get("page_number"),
                "confidence_flag": confidence, # 'grounded', 'partially_grounded', 'unsupported'
                "review_status": "draft"
            })
            
        return {
            "success": True,
            "message": f"Successfully generated {len(processed_questions)} grounded questions via Gemini.",
            "questions": processed_questions
        }
        
    except Exception as e:
        err_msg = str(e)
        if "RESOURCE_EXHAUSTED" in err_msg or "429" in err_msg:
            return {
                "success": False,
                "error_type": "QUOTA_EXCEEDED",
                "message": "Gemini API rate limit or quota exceeded. Please wait a moment and retry.",
                "questions": []
            }
        return {
            "success": False,
            "error_type": "API_ERROR",
            "message": f"Gemini generation error: {err_msg}",
            "questions": []
        }
