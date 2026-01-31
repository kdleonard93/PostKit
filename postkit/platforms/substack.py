import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

class SubstackPublisher:
    def __init__(self, credentials):
        self.publication_email = credentials['email']  
        self.smtp_host = credentials['smtp_host']     
        self.smtp_port = credentials['smtp_port']   
        self.smtp_user = credentials['smtp_user']   
        self.smtp_password = credentials['smtp_password'] 
        
        print(f"DEBUG Substack config:")
        print(f"  Email: {self.publication_email}")
        print(f"  SMTP Host: {self.smtp_host}")
        print(f"  SMTP Port: {self.smtp_port}")
        print(f"  SMTP User: {self.smtp_user}")
    
    def publish(self, content):
        """
        Send HTML email to Substack
        """
        try:
            # Create email
            msg = MIMEMultipart('related')
            msg['Subject'] = content['title']
            msg['From'] = self.smtp_user
            msg['To'] = self.publication_email
            
            # Add HTML content
            html_part = MIMEText(content['html'], 'html')
            msg.attach(html_part)
            
            # Send via SMTP
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.ehlo()
            server.starttls()
            server.ehlo() 
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"SMTP Error details: {e}")
            return False