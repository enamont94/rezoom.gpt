"""
AI Engine for Resume Optimization
Handles AI-powered resume optimization using Ollama and Mistral
"""

import requests
import json
import os
from typing import Dict, Any, List, Optional
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class AIEngine:
    """AI engine for resume optimization using Ollama + Mistral"""
    
    def __init__(self):
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model = os.getenv("AI_MODEL", "mistral")
        self.timeout = int(os.getenv("AI_TIMEOUT", "60"))
    
    def optimize_resume(self, resume_text: str, job_description: str, 
                       tone: str = "professional") -> Dict[str, Any]:
        """
        Optimize resume using AI
        
        Args:
            resume_text: Original resume text
            job_description: Job description text
            tone: Resume tone (professional, tech, creative)
            
        Returns:
            Dictionary with optimized resume and metadata
        """
        try:
            # Check if Ollama is available
            if not self.check_ollama_availability():
                logger.warning("Ollama not available, using fallback optimization")
                return self.fallback_optimization(resume_text, job_description, tone)
            
            # Generate optimized resume
            optimized_text = self.generate_optimized_resume(resume_text, job_description, tone)
            
            # Extract improvements
            improvements = self.extract_improvements(resume_text, optimized_text)
            
            # Calculate optimization score
            optimization_score = self.calculate_optimization_score(resume_text, optimized_text)
            
            return {
                'success': True,
                'optimized_resume': optimized_text,
                'improvements': improvements,
                'optimization_score': optimization_score,
                'tone_applied': tone,
                'ai_model': self.model,
                'method': 'ai_optimization'
            }
            
        except Exception as e:
            logger.error(f"AI optimization failed: {str(e)}")
            return self.fallback_optimization(resume_text, job_description, tone)
    
    def generate_optimized_resume(self, resume_text: str, job_description: str, 
                                 tone: str) -> str:
        """Generate optimized resume using AI"""
        try:
            # Construct prompt
            prompt = self.construct_optimization_prompt(resume_text, job_description, tone)
            
            # Call Ollama API
            response = self.call_ollama_api(prompt)
            
            if not response:
                raise Exception("No response from AI model")
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating optimized resume: {str(e)}")
            raise Exception(f"AI generation failed: {str(e)}")
    
    def construct_optimization_prompt(self, resume_text: str, job_description: str, 
                                    tone: str) -> str:
        """Construct the prompt for AI optimization"""
        
        tone_instructions = {
            "professional": "Use a formal, corporate tone with traditional business language and focus on achievements and responsibilities.",
            "tech": "Use modern, technical language with industry-specific terminology, focus on technical achievements, and emphasize innovation and problem-solving.",
            "creative": "Use innovative, dynamic language that showcases creativity, forward-thinking approach, and artistic sensibility while maintaining professionalism."
        }
        
        tone_instruction = tone_instructions.get(tone, tone_instructions["professional"])
        
        prompt = f"""
You are an expert ATS (Applicant Tracking System) resume optimizer and career coach with 10+ years of experience helping professionals land their dream jobs.

TASK: Rewrite and optimize the following resume to maximize ATS compatibility and job match for the specific role.

TONE REQUIREMENT: {tone_instruction}

JOB DESCRIPTION:
{job_description}

ORIGINAL RESUME:
{resume_text}

OPTIMIZATION REQUIREMENTS:
1. Use keywords from the job description naturally throughout the resume
2. Quantify achievements with specific numbers, percentages, and metrics
3. Use strong action verbs (Led, Developed, Implemented, Increased, etc.)
4. Ensure ATS-friendly formatting (no tables, simple layout)
5. Match the tone specified: {tone}
6. Keep content truthful but enhance impact and relevance
7. Focus on experience most relevant to this specific role
8. Include a compelling professional summary
9. Organize sections logically: Contact, Summary, Experience, Skills, Education
10. Remove any irrelevant information that doesn't support the target role

OUTPUT FORMAT:
Provide the optimized resume in the following structure:

**CONTACT INFORMATION**
[Name, Email, Phone, Location, LinkedIn (if available)]

**PROFESSIONAL SUMMARY**
[2-3 sentences highlighting key qualifications and value proposition for this specific role]

**PROFESSIONAL EXPERIENCE**
[Each role with: Job Title, Company, Dates, 3-4 bullet points with quantified achievements]

**KEY SKILLS**
[Relevant technical and soft skills from job description, organized by category]

**EDUCATION**
[Degree, Institution, Year, relevant coursework or achievements if applicable]

**ADDITIONAL SECTIONS** (if relevant)
[Certifications, Projects, Languages, etc. - only if they support the target role]

IMPORTANT GUIDELINES:
- Make sure the resume is ATS-optimized with relevant keywords
- Quantify achievements with specific metrics and numbers
- Tailor content specifically to the job description
- Use professional, compelling language
- Ensure the resume is ready for immediate use
- Focus on results and impact, not just responsibilities
- Use industry-standard terminology from the job description

Generate the complete optimized resume now:
"""
        
        return prompt
    
    def call_ollama_api(self, prompt: str) -> str:
        """Call Ollama API to generate optimized resume"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 2000
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.status_code}")
            
            result = response.json()
            return result.get("response", "")
            
        except requests.exceptions.ConnectionError:
            raise Exception("Cannot connect to Ollama service")
        except requests.exceptions.Timeout:
            raise Exception("AI request timed out")
        except Exception as e:
            raise Exception(f"API call failed: {str(e)}")
    
    def check_ollama_availability(self) -> bool:
        """Check if Ollama service is available"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def fallback_optimization(self, resume_text: str, job_description: str, 
                            tone: str) -> Dict[str, Any]:
        """Fallback optimization using rule-based approach"""
        logger.info("Using fallback optimization")
        
        # Extract keywords from job description
        job_keywords = self.extract_keywords_from_job(job_description)
        
        # Basic optimization
        optimized_sections = []
        
        # Add contact section
        optimized_sections.append("**CONTACT INFORMATION**")
        optimized_sections.append("[Add your contact details here]")
        optimized_sections.append("")
        
        # Add professional summary
        optimized_sections.append("**PROFESSIONAL SUMMARY**")
        optimized_sections.append("Results-driven professional with expertise in key areas relevant to this position.")
        optimized_sections.append("")
        
        # Add experience section
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
        
        optimized_text = "\n".join(optimized_sections)
        
        return {
            'success': True,
            'optimized_resume': optimized_text,
            'improvements': ["Basic ATS optimization applied", "Keywords added from job description"],
            'optimization_score': 60,
            'tone_applied': tone,
            'ai_model': 'fallback',
            'method': 'rule_based_optimization'
        }
    
    def extract_keywords_from_job(self, job_description: str) -> List[str]:
        """Extract relevant keywords from job description"""
        if not job_description:
            return []
        
        # Common technical skills
        tech_skills = [
            'javascript', 'python', 'java', 'react', 'node.js', 'sql', 'aws', 'docker',
            'kubernetes', 'git', 'agile', 'scrum', 'machine learning', 'data analysis'
        ]
        
        job_lower = job_description.lower()
        found_keywords = []
        
        for skill in tech_skills:
            if skill in job_lower:
                found_keywords.append(skill)
        
        return found_keywords
    
    def extract_improvements(self, original: str, optimized: str) -> List[str]:
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
    
    def calculate_optimization_score(self, original: str, optimized: str) -> int:
        """Calculate optimization score based on improvements"""
        score = 50  # Base score
        
        # Check for keyword density improvement
        if len(optimized.split()) > len(original.split()) * 1.1:
            score += 10
        
        # Check for quantified achievements
        import re
        numbers_in_optimized = len(re.findall(r'\d+', optimized))
        numbers_in_original = len(re.findall(r'\d+', original))
        
        if numbers_in_optimized > numbers_in_original:
            score += 15
        
        # Check for action verbs
        action_verbs = ['led', 'developed', 'implemented', 'increased', 'improved', 'managed', 'created', 'designed']
        optimized_lower = optimized.lower()
        original_lower = original.lower()
        
        action_verb_count_opt = sum(1 for verb in action_verbs if verb in optimized_lower)
        action_verb_count_orig = sum(1 for verb in action_verbs if verb in original_lower)
        
        if action_verb_count_opt > action_verb_count_orig:
            score += 10
        
        # Check for structure improvements
        if "**PROFESSIONAL SUMMARY**" in optimized:
            score += 10
        
        if "**KEY SKILLS**" in optimized:
            score += 5
        
        return min(100, score)
    
    def get_available_models(self) -> List[str]:
        """Get list of available AI models"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except:
            return []
    
    def test_ai_connection(self) -> Dict[str, Any]:
        """Test AI connection and model availability"""
        try:
            # Test basic connection
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code != 200:
                return {
                    'available': False,
                    'error': f"Ollama service returned status {response.status_code}"
                }
            
            # Test model availability
            models = self.get_available_models()
            if self.model not in models:
                return {
                    'available': False,
                    'error': f"Model '{self.model}' not found. Available models: {models}"
                }
            
            # Test simple generation
            test_prompt = "Hello, this is a test."
            test_response = self.call_ollama_api(test_prompt)
            
            return {
                'available': True,
                'model': self.model,
                'models_available': models,
                'test_response': test_response[:100] + "..." if len(test_response) > 100 else test_response
            }
            
        except Exception as e:
            return {
                'available': False,
                'error': str(e)
            }
