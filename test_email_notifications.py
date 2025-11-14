"""
Tests for Email Notification System
Tests email templates, service, and API endpoints
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from main import app
from email_service import EmailService, EmailServiceError
from email_templates import EmailTemplates


# ============================================================================
# Email Templates Tests
# ============================================================================


class TestEmailTemplates:
    """Test email template generation"""

    def test_contact_form_template(self):
        """Test contact form notification template"""
        result = EmailTemplates.contact_form_notification(
            name="John Doe",
            email="john@example.com",
            business_type="Healthcare",
            challenge="Need AI solution for patient data"
        )

        assert "subject" in result
        assert "html_content" in result
        assert "John Doe" in result["subject"]
        assert "Healthcare" in result["subject"]
        assert "john@example.com" in result["html_content"]
        assert "Need AI solution" in result["html_content"]

    def test_alert_template_info(self):
        """Test info alert template"""
        result = EmailTemplates.alert_notification(
            alert_type="System Update",
            message="Platform updated to v1.5.0",
            severity="info"
        )

        assert "subject" in result
        assert "html_content" in result
        assert "[INFO]" in result["subject"]
        assert "System Update" in result["subject"]
        assert "v1.5.0" in result["html_content"]

    def test_alert_template_warning(self):
        """Test warning alert template"""
        result = EmailTemplates.alert_notification(
            alert_type="High Lead Score",
            message="Lead scored 95/100 - urgent follow-up",
            severity="warning"
        )

        assert "[WARNING]" in result["subject"]
        assert "High Lead Score" in result["subject"]
        assert "95/100" in result["html_content"]

    def test_alert_template_error(self):
        """Test error alert template"""
        result = EmailTemplates.alert_notification(
            alert_type="API Failure",
            message="External API returned 500 error",
            severity="error"
        )

        assert "[ERROR]" in result["subject"]
        assert "500 error" in result["html_content"]

    def test_custom_template(self):
        """Test custom notification template"""
        result = EmailTemplates.custom_notification(
            subject="Weekly Report",
            title="Platform Usage Summary",
            body="<p>This week we processed 1,000 requests</p>"
        )

        assert result["subject"] == "Weekly Report"
        assert "Platform Usage Summary" in result["html_content"]
        assert "1,000 requests" in result["html_content"]


# ============================================================================
# Email Service Tests
# ============================================================================


class TestEmailService:
    """Test email service functionality"""

    @pytest.fixture
    def mock_env(self, monkeypatch):
        """Mock environment variables"""
        monkeypatch.setenv("SENDGRID_API_KEY", "test_api_key_123")
        monkeypatch.setenv("SENDGRID_FROM_EMAIL", "test@projectlavos.com")
        monkeypatch.setenv("SENDGRID_FROM_NAME", "Test Sender")
        monkeypatch.setenv("NOTIFICATION_RECIPIENTS", "recipient@example.com,admin@example.com")

    def test_parse_recipients(self, mock_env):
        """Test recipient parsing from environment"""
        service = EmailService()
        assert len(service.default_recipients) == 2
        assert "recipient@example.com" in service.default_recipients
        assert "admin@example.com" in service.default_recipients

    def test_no_api_key_warning(self, monkeypatch):
        """Test warning when API key is not configured"""
        monkeypatch.setenv("SENDGRID_API_KEY", "your_sendgrid_api_key_here")
        service = EmailService()
        assert service.client is None

    @patch('email_service.SendGridAPIClient')
    @pytest.mark.asyncio
    async def test_send_contact_form_notification(self, mock_sg_client, mock_env):
        """Test sending contact form notification"""
        # Mock SendGrid response
        mock_response = Mock()
        mock_response.status_code = 202
        mock_response.body = "success"
        mock_response.headers = {"x-message-id": "test123"}

        mock_client_instance = Mock()
        mock_client_instance.send = Mock(return_value=mock_response)
        mock_sg_client.return_value = mock_client_instance

        service = EmailService()
        result = await service.send_contact_form_notification(
            name="Test User",
            email="test@example.com",
            business_type="Tech",
            challenge="Testing email service"
        )

        assert result["status_code"] == 202
        assert mock_client_instance.send.called

    @patch('email_service.SendGridAPIClient')
    @pytest.mark.asyncio
    async def test_send_alert(self, mock_sg_client, mock_env):
        """Test sending alert notification"""
        mock_response = Mock()
        mock_response.status_code = 202
        mock_response.body = "success"
        mock_response.headers = {}

        mock_client_instance = Mock()
        mock_client_instance.send = Mock(return_value=mock_response)
        mock_sg_client.return_value = mock_client_instance

        service = EmailService()
        result = await service.send_alert(
            alert_type="Test Alert",
            message="This is a test alert",
            severity="info"
        )

        assert result["status_code"] == 202

    @patch('email_service.SendGridAPIClient')
    @pytest.mark.asyncio
    async def test_send_custom_notification(self, mock_sg_client, mock_env):
        """Test sending custom notification"""
        mock_response = Mock()
        mock_response.status_code = 202
        mock_response.body = "success"
        mock_response.headers = {}

        mock_client_instance = Mock()
        mock_client_instance.send = Mock(return_value=mock_response)
        mock_sg_client.return_value = mock_client_instance

        service = EmailService()
        result = await service.send_custom_notification(
            subject="Test Subject",
            title="Test Title",
            body="<p>Test body content</p>"
        )

        assert result["status_code"] == 202

    @pytest.mark.asyncio
    async def test_validation_no_api_key(self, monkeypatch):
        """Test validation fails without API key"""
        monkeypatch.setenv("SENDGRID_API_KEY", "your_sendgrid_api_key_here")

        service = EmailService()

        with pytest.raises(EmailServiceError, match="SendGrid not configured"):
            await service.send_alert(
                alert_type="Test",
                message="Test message"
            )


# ============================================================================
# API Endpoint Tests
# ============================================================================


class TestNotificationEndpoints:
    """Test notification API endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_email_service(self):
        """Mock email service for endpoint tests"""
        with patch('main.get_email_service') as mock:
            service_mock = Mock()
            service_mock.send_contact_form_notification = AsyncMock(
                return_value={"status_code": 202, "body": "success", "headers": {}}
            )
            service_mock.send_alert = AsyncMock(
                return_value={"status_code": 202, "body": "success", "headers": {}}
            )
            service_mock.send_custom_notification = AsyncMock(
                return_value={"status_code": 202, "body": "success", "headers": {}}
            )
            mock.return_value = service_mock
            yield service_mock

    def test_notify_contact_form(self, client, mock_email_service):
        """Test /api/notify with contact_form type"""
        response = client.post("/api/notify", json={
            "notification_type": "contact_form",
            "name": "John Doe",
            "email": "john@example.com",
            "business_type": "Healthcare",
            "challenge": "Need AI solution"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Contact form notification sent" in data["message"]
        assert mock_email_service.send_contact_form_notification.called

    def test_notify_contact_form_missing_fields(self, client, mock_email_service):
        """Test /api/notify contact_form with missing required fields"""
        response = client.post("/api/notify", json={
            "notification_type": "contact_form",
            "name": "John Doe"
            # Missing email, business_type, challenge
        })

        assert response.status_code == 400
        assert "requires: name, email, business_type, challenge" in response.json()["detail"]

    def test_notify_alert(self, client, mock_email_service):
        """Test /api/notify with alert type"""
        response = client.post("/api/notify", json={
            "notification_type": "alert",
            "alert_type": "High Lead Score",
            "message": "Lead scored 95/100",
            "severity": "warning"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Alert notification sent" in data["message"]
        assert mock_email_service.send_alert.called

    def test_notify_custom(self, client, mock_email_service):
        """Test /api/notify with custom type"""
        response = client.post("/api/notify", json={
            "notification_type": "custom",
            "subject": "Weekly Report",
            "title": "Platform Usage",
            "body": "<p>This week's metrics</p>",
            "recipients": ["custom@example.com"]
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Custom notification sent" in data["message"]
        assert mock_email_service.send_custom_notification.called

    def test_notify_invalid_type(self, client, mock_email_service):
        """Test /api/notify with invalid notification type"""
        response = client.post("/api/notify", json={
            "notification_type": "invalid_type",
            "message": "Test"
        })

        assert response.status_code == 400
        assert "Invalid notification_type" in response.json()["detail"]

    def test_health_check_includes_email(self, client):
        """Test health check shows email notification status"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "features" in data
        assert "email_notifications" in data["features"]


# ============================================================================
# Integration Tests
# ============================================================================


class TestEmailIntegration:
    """Integration tests for email notification flow"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @patch('main.get_email_service')
    def test_contact_form_sends_email(self, mock_get_service, client):
        """Test contact form automatically sends email notification"""
        # Mock email service
        service_mock = Mock()
        service_mock.send_contact_form_notification = AsyncMock(
            return_value={"status_code": 202}
        )
        mock_get_service.return_value = service_mock

        # Submit contact form
        response = client.post("/api/contact", json={
            "name": "Test User",
            "email": "test@example.com",
            "businessType": "Tech",
            "challenge": "Need AI solution"
        })

        assert response.status_code == 200
        assert service_mock.send_contact_form_notification.called

    @patch('main.get_email_service')
    def test_contact_form_succeeds_even_if_email_fails(self, mock_get_service, client):
        """Test contact form succeeds even if email notification fails"""
        # Mock email service to raise error
        service_mock = Mock()
        service_mock.send_contact_form_notification = AsyncMock(
            side_effect=EmailServiceError("SendGrid API error")
        )
        mock_get_service.return_value = service_mock

        # Submit contact form - should still succeed
        response = client.post("/api/contact", json={
            "name": "Test User",
            "email": "test@example.com",
            "businessType": "Tech",
            "challenge": "Need AI solution"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
