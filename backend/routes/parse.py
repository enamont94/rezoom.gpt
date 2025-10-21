from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import fitz  # PyMuPDF
from docx import Document
import io
import re
from typing import Dict, Any

router = APIRouter()

@router.post("/resume")
async def parse_resume(file: UploadFile = File(...)):
    """
    Parse resume from PDF or DOCX file and extract text content
    """
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_extension = file.filename.lower().split('.')[-1]
        if file_extension not in ['pdf', 'docx', 'doc']:
            raise HTTPException(
                status_code=400, 
                detail="Unsupported file type. Please upload PDF or DOCX files only."
            )
        
        # Read file content
        content = await file.read()
        
        # Parse based on file type
        if file_extension == 'pdf':
            text = parse_pdf(content)
        elif file_extension in ['docx', 'doc']:
            text = parse_docx(content)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Clean and structure the text
        cleaned_text = clean_text(text)
        structured_data = structure_resume_text(cleaned_text)
        
        return JSONResponse(content={
            "success": True,
            "filename": file.filename,
            "file_size": len(content),
            "text": cleaned_text,
            "structured_data": structured_data,
            "word_count": len(cleaned_text.split()),
            "message": "Resume parsed successfully"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing resume: {str(e)}")

def parse_pdf(content: bytes) -> str:
    """Extract text from PDF using PyMuPDF"""
    try:
        doc = fitz.open(stream=content, filetype="pdf")
        text = ""
        
        for page in doc:
            text += page.get_text()
        
        doc.close()
        return text
    except Exception as e:
        raise Exception(f"Error parsing PDF: {str(e)}")

def parse_docx(content: bytes) -> str:
    """Extract text from DOCX using python-docx"""
    try:
        doc = Document(io.BytesIO(content))
        text = ""
        
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text
    except Exception as e:
        raise Exception(f"Error parsing DOCX: {str(e)}")

def clean_text(text: str) -> str:
    """Clean and normalize extracted text"""
    # Remove extra whitespace and normalize line breaks
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Remove common PDF artifacts
    text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}\"\'\/\@\#\$\%\&\*\+\=\<\>\|\\]', '', text)
    
    # Normalize bullet points
    text = re.sub(r'[•·▪▫‣⁃]', '•', text)
    
    return text.strip()

def structure_resume_text(text: str) -> Dict[str, Any]:
    """Extract structured information from resume text"""
    lines = text.split('\n')
    structured = {
        "name": "",
        "email": "",
        "phone": "",
        "summary": "",
        "experience": [],
        "education": [],
        "skills": [],
        "sections": {}
    }
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, text)
    if email_match:
        structured["email"] = email_match.group()
    
    # Extract phone
    phone_pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        structured["phone"] = phone_match.group()
    
    # Simple section detection
    sections = {
        "summary": ["summary", "objective", "profile", "about"],
        "experience": ["experience", "work history", "employment", "career"],
        "education": ["education", "academic", "qualifications"],
        "skills": ["skills", "technical skills", "competencies", "abilities"]
    }
    
    current_section = None
    current_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if line is a section header
        is_section_header = False
        for section_name, keywords in sections.items():
            if any(keyword in line.lower() for keyword in keywords):
                if current_section and current_content:
                    structured["sections"][current_section] = '\n'.join(current_content)
                current_section = section_name
                current_content = []
                is_section_header = True
                break
        
        if not is_section_header and current_section:
            current_content.append(line)
        elif not is_section_header and not current_section:
            # This might be the name or early content
            if not structured["name"] and len(line.split()) <= 3:
                structured["name"] = line
    
    # Add the last section
    if current_section and current_content:
        structured["sections"][current_section] = '\n'.join(current_content)
    
    return structured

@router.post("/job-description")
async def parse_job_description(job_text: str):
    """
    Parse job description text and extract key requirements
    """
    try:
        if not job_text.strip():
            raise HTTPException(status_code=400, detail="No job description provided")
        
        # Extract key information
        structured_job = extract_job_requirements(job_text)
        
        return JSONResponse(content={
            "success": True,
            "original_text": job_text,
            "structured_data": structured_job,
            "word_count": len(job_text.split()),
            "message": "Job description parsed successfully"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing job description: {str(e)}")

def extract_job_requirements(job_text: str) -> Dict[str, Any]:
    """Extract structured requirements from job description"""
    structured = {
        "title": "",
        "company": "",
        "location": "",
        "requirements": [],
        "responsibilities": [],
        "skills": [],
        "experience_level": "",
        "education": "",
        "benefits": []
    }
    
    lines = job_text.split('\n')
    
    # Extract job title (usually in first few lines)
    for line in lines[:5]:
        if any(word in line.lower() for word in ['engineer', 'developer', 'manager', 'analyst', 'specialist']):
            structured["title"] = line.strip()
            break
    
    # Extract skills and requirements
    skill_keywords = [
        'javascript', 'python', 'java', 'react', 'node.js', 'sql', 'aws', 'docker',
        'kubernetes', 'git', 'agile', 'scrum', 'leadership', 'communication'
    ]
    
    for line in lines:
        line_lower = line.lower()
        for skill in skill_keywords:
            if skill in line_lower:
                structured["skills"].append(skill.title())
    
    # Extract experience level
    experience_patterns = [
        r'(\d+)\+?\s*years?',
        r'entry.level',
        r'senior',
        r'junior',
        r'mid.level',
        r'lead'
    ]
    
    for pattern in experience_patterns:
        if re.search(pattern, job_text.lower()):
            structured["experience_level"] = re.search(pattern, job_text.lower()).group()
            break
    
    return structured
