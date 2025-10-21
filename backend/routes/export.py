from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from typing import Dict, Any, List
import os
import tempfile
import subprocess
from jinja2 import Template
import uuid
from datetime import datetime

router = APIRouter()

class ExportRequest(BaseModel):
    resume_data: Dict[str, Any]
    format: str = "pdf"  # pdf, docx, html
    include_watermark: bool = True

class ExportResponse(BaseModel):
    success: bool
    download_url: str
    filename: str
    file_size: int
    message: str

@router.post("/pdf", response_model=ExportResponse)
async def export_pdf(request: ExportRequest):
    """
    Export resume as PDF using LaTeX
    """
    try:
        # Validate resume data
        if not request.resume_data:
            raise HTTPException(status_code=400, detail="Resume data is required")
        
        # Generate unique filename
        filename = f"resume_{uuid.uuid4().hex[:8]}.pdf"
        filepath = os.path.join("tmp", filename)
        
        # Generate PDF using LaTeX
        pdf_path = await generate_pdf_resume(request.resume_data, filepath, request.include_watermark)
        
        # Get file size
        file_size = os.path.getsize(pdf_path)
        
        return ExportResponse(
            success=True,
            download_url=f"/api/export/download/{filename}",
            filename=filename,
            file_size=file_size,
            message="PDF generated successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

@router.get("/download/{filename}")
async def download_file(filename: str):
    """
    Download generated resume file
    """
    try:
        filepath = os.path.join("tmp", filename)
        
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type="application/pdf"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")

async def generate_pdf_resume(resume_data: Dict[str, Any], output_path: str, include_watermark: bool = True) -> str:
    """
    Generate PDF resume using LaTeX template
    """
    try:
        # Load LaTeX template
        template_path = "templates/modern.tex"
        if not os.path.exists(template_path):
            # Create default template if it doesn't exist
            create_default_latex_template(template_path)
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Prepare data for template
        template_data = prepare_resume_data(resume_data, include_watermark)
        
        # Render template
        template = Template(template_content)
        latex_content = template.render(**template_data)
        
        # Write LaTeX file
        tex_filename = output_path.replace('.pdf', '.tex')
        with open(tex_filename, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        # Compile LaTeX to PDF
        compile_latex_to_pdf(tex_filename, output_path)
        
        # Clean up LaTeX files
        cleanup_latex_files(tex_filename)
        
        return output_path
        
    except Exception as e:
        raise Exception(f"Error generating PDF: {str(e)}")

def prepare_resume_data(resume_data: Dict[str, Any], include_watermark: bool) -> Dict[str, Any]:
    """Prepare resume data for LaTeX template"""
    
    # Extract basic info
    name = resume_data.get("name", "Your Name")
    title = resume_data.get("title", "Professional Title")
    email = resume_data.get("email", "your.email@example.com")
    phone = resume_data.get("phone", "(555) 123-4567")
    location = resume_data.get("location", "City, State")
    
    # Extract summary
    summary = resume_data.get("summary", "")
    if not summary and "sections" in resume_data:
        summary = resume_data["sections"].get("summary", "")
    
    # Extract experience
    experience = resume_data.get("experience", [])
    if not experience and "sections" in resume_data:
        experience_text = resume_data["sections"].get("experience", "")
        experience = parse_experience_text(experience_text)
    
    # Extract skills
    skills = resume_data.get("skills", [])
    if not skills and "sections" in resume_data:
        skills_text = resume_data["sections"].get("skills", "")
        skills = parse_skills_text(skills_text)
    
    # Extract education
    education = resume_data.get("education", "")
    if not education and "sections" in resume_data:
        education = resume_data["sections"].get("education", "")
    
    # Add watermark if requested
    watermark = ""
    if include_watermark:
        watermark = "Generated with Rezoom.ai"
    
    return {
        "name": name,
        "title": title,
        "email": email,
        "phone": phone,
        "location": location,
        "summary": summary,
        "experience": experience,
        "skills": skills,
        "education": education,
        "watermark": watermark,
        "generated_date": datetime.now().strftime("%B %Y")
    }

def parse_experience_text(experience_text: str) -> List[Dict[str, str]]:
    """Parse experience text into structured format"""
    experience = []
    
    if not experience_text:
        return experience
    
    # Simple parsing - split by lines and look for job patterns
    lines = experience_text.split('\n')
    current_job = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Look for job title patterns
        if any(word in line.lower() for word in ['engineer', 'developer', 'manager', 'analyst', 'specialist', 'coordinator']):
            if current_job:
                experience.append(current_job)
            current_job = {
                "title": line,
                "company": "",
                "years": "",
                "description": ""
            }
        elif current_job and not current_job["company"]:
            current_job["company"] = line
        elif current_job and not current_job["years"] and any(char.isdigit() for char in line):
            current_job["years"] = line
        elif current_job:
            current_job["description"] += line + " "
    
    if current_job:
        experience.append(current_job)
    
    return experience

def parse_skills_text(skills_text: str) -> List[str]:
    """Parse skills text into list"""
    if not skills_text:
        return []
    
    # Split by common separators
    skills = re.split(r'[,;•\n]', skills_text)
    skills = [skill.strip() for skill in skills if skill.strip()]
    
    return skills[:20]  # Limit to 20 skills

def compile_latex_to_pdf(tex_file: str, output_file: str):
    """Compile LaTeX file to PDF using pdflatex"""
    try:
        # Run pdflatex
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-output-directory=tmp", tex_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            raise Exception(f"LaTeX compilation failed: {result.stderr}")
        
        # Move PDF to final location
        base_name = os.path.splitext(os.path.basename(tex_file))[0]
        temp_pdf = os.path.join("tmp", f"{base_name}.pdf")
        
        if os.path.exists(temp_pdf):
            os.rename(temp_pdf, output_file)
        else:
            raise Exception("PDF file not generated")
            
    except subprocess.TimeoutExpired:
        raise Exception("LaTeX compilation timed out")
    except FileNotFoundError:
        raise Exception("pdflatex not found. Please install LaTeX distribution.")

def cleanup_latex_files(tex_file: str):
    """Clean up LaTeX auxiliary files"""
    base_name = os.path.splitext(tex_file)[0]
    aux_files = ['.aux', '.log', '.out', '.toc', '.fdb_latexmk', '.fls', '.synctex.gz']
    
    for ext in aux_files:
        aux_file = base_name + ext
        if os.path.exists(aux_file):
            try:
                os.remove(aux_file)
            except:
                pass

def create_default_latex_template(template_path: str):
    """Create default LaTeX template if it doesn't exist"""
    template_content = r"""
\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[margin=0.75in]{geometry}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{xcolor}
\usepackage{titlesec}

% Custom colors
\definecolor{primary}{RGB}{0,119,255}
\definecolor{secondary}{RGB}{107,114,128}

% Remove page numbers
\pagestyle{empty}

% Custom section formatting
\titleformat{\section}{\large\bfseries\color{primary}}{}{0em}{}[\titlerule]
\titleformat{\subsection}{\normalsize\bfseries}{}{0em}{}

% Custom commands
\newcommand{\resumeitem}[1]{\item\small{#1}}
\newcommand{\resumesubheading}[4]{
  \vspace{-1pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-5pt}
}

\newcommand{\resumesubitem}[1]{\resumeitem{#1}\vspace{-4pt}}

\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}

\begin{document}

% Header
\begin{center}
    {\Huge \textbf{\textcolor{primary}{{{ name }}}}} \\
    \vspace{2pt}
    {\large \textbf{{{ title }}}} \\
    \vspace{4pt}
    {{ email }} $\bullet$ {{ phone }} $\bullet$ {{ location }}
\end{center}

% Professional Summary
\section{Professional Summary}
{{ summary }}

% Experience
\section{Professional Experience}
\begin{itemize}[leftmargin=0.15in, label={}]
{% for job in experience %}
\resumesubheading
    {{{ job.title }}}{{{ job.years }}}
    {{{ job.company }}}{{{ job.description }}}
{% endfor %}
\end{itemize}

% Skills
\section{Key Skills}
\begin{itemize}[leftmargin=0.15in, label={}]
{% for skill in skills %}
\resumeitem{{{ skill }}}
{% endfor %}
\end{itemize}

% Education
\section{Education}
{{ education }}

% Watermark
{% if watermark %}
\vfill
\begin{center}
\small \textcolor{secondary}{{{ watermark }}}
\end{center}
{% endif %}

\end{document}
"""
    
    # Create templates directory if it doesn't exist
    os.makedirs(os.path.dirname(template_path), exist_ok=True)
    
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template_content)

@router.post("/docx")
async def export_docx(request: ExportRequest):
    """
    Export resume as DOCX (placeholder - would require python-docx implementation)
    """
    # This would require implementing DOCX generation
    # For now, return a message that this feature is coming soon
    return {
        "success": False,
        "message": "DOCX export coming soon. Please use PDF format for now."
    }

@router.get("/formats")
async def get_export_formats():
    """
    Get available export formats
    """
    return {
        "formats": [
            {
                "format": "pdf",
                "name": "PDF",
                "description": "High-quality PDF format, ATS-friendly",
                "available": True
            },
            {
                "format": "docx",
                "name": "Microsoft Word",
                "description": "Editable Word document",
                "available": False
            },
            {
                "format": "html",
                "name": "HTML",
                "description": "Web-friendly format",
                "available": False
            }
        ]
    }
