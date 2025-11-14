"""
Email Templates for Project Lavos Notifications
HTML email templates for various notification types
"""

from typing import Dict


class EmailTemplates:
    """HTML email templates with inline CSS for compatibility"""

    @staticmethod
    def base_template(title: str, content: str) -> str:
        """
        Base email template with consistent branding
        Args:
            title: Email subject/title
            content: HTML content to inject
        """
        gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        header_style = (
            f"background: {gradient}; padding: 30px; "
            "border-radius: 8px 8px 0 0;"
        )
        table_style = (
            "background-color: #ffffff; border-radius: 8px; "
            "box-shadow: 0 2px 4px rgba(0,0,0,0.1);"
        )
        footer_style = (
            "background-color: #f8f9fa; padding: 20px 30px; "
            "border-radius: 0 0 8px 8px; border-top: 1px solid #e0e0e0;"
        )
        link_style = "color: #667eea; text-decoration: none;"

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4;">
        <tr>
            <td align="center" style="padding: 40px 0;">
                <table width="600" cellpadding="0" cellspacing="0" style="{table_style}">
                    <!-- Header -->
                    <tr>
                        <td style="{header_style}">
                            <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: bold;">
                                Project Lavos
                            </h1>
                            <p style="margin: 5px 0 0 0; color: #e0e0e0; font-size: 14px;">
                                AI/ML Platform Notification
                            </p>
                        </td>
                    </tr>

                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            {content}
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="{footer_style}">
                            <p style="margin: 0; color: #666; font-size: 12px; text-align: center;">
                                Project Lavos - Louisville AI/ML Platform<br>
                                Matthew David Scott |
                                <a href="https://projectlavos.com" style="{link_style}">
                                    projectlavos.com
                                </a>
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
        """

    @staticmethod
    def contact_form_notification(
        name: str,
        email: str,
        business_type: str,
        challenge: str
    ) -> Dict[str, str]:
        """
        Template for new contact form submissions
        Args:
            name: Submitter name
            email: Submitter email
            business_type: Type of business
            challenge: Challenge description
        Returns:
            Dict with subject and html_content
        """
        content = f"""
<h2 style="margin: 0 0 20px 0; color: #333; font-size: 20px;">
    New Contact Form Submission
</h2>

<div style="background-color: #f8f9fa; padding: 20px; border-radius: 6px; margin-bottom: 20px;">
    <p style="margin: 0 0 15px 0; color: #333; font-size: 14px;">
        <strong style="color: #667eea;">Name:</strong><br>
        {name}
    </p>

    <p style="margin: 0 0 15px 0; color: #333; font-size: 14px;">
        <strong style="color: #667eea;">Email:</strong><br>
        <a href="mailto:{email}" style="color: #667eea; text-decoration: none;">{email}</a>
    </p>

    <p style="margin: 0 0 15px 0; color: #333; font-size: 14px;">
        <strong style="color: #667eea;">Business Type:</strong><br>
        {business_type}
    </p>

    <p style="margin: 0; color: #333; font-size: 14px;">
        <strong style="color: #667eea;">Challenge/Inquiry:</strong><br>
        {challenge}
    </p>
</div>

<div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 4px;">
    <p style="margin: 0; color: #856404; font-size: 14px;">
        <strong>Action Required:</strong> Respond within 24 hours
    </p>
</div>
        """

        subject = f"New Contact Form: {name} ({business_type})"
        html_content = EmailTemplates.base_template(subject, content)

        return {
            "subject": subject,
            "html_content": html_content
        }

    @staticmethod
    def alert_notification(
        alert_type: str,
        message: str,
        severity: str = "info"
    ) -> Dict[str, str]:
        """
        Template for system alerts and notifications
        Args:
            alert_type: Type of alert (e.g., "High Lead Score", "Phishing Detected")
            message: Alert message/details
            severity: info, warning, error, success
        Returns:
            Dict with subject and html_content
        """
        # Color coding based on severity
        severity_colors = {
            "info": {"bg": "#d1ecf1", "border": "#0c5460", "text": "#0c5460"},
            "warning": {"bg": "#fff3cd", "border": "#856404", "text": "#856404"},
            "error": {"bg": "#f8d7da", "border": "#721c24", "text": "#721c24"},
            "success": {"bg": "#d4edda", "border": "#155724", "text": "#155724"}
        }

        colors = severity_colors.get(severity, severity_colors["info"])

        alert_box_style = (
            f"background-color: {colors['bg']}; "
            f"border-left: 4px solid {colors['border']}; "
            "padding: 20px; border-radius: 4px; margin-bottom: 20px;"
        )
        alert_text_style = (
            f"margin: 0; color: {colors['text']}; "
            "font-size: 14px; line-height: 1.6;"
        )

        content = f"""
<h2 style="margin: 0 0 20px 0; color: #333; font-size: 20px;">
    {alert_type}
</h2>

<div style="{alert_box_style}">
    <p style="{alert_text_style}">
        {message}
    </p>
</div>

<p style="margin: 0; color: #666; font-size: 12px; font-style: italic;">
    This is an automated notification from Project Lavos AI/ML Platform
</p>
        """

        subject = f"[{severity.upper()}] {alert_type}"
        html_content = EmailTemplates.base_template(subject, content)

        return {
            "subject": subject,
            "html_content": html_content
        }

    @staticmethod
    def custom_notification(
        subject: str,
        title: str,
        body: str
    ) -> Dict[str, str]:
        """
        Template for custom notifications
        Args:
            subject: Email subject
            title: Notification title
            body: HTML body content
        Returns:
            Dict with subject and html_content
        """
        content = f"""
<h2 style="margin: 0 0 20px 0; color: #333; font-size: 20px;">
    {title}
</h2>

<div style="color: #333; font-size: 14px; line-height: 1.6;">
    {body}
</div>
        """

        html_content = EmailTemplates.base_template(subject, content)

        return {
            "subject": subject,
            "html_content": html_content
        }
