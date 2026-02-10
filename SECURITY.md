# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in InsightForge, please report it responsibly:

1. **Do not** create a public GitHub issue for security vulnerabilities
2. Email the maintainers directly with details of the vulnerability
3. Include steps to reproduce if possible
4. Allow reasonable time for a fix before public disclosure

## Security Measures

### Data Protection
- All API keys are encrypted at rest using Fernet encryption
- User passwords are hashed using bcrypt
- JWT tokens are used for authentication with configurable expiration

### API Security
- CORS is configured to allow only specified origins
- All endpoints require authentication except public routes
- Rate limiting can be configured via reverse proxy

### Infrastructure
- Docker containers run as non-root users
- Database credentials are injected via environment variables
- Secrets are never logged or exposed in error messages

## Best Practices for Users

1. **Use strong passwords** for your account
2. **Protect your API keys** - never share them or commit them to version control
3. **Use HTTPS** in production deployments
4. **Regularly rotate** your LLM provider API keys
5. **Review access logs** periodically if self-hosting

## Dependency Management

- Dependencies are automatically scanned via GitHub Dependabot
- Security updates are prioritized and applied promptly
- CI pipeline includes vulnerability scanning
