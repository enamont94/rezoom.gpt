"""
LaTeX Resume Renderer
Handles LaTeX template rendering and PDF generation
"""

import os
import subprocess
import tempfile
from jinja2 import Template
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class LaTeXRenderer:
    """LaTeX resume renderer with template support"""
    
    def __init__(self, template_dir: str = "templates"):
        self.template_dir = template_dir
        self.ensure_template_dir()
    
    def ensure_template_dir(self):
        """Ensure template directory exists"""
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir, exist_ok=True)
    
    def render_resume(self, resume_data: Dict[str, Any], template_name: str = "modern.tex") -> str:
        """
        Render resume using LaTeX template
        
        Args:
            resume_data: Resume data dictionary
            template_name: Name of the LaTeX template file
            
        Returns:
            Rendered LaTeX content as string
        """
        try:
            template_path = os.path.join(self.template_dir, template_name)
            
            if not os.path.exists(template_path):
                # Create default template
                self.create_default_template(template_path)
            
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Prepare data for template
            template_data = self.prepare_template_data(resume_data)
            
            # Render template
            template = Template(template_content)
            rendered_content = template.render(**template_data)
            
            return rendered_content
            
        except Exception as e:
            logger.error(f"Error rendering LaTeX template: {str(e)}")
            raise Exception(f"LaTeX rendering failed: {str(e)}")
    
    def generate_pdf(self, latex_content: str, output_path: str) -> str:
        """
        Generate PDF from LaTeX content
        
        Args:
            latex_content: LaTeX source code
            output_path: Path for output PDF file
            
        Returns:
            Path to generated PDF file
        """
        try:
            # Create temporary directory for LaTeX compilation
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write LaTeX file
                tex_file = os.path.join(temp_dir, "resume.tex")
                with open(tex_file, 'w', encoding='utf-8') as f:
                    f.write(latex_content)
                
                # Compile LaTeX to PDF
                self.compile_latex(tex_file, temp_dir)
                
                # Move PDF to final location
                temp_pdf = os.path.join(temp_dir, "resume.pdf")
                if os.path.exists(temp_pdf):
                    os.rename(temp_pdf, output_path)
                    return output_path
                else:
                    raise Exception("PDF file not generated")
                    
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise Exception(f"PDF generation failed: {str(e)}")
    
    def compile_latex(self, tex_file: str, output_dir: str):
        """Compile LaTeX file to PDF"""
        try:
            # Run pdflatex
            result = subprocess.run(
                [
                    "pdflatex",
                    "-interaction=nonstopmode",
                    f"-output-directory={output_dir}",
                    tex_file
                ],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                error_msg = f"LaTeX compilation failed: {result.stderr}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except subprocess.TimeoutExpired:
            raise Exception("LaTeX compilation timed out")
        except FileNotFoundError:
            raise Exception("pdflatex not found. Please install LaTeX distribution.")
    
    def prepare_template_data(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare resume data for template rendering"""
        
        # Extract basic information
        data = {
            "name": resume_data.get("name", "Your Name"),
            "title": resume_data.get("title", "Professional Title"),
            "email": resume_data.get("email", "your.email@example.com"),
            "phone": resume_data.get("phone", "(555) 123-4567"),
            "location": resume_data.get("location", "City, State"),
            "linkedin": resume_data.get("linkedin", ""),
            "website": resume_data.get("website", ""),
            "summary": resume_data.get("summary", ""),
            "experience": resume_data.get("experience", []),
            "education": resume_data.get("education", []),
            "skills": resume_data.get("skills", []),
            "certifications": resume_data.get("certifications", []),
            "projects": resume_data.get("projects", []),
            "languages": resume_data.get("languages", []),
            "watermark": resume_data.get("watermark", ""),
            "generated_date": resume_data.get("generated_date", ""),
        }
        
        # Process experience data
        if data["experience"]:
            data["experience"] = self.process_experience_data(data["experience"])
        
        # Process education data
        if data["education"]:
            data["education"] = self.process_education_data(data["education"])
        
        # Process skills data
        if data["skills"]:
            data["skills"] = self.process_skills_data(data["skills"])
        
        return data
    
    def process_experience_data(self, experience: list) -> list:
        """Process experience data for template"""
        processed = []
        
        for job in experience:
            if isinstance(job, dict):
                processed.append({
                    "title": job.get("title", ""),
                    "company": job.get("company", ""),
                    "location": job.get("location", ""),
                    "start_date": job.get("start_date", ""),
                    "end_date": job.get("end_date", ""),
                    "current": job.get("current", False),
                    "description": job.get("description", ""),
                    "achievements": job.get("achievements", [])
                })
        
        return processed
    
    def process_education_data(self, education: list) -> list:
        """Process education data for template"""
        processed = []
        
        for edu in education:
            if isinstance(edu, dict):
                processed.append({
                    "degree": edu.get("degree", ""),
                    "institution": edu.get("institution", ""),
                    "location": edu.get("location", ""),
                    "graduation_date": edu.get("graduation_date", ""),
                    "gpa": edu.get("gpa", ""),
                    "relevant_coursework": edu.get("relevant_coursework", [])
                })
        
        return processed
    
    def process_skills_data(self, skills: list) -> list:
        """Process skills data for template"""
        if isinstance(skills, str):
            # Split string into list
            skills = [skill.strip() for skill in skills.split(',')]
        
        return [skill for skill in skills if skill.strip()]
    
    def create_default_template(self, template_path: str):
        """Create default LaTeX template"""
        template_content = r"""
\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[margin=0.75in]{geometry}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{fontawesome}

% Custom colors
\definecolor{primary}{RGB}{0,119,255}
\definecolor{secondary}{RGB}{107,114,128}
\definecolor{accent}{RGB}{59,130,246}

% Remove page numbers
\pagestyle{empty}

% Custom section formatting
\titleformat{\section}{\large\bfseries\color{primary}}{}{0em}{}[\titlerule]
\titleformat{\subsection}{\normalsize\bfseries\color{accent}}{}{0em}{}

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
    {% if email %}{{ email }}{% endif %}{% if phone %} $\bullet$ {{ phone }}{% endif %}{% if location %} $\bullet$ {{ location }}{% endif %}
    {% if linkedin or website %}
    \\ \vspace{2pt}
    {% if linkedin %}\faLinkedin\ \href{https://linkedin.com/in/{{ linkedin }}}{linkedin.com/in/{{ linkedin }}}{% endif %}{% if linkedin and website %} $\bullet$ {% endif %}{% if website %}\faGlobe\ \href{https://{{ website }}}{{{ website }}}{% endif %}
    {% endif %}
\end{center}

% Professional Summary
{% if summary %}
\section{Professional Summary}
{{ summary }}
{% endif %}

% Experience
{% if experience %}
\section{Professional Experience}
\begin{itemize}[leftmargin=0.15in, label={}]
{% for job in experience %}
\resumesubheading
    {{{ job.title }}}{{{ job.end_date if not job.current else "Present" }}}
    {{{ job.company }}}{{{ job.start_date }}}
{% if job.description %}
\resumeitem{{{ job.description }}}
{% endif %}
{% if job.achievements %}
{% for achievement in job.achievements %}
\resumeitem{{{ achievement }}}
{% endfor %}
{% endif %}
{% endfor %}
\end{itemize}
{% endif %}

% Skills
{% if skills %}
\section{Key Skills}
\begin{itemize}[leftmargin=0.15in, label={}]
{% for skill in skills %}
\resumeitem{{{ skill }}}
{% endfor %}
\end{itemize}
{% endif %}

% Education
{% if education %}
\section{Education}
\begin{itemize}[leftmargin=0.15in, label={}]
{% for edu in education %}
\resumesubheading
    {{{ edu.degree }}}{{{ edu.graduation_date }}}
    {{{ edu.institution }}}{{{ edu.location }}}
{% if edu.gpa %}
\resumeitem{GPA: {{ edu.gpa }}}
{% endif %}
{% if edu.relevant_coursework %}
\resumeitem{Relevant Coursework: {{ edu.relevant_coursework | join(', ') }}
{% endif %}
{% endfor %}
\end{itemize}
{% endif %}

% Certifications
{% if certifications %}
\section{Certifications}
\begin{itemize}[leftmargin=0.15in, label={}]
{% for cert in certifications %}
\resumeitem{{{ cert }}}
{% endfor %}
\end{itemize}
{% endif %}

% Projects
{% if projects %}
\section{Projects}
\begin{itemize}[leftmargin=0.15in, label={}]
{% for project in projects %}
\resumeitem{{{ project }}}
{% endfor %}
\end{itemize}
{% endif %}

% Languages
{% if languages %}
\section{Languages}
\begin{itemize}[leftmargin=0.15in, label={}]
{% for language in languages %}
\resumeitem{{{ language }}}
{% endfor %}
\end{itemize}
{% endif %}

% Watermark
{% if watermark %}
\vfill
\begin{center}
\small \textcolor{secondary}{{{ watermark }}}
\end{center}
{% endif %}

\end{document}
"""
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
    
    def cleanup_temp_files(self, temp_dir: str):
        """Clean up temporary LaTeX files"""
        try:
            aux_files = ['.aux', '.log', '.out', '.toc', '.fdb_latexmk', '.fls', '.synctex.gz']
            
            for file in os.listdir(temp_dir):
                if any(file.endswith(ext) for ext in aux_files):
                    file_path = os.path.join(temp_dir, file)
                    if os.path.exists(file_path):
                        os.remove(file_path)
        except Exception as e:
            logger.warning(f"Error cleaning up temp files: {str(e)}")

# Utility functions
def check_latex_installation() -> bool:
    """Check if LaTeX is installed"""
    try:
        result = subprocess.run(
            ["pdflatex", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except:
        return False

def get_latex_version() -> str:
    """Get LaTeX version"""
    try:
        result = subprocess.run(
            ["pdflatex", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout.split('\n')[0]
        return "Unknown"
    except:
        return "Not installed"
