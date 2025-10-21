from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from dotenv import load_dotenv
import tempfile

load_dotenv()

router = APIRouter()

class EmailRequest(BaseModel):
    to_email: str
    subject: Optional[str] = None
    message: Optional[str] = None
    attachment_path: Optional[str] = None
    resume_data: Optional[dict] = None

class EmailResponse(BaseModel):
    success: bool
    message: str
    email_id: Optional[str] = None

@router.post("/send", response_model=EmailResponse)
async def send_email(request: EmailRequest):
    """
    Send resume via email
    """
    try:
        # Validate email
        if not request.to_email or "@" not in request.to_email:
            raise HTTPException(status_code=400, detail="Valid email address is required")
        
        # Get email configuration
        smtp_config = get_smtp_config()
        if not smtp_config:
            raise HTTPException(status_code=500, detail="Email configuration not found")
        
        # Prepare email content
        subject = request.subject or "Your ATS-Optimized Resume from Rezoom.ai"
        message = request.message or get_default_message()
        
        # Create email
        msg = MIMEMultipart()
        msg['From'] = smtp_config['from_email']
        msg['To'] = request.to_email
        msg['Subject'] = subject
        
        # Add message body
        msg.attach(MIMEText(message, 'html'))
        
        # Add attachment if provided
        if request.attachment_path and os.path.exists(request.attachment_path):
            with open(request.attachment_path, "rb") as attachment:
                part = MIMEApplication(attachment.read(), _subtype="pdf")
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(request.attachment_path)}'
                )
                msg.attach(part)
        
        # Send email
        with smtplib.SMTP(smtp_config['smtp_server'], smtp_config['smtp_port']) as server:
            server.starttls()
            server.login(smtp_config['username'], smtp_config['password'])
            server.send_message(msg)
        
        return EmailResponse(
            success=True,
            message="Email sent successfully",
            email_id=f"email_{request.to_email}_{int(time.time())}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")

@router.post("/send-resume")
async def send_resume_email(request: EmailRequest):
    """
    Send optimized resume via email with PDF attachment
    """
    try:
        if not request.resume_data:
            raise HTTPException(status_code=400, detail="Resume data is required")
        
        # Generate PDF first
        from routes.export import generate_pdf_resume
        import uuid
        
        filename = f"resume_{uuid.uuid4().hex[:8]}.pdf"
        filepath = os.path.join("tmp", filename)
        
        # Generate PDF
        pdf_path = await generate_pdf_resume(request.resume_data, filepath, True)
        
        # Send email with attachment
        email_request = EmailRequest(
            to_email=request.to_email,
            subject="Your ATS-Optimized Resume is Ready! 🎉",
            message=get_resume_email_template(request.resume_data),
            attachment_path=pdf_path
        )
        
        result = await send_email(email_request)
        
        # Clean up temporary file
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending resume email: {str(e)}")

def get_smtp_config():
    """Get SMTP configuration from environment variables"""
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    from_email = os.getenv("FROM_EMAIL", smtp_user)
    
    if not smtp_user or not smtp_pass:
        return None
    
    return {
        "username": smtp_user,
        "password": smtp_pass,
        "smtp_server": smtp_server,
        "smtp_port": smtp_port,
        "from_email": from_email
    }

def get_default_message():
    """Get default email message"""
    return """
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #0077FF;">Your Resume is Ready! 🎉</h2>
            
            <p>Thank you for using Rezoom.ai to optimize your resume!</p>
            
            <p>Your ATS-optimized resume has been generated and is attached to this email. 
            This resume has been specifically tailored to pass Applicant Tracking Systems 
            and increase your chances of landing interviews.</p>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="color: #0077FF; margin-top: 0;">What's Next?</h3>
                <ul>
                    <li>Review your optimized resume</li>
                    <li>Customize it further if needed</li>
                    <li>Apply to jobs with confidence!</li>
                </ul>
            </div>
            
            <p>Good luck with your job search!</p>
            
            <p>Best regards,<br>
            The Rezoom.ai Team</p>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            <p style="font-size: 12px; color: #666;">
                Generated with Rezoom.ai - AI Resume Builder that Beats the ATS Filters
            </p>
        </div>
    </body>
    </html>
    """

def get_resume_email_template(resume_data: dict):
    """Get personalized email template for resume delivery"""
    name = resume_data.get("name", "there")
    title = resume_data.get("title", "Professional")
    
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #0077FF;">Hi {name}! Your {title} Resume is Ready! 🎉</h2>
            
            <p>Great news! Your ATS-optimized resume has been generated and is attached to this email.</p>
            
            <div style="background-color: #e8f4fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="color: #0077FF; margin-top: 0;">✨ What We've Optimized:</h3>
                <ul style="margin: 10px 0;">
                    <li>Added relevant keywords from the job description</li>
                    <li>Enhanced with quantified achievements</li>
                    <li>Optimized for ATS compatibility</li>
                    <li>Improved formatting and structure</li>
                </ul>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="color: #0077FF; margin-top: 0;">🚀 Ready to Apply?</h3>
                <p>Your resume is now optimized to:</p>
                <ul>
                    <li>Pass ATS filters with flying colors</li>
                    <li>Stand out to recruiters and hiring managers</li>
                    <li>Land more interviews</li>
                </ul>
            </div>
            
            <p>We're excited to see where your optimized resume takes you!</p>
            
            <p>Best of luck with your job search,<br>
            The Rezoom.ai Team</p>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            <p style="font-size: 12px; color: #666;">
                Generated with Rezoom.ai - AI Resume Builder that Beats the ATS Filters
            </p>
        </div>
    </body>
    </html>
    """

@router.get("/config")
async def get_email_config():
    """
    Get email configuration status
    """
    smtp_config = get_smtp_config()
    
    if smtp_config:
        return {
            "configured": True,
            "smtp_server": smtp_config['smtp_server'],
            "from_email": smtp_config['from_email'],
            "message": "Email service is configured and ready"
        }
    else:
        return {
            "configured": False,
            "message": "Email service not configured. Please set SMTP_USER and SMTP_PASS environment variables."
        }

@router.post("/test")
async def test_email_config():
    """
    Test email configuration
    """
    try:
        smtp_config = get_smtp_config()
        if not smtp_config:
            raise HTTPException(status_code=400, detail="Email not configured")
        
        # Test SMTP connection
        with smtplib.SMTP(smtp_config['smtp_server'], smtp_config['smtp_port']) as server:
            server.starttls()
            server.login(smtp_config['username'], smtp_config['password'])
        
        return {
            "success": True,
            "message": "Email configuration test successful"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email test failed: {str(e)}")
