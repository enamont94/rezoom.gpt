"""
ATS (Applicant Tracking System) Matching Utilities
Handles keyword matching and ATS compatibility scoring
"""

import re
from typing import List, Dict, Any, Tuple
from collections import Counter
import math

class ATSMatcher:
    """ATS compatibility matching and scoring"""
    
    def __init__(self):
        self.technical_skills = [
            'javascript', 'python', 'java', 'react', 'node.js', 'sql', 'aws', 'docker',
            'kubernetes', 'git', 'agile', 'scrum', 'machine learning', 'data analysis',
            'html', 'css', 'typescript', 'angular', 'vue', 'mongodb', 'postgresql',
            'redis', 'elasticsearch', 'kafka', 'microservices', 'api', 'rest', 'graphql',
            'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn', 'jupyter',
            'jenkins', 'terraform', 'ansible', 'linux', 'bash', 'powershell',
            'tableau', 'power bi', 'excel', 'vba', 'r', 'matlab', 'spark', 'hadoop'
        ]
        
        self.soft_skills = [
            'leadership', 'communication', 'teamwork', 'problem solving', 'project management',
            'collaboration', 'time management', 'adaptability', 'creativity', 'analytical',
            'critical thinking', 'attention to detail', 'multitasking', 'mentoring',
            'negotiation', 'presentation', 'writing', 'research', 'organization',
            'customer service', 'sales', 'marketing', 'strategy', 'innovation'
        ]
        
        self.action_verbs = [
            'led', 'developed', 'implemented', 'increased', 'improved', 'managed', 'created',
            'designed', 'built', 'launched', 'optimized', 'streamlined', 'coordinated',
            'supervised', 'trained', 'mentored', 'collaborated', 'delivered', 'achieved',
            'accomplished', 'executed', 'facilitated', 'initiated', 'organized', 'planned'
        ]
    
    def calculate_ats_score(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """
        Calculate ATS compatibility score between resume and job description
        
        Args:
            resume_text: Resume text content
            job_description: Job description text
            
        Returns:
            Dictionary with ATS score and analysis
        """
        try:
            # Extract keywords from job description
            job_keywords = self.extract_job_keywords(job_description)
            
            # Extract keywords from resume
            resume_keywords = self.extract_resume_keywords(resume_text)
            
            # Calculate keyword match score
            keyword_score = self.calculate_keyword_match(job_keywords, resume_keywords)
            
            # Calculate technical skills match
            technical_score = self.calculate_technical_skills_match(resume_text, job_description)
            
            # Calculate soft skills match
            soft_skills_score = self.calculate_soft_skills_match(resume_text, job_description)
            
            # Calculate experience level match
            experience_score = self.calculate_experience_match(resume_text, job_description)
            
            # Calculate education match
            education_score = self.calculate_education_match(resume_text, job_description)
            
            # Calculate action verbs score
            action_verbs_score = self.calculate_action_verbs_score(resume_text)
            
            # Calculate overall ATS score
            overall_score = self.calculate_overall_score({
                'keyword': keyword_score,
                'technical': technical_score,
                'soft_skills': soft_skills_score,
                'experience': experience_score,
                'education': education_score,
                'action_verbs': action_verbs_score
            })
            
            # Find missing keywords
            missing_keywords = self.find_missing_keywords(job_keywords, resume_keywords)
            
            # Generate improvement suggestions
            suggestions = self.generate_suggestions(overall_score, missing_keywords, resume_text, job_description)
            
            return {
                'overall_score': overall_score,
                'keyword_score': keyword_score,
                'technical_score': technical_score,
                'soft_skills_score': soft_skills_score,
                'experience_score': experience_score,
                'education_score': education_score,
                'action_verbs_score': action_verbs_score,
                'missing_keywords': missing_keywords,
                'suggestions': suggestions,
                'matched_keywords': self.find_matched_keywords(job_keywords, resume_keywords),
                'analysis': self.generate_analysis(overall_score, keyword_score, technical_score)
            }
            
        except Exception as e:
            return {
                'overall_score': 0,
                'error': f"Error calculating ATS score: {str(e)}"
            }
    
    def extract_job_keywords(self, job_description: str) -> List[str]:
        """Extract important keywords from job description"""
        if not job_description:
            return []
        
        # Convert to lowercase
        job_lower = job_description.lower()
        
        # Extract technical skills
        technical_found = [skill for skill in self.technical_skills if skill in job_lower]
        
        # Extract soft skills
        soft_skills_found = [skill for skill in self.soft_skills if skill in job_lower]
        
        # Extract other important words (capitalized words, specific terms)
        other_keywords = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', job_description)
        other_keywords = [kw.lower() for kw in other_keywords if len(kw) > 2]
        
        # Extract experience level keywords
        experience_keywords = []
        if re.search(r'\d+\+?\s*years?', job_lower):
            experience_keywords.append('years experience')
        if 'senior' in job_lower:
            experience_keywords.append('senior')
        if 'junior' in job_lower:
            experience_keywords.append('junior')
        if 'lead' in job_lower:
            experience_keywords.append('lead')
        
        # Combine all keywords
        all_keywords = technical_found + soft_skills_found + other_keywords + experience_keywords
        
        # Remove duplicates and return
        return list(set(all_keywords))
    
    def extract_resume_keywords(self, resume_text: str) -> List[str]:
        """Extract keywords from resume text"""
        if not resume_text:
            return []
        
        resume_lower = resume_text.lower()
        
        # Extract technical skills
        technical_found = [skill for skill in self.technical_skills if skill in resume_lower]
        
        # Extract soft skills
        soft_skills_found = [skill for skill in self.soft_skills if skill in resume_lower]
        
        # Extract action verbs
        action_verbs_found = [verb for verb in self.action_verbs if verb in resume_lower]
        
        # Extract other important words
        other_keywords = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', resume_text)
        other_keywords = [kw.lower() for kw in other_keywords if len(kw) > 2]
        
        # Combine all keywords
        all_keywords = technical_found + soft_skills_found + action_verbs_found + other_keywords
        
        # Remove duplicates and return
        return list(set(all_keywords))
    
    def calculate_keyword_match(self, job_keywords: List[str], resume_keywords: List[str]) -> Dict[str, Any]:
        """Calculate keyword match score"""
        if not job_keywords:
            return {'score': 0, 'matched': 0, 'total': 0, 'percentage': 0}
        
        matched_keywords = [kw for kw in job_keywords if kw in resume_keywords]
        
        score = len(matched_keywords)
        total = len(job_keywords)
        percentage = (score / total * 100) if total > 0 else 0
        
        return {
            'score': score,
            'matched': matched_keywords,
            'total': total,
            'percentage': round(percentage, 2)
        }
    
    def calculate_technical_skills_match(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """Calculate technical skills match score"""
        job_technical = [skill for skill in self.technical_skills if skill in job_description.lower()]
        resume_technical = [skill for skill in self.technical_skills if skill in resume_text.lower()]
        
        if not job_technical:
            return {'score': 0, 'matched': 0, 'total': 0, 'percentage': 0}
        
        matched_technical = [skill for skill in job_technical if skill in resume_technical]
        
        score = len(matched_technical)
        total = len(job_technical)
        percentage = (score / total * 100) if total > 0 else 0
        
        return {
            'score': score,
            'matched': matched_technical,
            'total': total,
            'percentage': round(percentage, 2)
        }
    
    def calculate_soft_skills_match(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """Calculate soft skills match score"""
        job_soft_skills = [skill for skill in self.soft_skills if skill in job_description.lower()]
        resume_soft_skills = [skill for skill in self.soft_skills if skill in resume_text.lower()]
        
        if not job_soft_skills:
            return {'score': 0, 'matched': 0, 'total': 0, 'percentage': 0}
        
        matched_soft_skills = [skill for skill in job_soft_skills if skill in resume_soft_skills]
        
        score = len(matched_soft_skills)
        total = len(job_soft_skills)
        percentage = (score / total * 100) if total > 0 else 0
        
        return {
            'score': score,
            'matched': matched_soft_skills,
            'total': total,
            'percentage': round(percentage, 2)
        }
    
    def calculate_experience_match(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """Calculate experience level match score"""
        # Extract years of experience from job description
        job_years = self.extract_years_from_text(job_description)
        resume_years = self.extract_years_from_text(resume_text)
        
        if not job_years:
            return {'score': 50, 'job_years': 0, 'resume_years': resume_years, 'match': True}
        
        # Calculate match score
        if resume_years >= job_years:
            score = 100
        elif resume_years >= job_years * 0.8:  # 80% of required experience
            score = 80
        elif resume_years >= job_years * 0.6:  # 60% of required experience
            score = 60
        else:
            score = 30
        
        return {
            'score': score,
            'job_years': job_years,
            'resume_years': resume_years,
            'match': resume_years >= job_years
        }
    
    def calculate_education_match(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """Calculate education match score"""
        # Education requirements from job description
        job_education = self.extract_education_requirements(job_description)
        resume_education = self.extract_education_from_resume(resume_text)
        
        if not job_education:
            return {'score': 50, 'job_education': [], 'resume_education': resume_education, 'match': True}
        
        # Check if resume has required education
        match = any(edu in resume_education for edu in job_education)
        score = 100 if match else 30
        
        return {
            'score': score,
            'job_education': job_education,
            'resume_education': resume_education,
            'match': match
        }
    
    def calculate_action_verbs_score(self, resume_text: str) -> Dict[str, Any]:
        """Calculate action verbs score"""
        resume_lower = resume_text.lower()
        found_verbs = [verb for verb in self.action_verbs if verb in resume_lower]
        
        score = min(100, len(found_verbs) * 10)  # 10 points per action verb, max 100
        
        return {
            'score': score,
            'found_verbs': found_verbs,
            'count': len(found_verbs)
        }
    
    def calculate_overall_score(self, scores: Dict[str, Dict[str, Any]]) -> int:
        """Calculate overall ATS score"""
        # Weighted scoring
        weights = {
            'keyword': 0.3,
            'technical': 0.25,
            'soft_skills': 0.15,
            'experience': 0.15,
            'education': 0.1,
            'action_verbs': 0.05
        }
        
        overall_score = 0
        for category, weight in weights.items():
            if category in scores:
                score = scores[category].get('score', 0)
                if isinstance(score, dict):
                    score = score.get('percentage', 0)
                overall_score += score * weight
        
        return min(100, max(0, round(overall_score)))
    
    def find_missing_keywords(self, job_keywords: List[str], resume_keywords: List[str]) -> List[str]:
        """Find keywords that are in job description but not in resume"""
        return [kw for kw in job_keywords if kw not in resume_keywords]
    
    def find_matched_keywords(self, job_keywords: List[str], resume_keywords: List[str]) -> List[str]:
        """Find keywords that match between job and resume"""
        return [kw for kw in job_keywords if kw in resume_keywords]
    
    def generate_suggestions(self, overall_score: int, missing_keywords: List[str], 
                           resume_text: str, job_description: str) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        if overall_score < 60:
            suggestions.append("Add more relevant keywords from the job description")
        
        if missing_keywords:
            top_missing = missing_keywords[:5]
            suggestions.append(f"Consider adding these keywords: {', '.join(top_missing)}")
        
        # Check for quantified achievements
        if not re.search(r'\d+', resume_text):
            suggestions.append("Add quantified achievements with specific numbers and metrics")
        
        # Check for action verbs
        action_verb_count = sum(1 for verb in self.action_verbs if verb in resume_text.lower())
        if action_verb_count < 3:
            suggestions.append("Use more strong action verbs to describe your achievements")
        
        # Check for professional summary
        if not any(keyword in resume_text.lower() for keyword in ['summary', 'objective', 'profile']):
            suggestions.append("Add a compelling professional summary section")
        
        return suggestions
    
    def generate_analysis(self, overall_score: int, keyword_score: Dict[str, Any], 
                         technical_score: Dict[str, Any]) -> Dict[str, str]:
        """Generate analysis of the ATS score"""
        analysis = {}
        
        # Overall score analysis
        if overall_score >= 80:
            analysis['overall'] = "Excellent ATS compatibility"
        elif overall_score >= 60:
            analysis['overall'] = "Good compatibility, minor improvements needed"
        elif overall_score >= 40:
            analysis['overall'] = "Fair compatibility, significant improvements needed"
        else:
            analysis['overall'] = "Poor compatibility, major optimization required"
        
        # Keyword analysis
        keyword_percentage = keyword_score.get('percentage', 0)
        if keyword_percentage >= 70:
            analysis['keywords'] = "Strong keyword match"
        elif keyword_percentage >= 50:
            analysis['keywords'] = "Moderate keyword match"
        else:
            analysis['keywords'] = "Weak keyword match"
        
        # Technical skills analysis
        technical_percentage = technical_score.get('percentage', 0)
        if technical_percentage >= 70:
            analysis['technical'] = "Strong technical skills match"
        elif technical_percentage >= 50:
            analysis['technical'] = "Moderate technical skills match"
        else:
            analysis['technical'] = "Weak technical skills match"
        
        return analysis
    
    def extract_years_from_text(self, text: str) -> int:
        """Extract years of experience from text"""
        if not text:
            return 0
        
        # Look for patterns like "5 years", "3+ years", etc.
        patterns = [
            r'(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*of\s*experience',
            r'(\d+)\+?\s*years?\s*in'
        ]
        
        max_years = 0
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                years = int(match)
                max_years = max(max_years, years)
        
        return max_years
    
    def extract_education_requirements(self, text: str) -> List[str]:
        """Extract education requirements from text"""
        education_requirements = []
        text_lower = text.lower()
        
        if 'bachelor' in text_lower or "bachelor's" in text_lower:
            education_requirements.append("Bachelor's Degree")
        if 'master' in text_lower or "master's" in text_lower:
            education_requirements.append("Master's Degree")
        if 'phd' in text_lower or 'doctorate' in text_lower:
            education_requirements.append("PhD")
        if 'certification' in text_lower or 'certified' in text_lower:
            education_requirements.append("Certification")
        
        return education_requirements
    
    def extract_education_from_resume(self, text: str) -> List[str]:
        """Extract education from resume text"""
        education = []
        text_lower = text.lower()
        
        if 'bachelor' in text_lower or "bachelor's" in text_lower:
            education.append("Bachelor's Degree")
        if 'master' in text_lower or "master's" in text_lower:
            education.append("Master's Degree")
        if 'phd' in text_lower or 'doctorate' in text_lower:
            education.append("PhD")
        if 'certification' in text_lower or 'certified' in text_lower:
            education.append("Certification")
        
        return education
