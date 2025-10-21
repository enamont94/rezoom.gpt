from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import re
from collections import Counter
import math

router = APIRouter()

class ATSRequest(BaseModel):
    cv_text: str
    job_description: str

class ATSResponse(BaseModel):
    score: int
    missing_keywords: List[str]
    matched_keywords: List[str]
    suggestions: List[str]
    analysis: Dict[str, Any]

@router.post("/calculate", response_model=ATSResponse)
async def calculate_ats_score(request: ATSRequest):
    """
    Calculate ATS compatibility score between resume and job description
    """
    try:
        if not request.cv_text.strip():
            raise HTTPException(status_code=400, detail="CV text is required")
        
        if not request.job_description.strip():
            raise HTTPException(status_code=400, detail="Job description is required")
        
        # Extract keywords from job description
        job_keywords = extract_job_keywords(request.job_description)
        
        # Extract keywords from CV
        cv_keywords = extract_cv_keywords(request.cv_text)
        
        # Calculate compatibility score
        score_data = calculate_compatibility_score(job_keywords, cv_keywords)
        
        # Generate suggestions
        suggestions = generate_improvement_suggestions(score_data, job_keywords, cv_keywords)
        
        return ATSResponse(
            score=score_data["score"],
            missing_keywords=score_data["missing_keywords"],
            matched_keywords=score_data["matched_keywords"],
            suggestions=suggestions,
            analysis=score_data["analysis"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating ATS score: {str(e)}")

def extract_job_keywords(job_description: str) -> List[str]:
    """Extract important keywords from job description"""
    # Convert to lowercase for processing
    job_lower = job_description.lower()
    
    # Technical skills keywords
    technical_skills = [
        'javascript', 'python', 'java', 'react', 'node.js', 'sql', 'aws', 'docker',
        'kubernetes', 'git', 'agile', 'scrum', 'machine learning', 'data analysis',
        'html', 'css', 'typescript', 'angular', 'vue', 'mongodb', 'postgresql',
        'redis', 'elasticsearch', 'kafka', 'microservices', 'api', 'rest', 'graphql'
    ]
    
    # Soft skills keywords
    soft_skills = [
        'leadership', 'communication', 'teamwork', 'problem solving', 'project management',
        'collaboration', 'time management', 'adaptability', 'creativity', 'analytical',
        'critical thinking', 'attention to detail', 'multitasking', 'mentoring'
    ]
    
    # Experience level keywords
    experience_keywords = [
        'senior', 'junior', 'mid-level', 'entry-level', 'lead', 'principal', 'architect',
        'manager', 'director', 'years experience', 'experience with'
    ]
    
    # Education keywords
    education_keywords = [
        'bachelor', 'master', 'phd', 'degree', 'university', 'college', 'certification',
        'certified', 'diploma', 'coursework'
    ]
    
    # Industry-specific keywords
    industry_keywords = [
        'fintech', 'healthcare', 'e-commerce', 'saas', 'startup', 'enterprise',
        'cloud', 'devops', 'frontend', 'backend', 'full-stack', 'mobile'
    ]
    
    all_keywords = technical_skills + soft_skills + experience_keywords + education_keywords + industry_keywords
    
    # Find keywords that appear in job description
    found_keywords = []
    for keyword in all_keywords:
        if keyword in job_lower:
            found_keywords.append(keyword)
    
    # Also extract capitalized words (likely proper nouns/technologies)
    capitalized_words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', job_description)
    for word in capitalized_words:
        if len(word) > 2 and word.lower() not in found_keywords:
            found_keywords.append(word.lower())
    
    # Remove duplicates and return
    return list(set(found_keywords))

def extract_cv_keywords(cv_text: str) -> List[str]:
    """Extract keywords from CV text"""
    cv_lower = cv_text.lower()
    
    # Technical skills patterns
    technical_patterns = [
        r'\b(javascript|python|java|react|node\.js|sql|aws|docker|kubernetes|git)\b',
        r'\b(html|css|typescript|angular|vue|mongodb|postgresql|redis)\b',
        r'\b(agile|scrum|machine learning|data analysis|api|rest|graphql)\b'
    ]
    
    found_keywords = []
    for pattern in technical_patterns:
        matches = re.findall(pattern, cv_lower)
        found_keywords.extend(matches)
    
    # Extract skills from common sections
    skills_section = extract_skills_section(cv_text)
    if skills_section:
        skills_keywords = re.findall(r'\b\w+\b', skills_section.lower())
        found_keywords.extend(skills_keywords)
    
    # Remove duplicates and common words
    common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    found_keywords = [kw for kw in found_keywords if kw not in common_words and len(kw) > 2]
    
    return list(set(found_keywords))

def extract_skills_section(cv_text: str) -> str:
    """Extract skills section from CV"""
    lines = cv_text.split('\n')
    skills_section = ""
    in_skills = False
    
    for line in lines:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in ['skills', 'technical skills', 'competencies', 'abilities']):
            in_skills = True
            continue
        elif in_skills and line.strip():
            if any(keyword in line_lower for keyword in ['experience', 'education', 'work', 'employment']):
                break
            skills_section += line + " "
    
    return skills_section.strip()

def calculate_compatibility_score(job_keywords: List[str], cv_keywords: List[str]) -> Dict[str, Any]:
    """Calculate ATS compatibility score"""
    if not job_keywords:
        return {
            "score": 0,
            "missing_keywords": [],
            "matched_keywords": [],
            "analysis": {"error": "No keywords found in job description"}
        }
    
    # Find matched keywords
    matched_keywords = [kw for kw in job_keywords if kw in cv_keywords]
    
    # Calculate score
    match_percentage = (len(matched_keywords) / len(job_keywords)) * 100
    score = min(100, int(match_percentage))
    
    # Find missing keywords
    missing_keywords = [kw for kw in job_keywords if kw not in cv_keywords]
    
    # Analyze keyword importance
    analysis = {
        "total_job_keywords": len(job_keywords),
        "matched_keywords_count": len(matched_keywords),
        "missing_keywords_count": len(missing_keywords),
        "match_percentage": round(match_percentage, 2),
        "score_category": get_score_category(score)
    }
    
    return {
        "score": score,
        "missing_keywords": missing_keywords[:10],  # Top 10 missing
        "matched_keywords": matched_keywords,
        "analysis": analysis
    }

def get_score_category(score: int) -> str:
    """Get score category description"""
    if score >= 80:
        return "Excellent ATS compatibility"
    elif score >= 60:
        return "Good compatibility, minor improvements needed"
    elif score >= 40:
        return "Fair compatibility, significant improvements needed"
    else:
        return "Poor compatibility, major optimization required"

def generate_improvement_suggestions(score_data: Dict, job_keywords: List[str], cv_keywords: List[str]) -> List[str]:
    """Generate improvement suggestions based on analysis"""
    suggestions = []
    score = score_data["score"]
    missing_keywords = score_data["missing_keywords"]
    
    if score < 60:
        suggestions.append("Add more relevant keywords from the job description to your resume")
    
    if len(missing_keywords) > 0:
        top_missing = missing_keywords[:5]
        suggestions.append(f"Consider adding these keywords: {', '.join(top_missing)}")
    
    # Check for quantified achievements
    if not re.search(r'\d+', ' '.join(cv_keywords)):
        suggestions.append("Add quantified achievements with specific numbers and metrics")
    
    # Check for action verbs
    action_verbs = ['led', 'developed', 'implemented', 'increased', 'improved', 'managed', 'created']
    cv_text_lower = ' '.join(cv_keywords).lower()
    action_verb_count = sum(1 for verb in action_verbs if verb in cv_text_lower)
    
    if action_verb_count < 3:
        suggestions.append("Use more strong action verbs to describe your achievements")
    
    # Check for professional summary
    if not any(keyword in ' '.join(cv_keywords).lower() for keyword in ['summary', 'objective', 'profile']):
        suggestions.append("Add a compelling professional summary section")
    
    # Check for skills section
    if not any(keyword in ' '.join(cv_keywords).lower() for keyword in ['skills', 'technical', 'competencies']):
        suggestions.append("Create a dedicated skills section highlighting relevant abilities")
    
    return suggestions

@router.get("/keywords/{text_type}")
async def extract_keywords(text_type: str, text: str):
    """
    Extract keywords from text (job description or CV)
    """
    try:
        if text_type == "job":
            keywords = extract_job_keywords(text)
        elif text_type == "cv":
            keywords = extract_cv_keywords(text)
        else:
            raise HTTPException(status_code=400, detail="Invalid text type. Use 'job' or 'cv'")
        
        return {
            "success": True,
            "text_type": text_type,
            "keywords": keywords,
            "keyword_count": len(keywords)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting keywords: {str(e)}")
