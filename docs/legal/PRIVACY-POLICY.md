# Privacy Policy

This document describes how data is handled by the tools and systems built in this project.

## Data Processing

### What Data is Processed
- Only the data explicitly configured by the client (API inputs, email content, uploaded documents, etc.)
- No personal data is collected beyond what is required for the tool's core functionality
- Credentials and API keys are stored locally in environment variables, never in code or logs

### How Data is Processed
- All processing happens locally on the client's infrastructure (or their designated server)
- Data is processed in memory and written only to configured outputs (database, files, APIs)
- No data is sent to third-party analytics, tracking, or advertising services
- Third-party API calls (e.g., Claude API, Telegram API) transmit only the minimum data required for the service

### Data Retention
- Processed data is stored only in the outputs configured by the client
- Log files contain operational information only (timestamps, status codes, error messages) — not user data
- The client controls all data retention and deletion through their own infrastructure

## Third-Party Services

This project may integrate with the following types of third-party services:

| Service Type | Purpose | Data Sent |
|-------------|---------|-----------|
| AI/LLM APIs (e.g., Claude, OpenAI) | Text processing, chat responses | User queries and context documents |
| Messaging APIs (e.g., Telegram, Slack) | Notifications and alerts | Alert messages and metadata |
| Database services | Data storage | Processed/structured data |
| Email services (IMAP/SMTP) | Email reading and sending | Email content and attachments |

Each third-party service has its own privacy policy. The client should review the privacy policies of any services they choose to integrate.

## GDPR Compliance

For clients operating in the EU/EEA or processing EU resident data:

- **Lawful basis**: processing is based on the client's legitimate interest or contractual necessity
- **Data minimization**: only data required for the tool's function is processed
- **Right to erasure**: the client can delete all processed data from their own infrastructure at any time
- **Data portability**: all data is stored in standard formats (CSV, JSON, SQLite) that can be exported
- **No cross-border transfers**: data stays on the client's infrastructure unless they configure external API integrations
- **Data processor agreement**: available upon request for enterprise clients

## Security Measures

- All credentials stored in environment variables (`.env` files), never in source code
- `.env` files are excluded from version control via `.gitignore`
- HTTPS/TLS used for all external API communications
- Database connections use parameterized queries (no SQL injection)
- Input validation on all user-facing interfaces

## Client Responsibilities

The client is responsible for:
- Securing their own infrastructure (servers, databases, API keys)
- Complying with applicable privacy laws for their jurisdiction and use case
- Obtaining necessary consents from their end users (if applicable)
- Configuring data retention and deletion policies on their infrastructure

## Contact

For privacy-related questions about this project, contact the developer through the original project communication channel.

---
*This policy template is provided as a starting point. Clients with specific compliance requirements should consult their legal team.*
