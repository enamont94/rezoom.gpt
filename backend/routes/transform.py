from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

class TransformRequest(BaseModel):
    cv_text: str
    job_description: str
    tone: str = "professional"
    user_email: Optional[str] = None

class TransformResponse(BaseModel):
    success: bool
    optimized_resume: str
    improvements: list
    tone_applied: str
    message: str

@router.post("/resume", response_model=TransformResponse)
async def transform_resume(request: TransformRequest):
    """
    Transform resume using AI (Ollama + Mistral) to optimize for ATS
    """
    try:
        # Validate inputs
        if not request.cv_text.strip():
            raise HTTPException(status_code=400, detail="CV text is required")
        
        if not request.job_description.strip():
            raise HTTPException(status_code=400, detail="Job description is required")
        
        # Generate optimized resume using AI
        optimized_resume = await generate_ats_resume(
            cv_text=request.cv_text,
            job_description=request.job_description,
            tone=request.tone
        )
        
        # Extract improvements made
        improvements = extract_improvements(request.cv_text, optimized_resume)
        
        return TransformResponse(
            success=True,
            optimized_resume=optimized_resume,
            improvements=improvements,
            tone_applied=request.tone,
            message="Resume optimized successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error transforming resume: {str(e)}")

async def generate_ats_resume(cv_text: str, job_description: str, tone: str) -> str:
    """
    Generate ATS-optimized resume using Ollama + Mistral
    """
    try:
        # Construct the prompt for Mistral
        prompt = construct_optimization_prompt(cv_text, job_description, tone)
        
        # Call Ollama API
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        
        payload = {
            "model": "mistral",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 2000
            }
        }
        
        response = requests.post(
            f"{ollama_url}/api/generate",
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.status_code}")
        
        result = response.json()
        optimized_text = result.get("response", "")
        
        if not optimized_text:
            raise Exception("No response from AI model")
        
        return optimized_text
        
    except requests.exceptions.ConnectionError:
        # Fallback to rule-based optimization if Ollama is not available
        return fallback_optimization(cv_text, job_description, tone)
    except Exception as e:
        raise Exception(f"AI generation failed: {str(e)}")

def construct_optimization_prompt(cv_text: str, job_description: str, tone: str) -> str:
    """Construct the prompt for AI optimization"""
    
    tone_instructions = {
        "professional": "Use a formal, corporate tone with traditional business language.",
        "tech": "Use modern, technical language with industry-specific terminology and focus on technical achievements.",
        "creative": "Use innovative, dynamic language that showcases creativity and forward-thinking approach."
    }
    
    tone_instruction = tone_instructions.get(tone, tone_instructions["professional"])
    
    prompt = f"""
You are an expert ATS (Applicant Tracking System) resume optimizer and career coach.

TASK: Rewrite and optimize the following resume to maximize ATS compatibility and job match.

TONE: {tone_instruction}

JOB DESCRIPTION:
{job_description}

ORIGINAL RESUME:
{cv_text}

OPTIMIZATION REQUIREMENTS:
1. Use keywords from the job description naturally throughout the resume
2. Quantify achievements with specific numbers, percentages, and metrics
3. Use strong action verbs (Led, Developed, Implemented, Increased, etc.)
4. Ensure ATS-friendly formatting (no tables, simple layout)
5. Match the tone specified: {tone}
6. Keep content truthful but enhance impact
7. Focus on relevant experience for this specific role
8. Include a compelling professional summary
9. Organize sections logically: Contact, Summary, Experience, Skills, Education

OUTPUT FORMAT:
Provide the optimized resume in the following structure:

**CONTACT INFORMATION**
[Name, Email, Phone, Location, LinkedIn]

**PROFESSIONAL SUMMARY**
[2-3 sentences highlighting key qualifications and value proposition]

**PROFESSIONAL EXPERIENCE**
[Each role with: Job Title, Company, Dates, 3-4 bullet points with quantified achievements]

**KEY SKILLS**
[Relevant technical and soft skills from job description]

**EDUCATION**
[Degree, Institution, Year, relevant coursework or achievements]

**ADDITIONAL SECTIONS** (if relevant)
[Certifications, Projects, Languages, etc.]

Make sure the resume is:
- ATS-optimized with relevant keywords
- Quantified with specific metrics
- Tailored to the job description
- Professional and compelling
- Ready for immediate use

Generate the complete optimized resume now:
"""
    
    return prompt

def fallback_optimization(cv_text: str, job_description: str, tone: str) -> str:
    """
    Fallback optimization using rule-based approach when AI is not available
    """
    # Extract keywords from job description
    job_keywords = extract_keywords_from_job(job_description)
    
    # Basic optimization rules
    optimized_sections = []
    
    # Add contact section
    optimized_sections.append("**CONTACT INFORMATION**")
    optimized_sections.append("[Add your contact details here]")
    optimized_sections.append("")
    
    # Add professional summary
    optimized_sections.append("**PROFESSIONAL SUMMARY**")
    optimized_sections.append("Results-driven professional with expertise in key areas relevant to this position.")
    optimized_sections.append("")
    
    # Process experience section
    optimized_sections.append("**PROFESSIONAL EXPERIENCE**")
    optimized_sections.append("[Your work experience with quantified achievements]")
    optimized_sections.append("")
    
    # Add skills section with job keywords
    optimized_sections.append("**KEY SKILLS**")
    for keyword in job_keywords[:10]:  # Top 10 keywords
        optimized_sections.append(f"• {keyword.title()}")
    optimized_sections.append("")
    
    # Add education
    optimized_sections.append("**EDUCATION**")
    optimized_sections.append("[Your educational background]")
    
    return "\n".join(optimized_sections)

def extract_keywords_from_job(job_description: str) -> list:
    """Extract relevant keywords from job description"""
    # Common technical skills
    tech_skills = [
        'javascript', 'python', 'java', 'react', 'node.js', 'sql', 'aws', 'docker',
        'kubernetes', 'git', 'agile', 'scrum', 'machine learning', 'data analysis'
    ]
    
    # Common soft skills
    soft_skills = [
        'leadership', 'communication', 'teamwork', 'problem solving', 'project management',
        'collaboration', 'time management', 'adaptability', 'creativity', 'analytical'
    ]
    
    job_lower = job_description.lower()
    found_keywords = []
    
    for skill in tech_skills + soft_skills:
        if skill in job_lower:
            found_keywords.append(skill)
    
    return found_keywords

def extract_improvements(original: str, optimized: str) -> list:
    """Extract list of improvements made to the resume"""
    improvements = []
    
    # Check for keyword optimization
    if len(optimized.split()) > len(original.split()) * 1.2:
        improvements.append("Enhanced content with relevant keywords")
    
    # Check for quantified achievements
    import re
    numbers_in_optimized = len(re.findall(r'\d+', optimized))
    numbers_in_original = len(re.findall(r'\d+', original))
    
    if numbers_in_optimized > numbers_in_original:
        improvements.append("Added quantified achievements and metrics")
    
    # Check for action verbs
    action_verbs = ['led', 'developed', 'implemented', 'increased', 'improved', 'managed', 'created', 'designed']
    optimized_lower = optimized.lower()
    original_lower = original.lower()
    
    action_verb_count_opt = sum(1 for verb in action_verbs if verb in optimized_lower)
    action_verb_count_orig = sum(1 for verb in action_verbs if verb in original_lower)
    
    if action_verb_count_opt > action_verb_count_orig:
        improvements.append("Enhanced with strong action verbs")
    
    # Check for structure improvements
    if "**PROFESSIONAL SUMMARY**" in optimized:
        improvements.append("Added compelling professional summary")
    
    if "**KEY SKILLS**" in optimized:
        improvements.append("Organized skills section for better visibility")
    
    return improvements if improvements else ["General ATS optimization applied"]

@router.get("/health")
async def health_check():
    """Check if the transformation service is healthy"""
    try:
        # Check if Ollama is available
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        
        if response.status_code == 200:
            return {"status": "healthy", "ai_available": True}
        else:
            return {"status": "degraded", "ai_available": False}
    except:
        return {"status": "degraded", "ai_available": False}
