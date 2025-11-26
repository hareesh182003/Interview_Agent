# import os
# import json
# import logging
# from typing import Dict, Any
# import boto3
# from django.conf import settings

# logger = logging.getLogger(__name__)


# class AIAnalyzer:
#     """Universal Bedrock AI Analyzer — works with ANY model."""

#     def __init__(self, model_id: str = None):
#         self.model_id = model_id or settings.BEDROCK_MODEL_ID

#         self.client = boto3.client(
#             service_name='bedrock-runtime',
#             region_name=settings.AWS_REGION,
#             aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
#         )

#     # MAIN ENTRY ------------------------------------------------------
#     def analyze_resume_match(self, resume_text: str, job_description: str, model_id: str = None) -> Dict[str, Any]:
#         if model_id:
#             self.model_id = model_id

#         prompt = self._build_analysis_prompt(resume_text, job_description)

#         try:
#             # Build correct payload for any model
#             request_body = self._build_payload(self.model_id, prompt)

#             response = self.client.invoke_model(
#                 modelId=self.model_id,
#                 body=json.dumps(request_body)
#             )

#             raw = response["body"].read()
#             response_body = json.loads(raw)

#             # Extract AI text
#             text = self._extract_response_text(response_body)

#             # Convert to JSON
#             json_data = self._extract_json(text)

#             return self._structure_response(json_data)

#         except Exception as e:
#             logger.error(f"AI Analysis failed for model {self.model_id}: {str(e)}")
#             raise Exception(f"Analysis failed: {e}")

#     # MODEL PAYLOAD BUILDER -------------------------------------------
#     def _build_payload(self, model_id: str, prompt: str) -> dict:
#         """
#         Detect model family & generate correct request body.
#         """

#         # ---------------- Claude (Anthropic) --------------------
#         if "anthropic" in model_id:
#             return {
#                 "anthropic_version": "bedrock-2023-05-31",
#                 "max_tokens": 4096,
#                 "temperature": 0.2,
#                 "messages": [
#                     {"role": "user", "content": prompt}
#                 ]
#             }

#         # ---------------- Llama (Meta) --------------------------
#         if "meta.llama" in model_id:
#             return {
#                 "prompt": prompt,
#                 "max_gen_len": 4096,
#                 "temperature": 0.2
#             }

#         # ---------------- Amazon Titan Text ---------------------
#         if "amazon.titan-text" in model_id:
#             return {
#                 "inputText": prompt,
#                 "textGenerationConfig": {
#                     "maxTokenCount": 4096,
#                     "temperature": 0.2,
#                 }
#             }

#         # ---------------- Amazon Nova (requires PTU) ------------
#         if "amazon.nova" in model_id:
#             raise Exception(
#                 f"{model_id} requires Provisioned Throughput (PTU). Cannot run On-Demand."
#             )

#         # ---------------- Mistral Models ------------------------
#         if "mistral" in model_id:
#             return {
#                 "prompt": prompt,
#                 "max_tokens": 4096,
#                 "temperature": 0.2
#             }

#         # ---------------- Command R (Cohere) --------------------
#         if "cohere" in model_id:
#             return {
#                 "prompt": prompt,
#                 "max_tokens": 4096,
#                 "temperature": 0.2
#             }

#         # ---------------- Fallback (generic) ---------------------
#         return {
#             "prompt": prompt,
#             "max_tokens": 4096,
#             "temperature": 0.2
#         }

#     # RESPONSE EXTRACTION -----------------------------------------
#     def _extract_response_text(self, body: Dict[str, Any]) -> str:
#         """
#         Extract generated text depending on model's response shape.
#         """

#         # Anthropic Claude
#         if "content" in body and isinstance(body["content"], list):
#             return "".join([c.get("text", "") for c in body["content"]])

#         # Llama
#         if "generation" in body:
#             return body["generation"]

#         # Titan
#         if "results" in body and len(body["results"]) > 0:
#             return body["results"][0].get("outputText", "")

#         # Cohere / Others
#         if "output_text" in body:
#             return body["output_text"]

#         return json.dumps(body)

#     # JSON EXTRACTOR ---------------------------------------------
#     def _extract_json(self, text: str) -> Dict[str, Any]:
#         if "```json" in text:
#             return json.loads(text.split("```json")[1].split("```")[0].strip())

#         if "```" in text:
#             return json.loads(text.split("```")[1].strip())

#         try:
#             return json.loads(text)
#         except:
#             return {"raw_response": text}

#     # PROMPT -------------------------------------------------------
#     def _build_analysis_prompt(self, resume_text: str, job_description: str) -> str:
#         return f"""
# You are an expert ATS Analyzer. Compare the Resume and Job Description and return ONLY valid JSON.

# ### JOB DESCRIPTION:
# {job_description}

# ### RESUME:
# {resume_text}

# ### JSON FORMAT TO RETURN:
# {{
#   "match_percentage": 0,
#   "matching_skills": [],
#   "matching_education": "",
#   "matching_experience": "",
#   "highlighted_strengths": [],
#   "identified_gaps": [],
#   "detailed_analysis": {{
#     "skills_breakdown": {{
#       "required_skills": [],
#       "candidate_skills": [],
#       "matched_count": 0,
#       "total_required": 0
#     }},
#     "experience_analysis": {{
#       "required_years": "",
#       "candidate_years": "",
#       "relevant_roles": []
#     }},
#     "education_analysis": {{
#       "required": "",
#       "candidate": "",
#       "match_level": ""
#     }}
#   }}
# }}

# Return JSON only.
# """

#     # STRUCTURE FINAL OUTPUT ---------------------------------------
#     def _structure_response(self, ai_result: Dict[str, Any]) -> Dict[str, Any]:
#         return {
#             "match_percentage": float(ai_result.get("match_percentage", 0)),
#             "matching_skills": ai_result.get("matching_skills", []),
#             "matching_education": ai_result.get("matching_education", ""),
#             "matching_experience": ai_result.get("matching_experience", ""),
#             "highlighted_strengths": ai_result.get("highlighted_strengths", []),
#             "identified_gaps": ai_result.get("identified_gaps", []),
#             "detailed_analysis": ai_result.get("detailed_analysis", {}),
#             "raw_response": ai_result
#         }
import os
import json
import logging
from typing import Dict, Any
import boto3
from django.conf import settings

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """Universal Bedrock model analyzer compatible with ALL models."""

    def __init__(self, model_id: str = None):
        self.model_id = model_id or settings.BEDROCK_MODEL_ID

        self.client = boto3.client(
            "bedrock-runtime",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )

    # ----------------------------------------------------------------------
    # MAIN FUNCTION
    # ----------------------------------------------------------------------
    def analyze_resume_match(self, resume_text: str, job_description: str, model_id: str = None):
        if model_id:
            self.model_id = model_id

        prompt = self._build_prompt(resume_text, job_description)

        # Build correct payload for selected model
        payload = self._build_payload(self.model_id, prompt)

        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(payload)
            )

            raw = response["body"].read()
            body = json.loads(raw)

            # Extract AI text
            result_text = self._extract_text(body)
            json_data = self._extract_json(result_text)

            return self._structure_output(json_data)

        except Exception as e:
            logger.error(f"❌ Bedrock Error ({self.model_id}): {str(e)}")
            raise Exception(f"Analysis failed: {str(e)}")

    # ----------------------------------------------------------------------
    # MODEL PAYLOAD AUTO-DETECT
    # ----------------------------------------------------------------------
    def _build_payload(self, model_id: str, prompt: str):

        # 1️⃣ CLAUDE MODELS
        if "anthropic" in model_id:
            return {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "temperature": 0.2,
                "messages": [{"role": "user", "content": prompt}]
            }

        # 2️⃣ META LLAMA (prompt-based)
        if "meta.llama" in model_id:
            return {
                "prompt": prompt,
                "max_gen_len": 4096,
                "temperature": 0.2
            }

        # 3️⃣ AMAZON TITAN TEXT (inputText)
        if "amazon.titan-text" in model_id:
            return {
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 4096,
                    "temperature": 0.2
                }
            }

        # 4️⃣ AMAZON NOVA — Requires Provisioned Throughput (PTU)
        if "amazon.nova" in model_id:
            raise Exception(
                f"{model_id} cannot run on-demand. Requires Provisioned Throughput (PTU)."
            )

        # 5️⃣ MISTRAL / COHERE / FALLBACK MODELS
        return {
            "prompt": prompt,
            "max_tokens": 4096,
            "temperature": 0.2
        }

    # ----------------------------------------------------------------------
    # EXTRACT TEXT FROM MODEL RESPONSE
    # ----------------------------------------------------------------------
    def _extract_text(self, body):

        # Claude format
        if "content" in body:
            return "".join([c.get("text", "") for c in body["content"]])

        # Llama
        if "generation" in body:
            return body["generation"]

        # Titan
        if "results" in body:
            return body["results"][0].get("outputText", "")

        # Fallback
        return json.dumps(body)

    # ----------------------------------------------------------------------
    # PARSE JSON RESPONSE
    # ----------------------------------------------------------------------
    def _extract_json(self, text: str):

        if "```json" in text:
            return json.loads(text.split("```json")[1].split("```")[0].strip())

        if "```" in text:
            return json.loads(text.split("```")[1].strip())

        try:
            return json.loads(text)
        except:
            return {"raw_response": text}

    # ----------------------------------------------------------------------
    # BUILD PROMPT
    # ----------------------------------------------------------------------
    def _build_prompt(self, resume_text: str, job_description: str):
        return f"""
You are an ATS Resume Analyzer. Compare the resume with the job description and return ONLY valid JSON.

### JOB DESCRIPTION:
{job_description}

### RESUME:
{resume_text}

### JSON FORMAT:
{{
  "match_percentage": 0,
  "matching_skills": [],
  "matching_education": "",
  "matching_experience": "",
  "highlighted_strengths": [],
  "identified_gaps": [],
  "detailed_analysis": {{
    "skills_breakdown": {{
      "required_skills": [],
      "candidate_skills": [],
      "matched_count": 0,
      "total_required": 0
    }},
    "experience_analysis": {{
      "required_years": "",
      "candidate_years": "",
      "relevant_roles": []
    }},
    "education_analysis": {{
      "required": "",
      "candidate": "",
      "match_level": ""
    }}
  }}
}}

Return ONLY the JSON. Do not include any explanation.
        """

    # ----------------------------------------------------------------------
    # STANDARD OUTPUT FORMAT (matches Streamlit UI)
    # ----------------------------------------------------------------------
    def _structure_output(self, data):

        return {
            "match_percentage": float(data.get("match_percentage", 0)),
            "matching_skills": data.get("matching_skills", []),
            "matching_education": data.get("matching_education", ""),
            "matching_experience": data.get("matching_experience", ""),
            "highlighted_strengths": data.get("highlighted_strengths", []),
            "identified_gaps": data.get("identified_gaps", []),
            "detailed_analysis": data.get("detailed_analysis", {}),
            "raw_response": data,
            "processing_time": data.get("processing_time", 1.0),
            "session_id": os.urandom(6).hex(),
        }
