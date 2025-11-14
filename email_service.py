"""
Email Service for Project Lavos
SendGrid integration with retry logic and error handling
"""

import os
import logging
from typing import List, Dict, Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
from email_templates import EmailTemplates

logger = logging.getLogger(__name__)


class EmailServiceError(Exception):
    """Custom exception for email service errors"""
    pass


class EmailService:
    """
    Email notification service using SendGrid
    Features: HTML templates, retry logic, error handling
    """

    def __init__(self) -> None:
        """Initialize SendGrid client with API key from environment"""
        self.api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("SENDGRID_FROM_EMAIL", "noreply@projectlavos.com")
        self.from_name = os.getenv("SENDGRID_FROM_NAME", "Project Lavos")
        self.default_recipients = self._parse_recipients(
            os.getenv("NOTIFICATION_RECIPIENTS", "")
        )
        self.max_retries = int(os.getenv("EMAIL_MAX_RETRIES", "3"))
        self.retry_delay = int(os.getenv("EMAIL_RETRY_DELAY", "2"))

        # Initialize SendGrid client
        if not self.api_key or self.api_key == "your_sendgrid_api_key_here":
            logger.warning("SendGrid API key not configured - emails will not be sent")
            self.client = None
        else:
            self.client = SendGridAPIClient(self.api_key)

        self.templates = EmailTemplates()

    @staticmethod
    def _parse_recipients(recipients_str: str) -> List[str]:
        """Parse comma-separated recipient list"""
        if not recipients_str:
            return []
        return [email.strip() for email in recipients_str.split(",") if email.strip()]

    def _validate_config(self) -> None:
        """Validate email service configuration"""
        if not self.client:
            raise EmailServiceError(
                "SendGrid not configured. Set SENDGRID_API_KEY environment variable."
            )

        if not self.from_email or "@" not in self.from_email:
            raise EmailServiceError(
                f"Invalid from email: {self.from_email}. Set SENDGRID_FROM_EMAIL."
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=10),
        retry=retry_if_exception_type((Exception,)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    async def _send_email_with_retry(self, message: Mail) -> Dict:
        """
        Send email with automatic retry logic
        Args:
            message: SendGrid Mail object
        Returns:
            Response dict with status code and body
        Raises:
            EmailServiceError: If all retries fail
        """
        try:
            response = self.client.send(message)
            logger.info(f"Email sent successfully: {response.status_code}")

            return {
                "status_code": response.status_code,
                "body": response.body,
                "headers": dict(response.headers)
            }

        except Exception as e:
            logger.error(f"SendGrid API error: {str(e)}")
            raise EmailServiceError(f"Failed to send email: {str(e)}")

    async def send_contact_form_notification(
        self,
        name: str,
        email: str,
        business_type: str,
        challenge: str,
        recipients: Optional[List[str]] = None
    ) -> Dict:
        """
        Send contact form notification email
        Args:
            name: Contact name
            email: Contact email
            business_type: Type of business
            challenge: Challenge/inquiry description
            recipients: Override default recipients
        Returns:
            Response dict
        """
        self._validate_config()

        # Generate email from template
        email_data = self.templates.contact_form_notification(
            name=name,
            email=email,
            business_type=business_type,
            challenge=challenge
        )

        # Prepare recipients
        to_emails = recipients or self.default_recipients
        if not to_emails:
            raise EmailServiceError("No recipients configured")

        # Create message
        message = Mail(
            from_email=Email(self.from_email, self.from_name),
            to_emails=[To(recipient) for recipient in to_emails],
            subject=email_data["subject"],
            html_content=Content("text/html", email_data["html_content"])
        )

        # Send with retry
        logger.info(f"Sending contact form notification to {len(to_emails)} recipients")
        return await self._send_email_with_retry(message)

    async def send_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = "info",
        recipients: Optional[List[str]] = None
    ) -> Dict:
        """
        Send alert notification
        Args:
            alert_type: Alert type (e.g., "High Lead Score")
            message: Alert message
            severity: info, warning, error, success
            recipients: Override default recipients
        Returns:
            Response dict
        """
        self._validate_config()

        # Generate email from template
        email_data = self.templates.alert_notification(
            alert_type=alert_type,
            message=message,
            severity=severity
        )

        # Prepare recipients
        to_emails = recipients or self.default_recipients
        if not to_emails:
            raise EmailServiceError("No recipients configured")

        # Create message
        message = Mail(
            from_email=Email(self.from_email, self.from_name),
            to_emails=[To(recipient) for recipient in to_emails],
            subject=email_data["subject"],
            html_content=Content("text/html", email_data["html_content"])
        )

        # Send with retry
        logger.info(f"Sending alert notification: {alert_type} ({severity})")
        return await self._send_email_with_retry(message)

    async def send_custom_notification(
        self,
        subject: str,
        title: str,
        body: str,
        recipients: Optional[List[str]] = None
    ) -> Dict:
        """
        Send custom notification
        Args:
            subject: Email subject
            title: Notification title
            body: HTML body content
            recipients: Override default recipients
        Returns:
            Response dict
        """
        self._validate_config()

        # Generate email from template
        email_data = self.templates.custom_notification(
            subject=subject,
            title=title,
            body=body
        )

        # Prepare recipients
        to_emails = recipients or self.default_recipients
        if not to_emails:
            raise EmailServiceError("No recipients configured")

        # Create message
        message = Mail(
            from_email=Email(self.from_email, self.from_name),
            to_emails=[To(recipient) for recipient in to_emails],
            subject=email_data["subject"],
            html_content=Content("text/html", email_data["html_content"])
        )

        # Send with retry
        logger.info(f"Sending custom notification: {subject}")
        return await self._send_email_with_retry(message)


# Singleton instance
_email_service = None


def get_email_service() -> EmailService:
    """Get or create email service singleton"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
