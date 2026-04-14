# Delivery Checklist

What the client receives at project completion. Every item is verified before final handover.

## Code Delivery
- [ ] Complete source code in a private GitHub repository (or ZIP archive)
- [ ] All code pushed to the `main` branch, clean commit history
- [ ] No hardcoded credentials, API keys, or secrets in the codebase
- [ ] `.env.example` file documenting all required environment variables
- [ ] `requirements.txt` or `package.json` with pinned dependency versions
- [ ] `.gitignore` configured (no build artifacts, caches, or secrets)

## Documentation
- [ ] README.md with setup instructions, usage guide, and configuration reference
- [ ] Architecture overview (how components connect)
- [ ] API documentation (if applicable)
- [ ] Deployment guide (step-by-step for the target environment)
- [ ] Troubleshooting section for common issues

## Testing
- [ ] All features manually verified against the SOW requirements
- [ ] Edge cases tested and handled
- [ ] Error scenarios tested (invalid input, network failures, missing data)
- [ ] Performance verified under expected load

## Deployment (if included in scope)
- [ ] Application deployed to production environment
- [ ] Environment variables configured
- [ ] Monitoring and logging active
- [ ] Auto-restart configured (PM2, systemd, or equivalent)
- [ ] SSL/TLS configured (if web-facing)

## Handover
- [ ] Repository ownership transferred to client (or client added as admin)
- [ ] All credentials and access documented in a secure handover document
- [ ] Final walkthrough call (30 minutes) to demo the system
- [ ] Post-delivery support terms confirmed:
  - **30 days**: bug fixes for issues within the original scope
  - **Bugs only**: new features or scope changes are quoted separately
  - **Response time**: within 24 hours on business days

## Sign-Off
- [ ] Client confirms all deliverables received
- [ ] Client confirms system is working as expected
- [ ] Final payment released
- [ ] Project marked complete on Upwork

---
*Both parties review this checklist together during the final handover call.*
