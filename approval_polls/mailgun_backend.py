"""
Mailgun API email backend for Django.

This backend sends emails using Mailgun's REST API instead of SMTP.
"""

import requests
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend


class MailgunBackend(BaseEmailBackend):
    """
    Email backend that uses Mailgun's REST API to send emails.
    """

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = getattr(settings, "MAILGUN_API_KEY", None)
        self.domain = getattr(settings, "MAILGUN_DOMAIN", None)
        self.api_url = f"https://api.mailgun.net/v3/{self.domain}/messages"

    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number of
        email messages sent.
        """
        if not self.api_key or not self.domain:
            if not self.fail_silently:
                raise ValueError("MAILGUN_API_KEY and MAILGUN_DOMAIN must be set")
            return 0

        num_sent = 0
        for message in email_messages:
            if self._send(message):
                num_sent += 1
        return num_sent

    def _send(self, email_message):
        """
        Send a single email message via Mailgun API.
        """
        try:
            # Prepare the data for Mailgun API
            # Mailgun expects comma-separated strings for recipients
            data = {
                "from": email_message.from_email or settings.DEFAULT_FROM_EMAIL,
                "to": ", ".join(email_message.to),
                "subject": email_message.subject,
            }

            # Add CC and BCC if present
            if email_message.cc:
                data["cc"] = ", ".join(email_message.cc)
            if email_message.bcc:
                data["bcc"] = ", ".join(email_message.bcc)

            # Handle email body
            if email_message.body:
                data["text"] = email_message.body

            # Handle HTML alternative if present
            if hasattr(email_message, "alternatives") and email_message.alternatives:
                for content, mimetype in email_message.alternatives:
                    if mimetype == "text/html":
                        data["html"] = content
                        break

            # Send the request
            response = requests.post(
                self.api_url,
                auth=("api", self.api_key),
                data=data,
                timeout=10,
            )

            # Raise an exception if the request failed
            response.raise_for_status()
            return True

        except Exception:
            if not self.fail_silently:
                raise
            return False
