"""
Text Cleaning Utilities
Handles text preprocessing and cleaning for resume and job descriptions
"""

import re
import string
from typing import List, Dict, Any
import unicodedata

class TextCleaner:
    """Text cleaning and preprocessing utilities"""
    
    def __init__(self):
        self.common_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
            'can', 'must', 'shall', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
            'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
    
    def clean_resume_text(self, text: str) -> str:
        """
        Clean and normalize resume text
        
        Args:
            text: Raw resume text
            
        Returns:
            Cleaned resume text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}\"\'\/\@\#\$\%\&\*\+\=\<\>\|\\]', '', text)
        
        # Normalize bullet points
        text = re.sub(r'[•·▪▫‣⁃]', '•', text)
        
        # Remove multiple line breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def clean_job_description(self, text: str) -> str:
        """
        Clean and normalize job description text
        
        Args:
            text: Raw job description text
            
        Returns:
            Cleaned job description text
        """
        if not text:
            return ""
        
        # Remove HTML tags if present
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}\"\'\/\@\#\$\%\&\*\+\=\<\>\|\\]', '', text)
        
        # Normalize bullet points
        text = re.sub(r'[•·▪▫‣⁃]', '•', text)
        
        # Remove multiple line breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def extract_keywords(self, text: str, min_length: int = 3) -> List[str]:
        """
        Extract keywords from text
        
        Args:
            text: Input text
            min_length: Minimum keyword length
            
        Returns:
            List of keywords
        """
        if not text:
            return []
        
        # Convert to lowercase
        text_lower = text.lower()
        
        # Remove punctuation
        text_clean = re.sub(r'[^\w\s]', ' ', text_lower)
        
        # Split into words
        words = text_clean.split()
        
        # Filter words
        keywords = []
        for word in words:
            if (len(word) >= min_length and 
                word not in self.common_words and 
                not word.isdigit()):
                keywords.append(word)
        
        return keywords
    
    def extract_technical_skills(self, text: str) -> List[str]:
        """
        Extract technical skills from text
        
        Args:
            text: Input text
            
        Returns:
            List of technical skills
        """
        if not text:
            return []
        
        # Common technical skills
        technical_skills = [
            'javascript', 'python', 'java', 'react', 'node.js', 'sql', 'aws', 'docker',
            'kubernetes', 'git', 'agile', 'scrum', 'machine learning', 'data analysis',
            'html', 'css', 'typescript', 'angular', 'vue', 'mongodb', 'postgresql',
            'redis', 'elasticsearch', 'kafka', 'microservices', 'api', 'rest', 'graphql',
            'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn', 'jupyter',
            'jenkins', 'terraform', 'ansible', 'linux', 'bash', 'powershell',
            'tableau', 'power bi', 'excel', 'vba', 'r', 'matlab', 'spark', 'hadoop'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in technical_skills:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        return list(set(found_skills))
    
    def extract_soft_skills(self, text: str) -> List[str]:
        """
        Extract soft skills from text
        
        Args:
            text: Input text
            
        Returns:
            List of soft skills
        """
        if not text:
            return []
        
        # Common soft skills
        soft_skills = [
            'leadership', 'communication', 'teamwork', 'problem solving', 'project management',
            'collaboration', 'time management', 'adaptability', 'creativity', 'analytical',
            'critical thinking', 'attention to detail', 'multitasking', 'mentoring',
            'negotiation', 'presentation', 'writing', 'research', 'organization',
            'customer service', 'sales', 'marketing', 'strategy', 'innovation'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in soft_skills:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        return list(set(found_skills))
    
    def extract_experience_level(self, text: str) -> str:
        """
        Extract experience level from text
        
        Args:
            text: Input text
            
        Returns:
            Experience level string
        """
        if not text:
            return "Unknown"
        
        text_lower = text.lower()
        
        # Experience level patterns
        if any(word in text_lower for word in ['senior', 'lead', 'principal', 'architect', 'director']):
            return "Senior"
        elif any(word in text_lower for word in ['junior', 'entry', 'graduate', 'intern']):
            return "Junior"
        elif any(word in text_lower for word in ['mid-level', 'intermediate', 'experienced']):
            return "Mid-level"
        elif re.search(r'\d+\+?\s*years?', text_lower):
            # Extract years of experience
            years_match = re.search(r'(\d+)\+?\s*years?', text_lower)
            if years_match:
                years = int(years_match.group(1))
                if years >= 5:
                    return "Senior"
                elif years >= 2:
                    return "Mid-level"
                else:
                    return "Junior"
        
        return "Unknown"
    
    def extract_education_requirements(self, text: str) -> List[str]:
        """
        Extract education requirements from text
        
        Args:
            text: Input text
            
        Returns:
            List of education requirements
        """
        if not text:
            return []
        
        text_lower = text.lower()
        education_requirements = []
        
        # Education level patterns
        if 'bachelor' in text_lower or 'bachelor\'s' in text_lower:
            education_requirements.append("Bachelor's Degree")
        if 'master' in text_lower or 'master\'s' in text_lower:
            education_requirements.append("Master's Degree")
        if 'phd' in text_lower or 'doctorate' in text_lower:
            education_requirements.append("PhD")
        if 'certification' in text_lower or 'certified' in text_lower:
            education_requirements.append("Certification")
        if 'diploma' in text_lower:
            education_requirements.append("Diploma")
        
        return education_requirements
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text for consistent processing
        
        Args:
            text: Input text
            
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        # Normalize unicode
        text = unicodedata.normalize('NFKD', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """
        Extract contact information from text
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with contact information
        """
        contact_info = {
            'email': '',
            'phone': '',
            'linkedin': '',
            'website': ''
        }
        
        if not text:
            return contact_info
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info['email'] = email_match.group()
        
        # Extract phone
        phone_pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact_info['phone'] = phone_match.group()
        
        # Extract LinkedIn
        linkedin_pattern = r'linkedin\.com/in/([a-zA-Z0-9-]+)'
        linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_match:
            contact_info['linkedin'] = linkedin_match.group(1)
        
        # Extract website
        website_pattern = r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})'
        website_match = re.search(website_pattern, text)
        if website_match:
            contact_info['website'] = website_match.group(1)
        
        return contact_info
    
    def remove_watermarks(self, text: str) -> str:
        """
        Remove common watermarks and boilerplate text
        
        Args:
            text: Input text
            
        Returns:
            Text with watermarks removed
        """
        if not text:
            return ""
        
        # Common watermarks and boilerplate
        watermarks = [
            'generated with',
            'created by',
            'powered by',
            'this document was',
            'confidential',
            'proprietary',
            'internal use only',
            'draft',
            'template',
            'sample'
        ]
        
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line_lower = line.lower()
            is_watermark = any(watermark in line_lower for watermark in watermarks)
            
            if not is_watermark:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """
        Extract sections from resume text
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with section names and content
        """
        sections = {}
        
        if not text:
            return sections
        
        # Common section headers
        section_patterns = {
            'summary': ['summary', 'objective', 'profile', 'about', 'overview'],
            'experience': ['experience', 'work history', 'employment', 'career', 'professional experience'],
            'education': ['education', 'academic', 'qualifications', 'degrees'],
            'skills': ['skills', 'technical skills', 'competencies', 'abilities', 'expertise'],
            'certifications': ['certifications', 'certificates', 'credentials', 'licenses'],
            'projects': ['projects', 'portfolio', 'work samples'],
            'languages': ['languages', 'language skills', 'bilingual']
        }
        
        lines = text.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue
            
            # Check if line is a section header
            is_section_header = False
            for section_name, keywords in section_patterns.items():
                if any(keyword in line_clean.lower() for keyword in keywords):
                    # Save previous section
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content)
                    
                    # Start new section
                    current_section = section_name
                    current_content = []
                    is_section_header = True
                    break
            
            if not is_section_header and current_section:
                current_content.append(line_clean)
            elif not is_section_header and not current_section:
                # This might be the name or early content
                if not any(section in sections for section in sections):
                    sections['header'] = line_clean
        
        # Save the last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
