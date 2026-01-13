# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| 0.1.x   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability within VideoDub, please send an email to [fldx123456@163.com](mailto:fldx123456@163.com). All security vulnerabilities will be promptly addressed.

Please do not publicly disclose the vulnerability until it has been fixed and a security release has been made.

## Security Considerations

### Data Handling
- VideoDub processes video files locally and does not transmit data to external servers
- Audio extraction and processing occurs entirely on your machine
- Translation models are downloaded from Hugging Face (secure HTTPS connections)

### Dependencies
We regularly audit our dependencies for security vulnerabilities:
- Automated security scanning in CI/CD pipeline
- Dependency updates checked with `safety` tool
- Static analysis with `bandit` for Python security issues

### Model Security
- Whisper models are loaded from official sources
- Translation models from Hugging Face undergo community review
- No model weights are modified or redistributed

## Best Practices

For secure usage of VideoDub:

1. **Keep dependencies updated**
   ```bash
   pip install --upgrade videodub
   ```

2. **Use virtual environments**
   ```bash
   python -m venv videodub-env
   source videodub-env/bin/activate
   ```

3. **Verify file sources**
   - Only process trusted video files
   - Scan input files for malware before processing

4. **Monitor resource usage**
   - Large video files may consume significant memory
   - Monitor system resources during processing

## Security Features

### Built-in Protections
- Input validation for file paths
- Safe temporary file handling
- Resource cleanup after processing
- Error handling to prevent crashes

### Coming Soon
- Sandboxed processing mode
- Enhanced input sanitization
- Security audit logging

## Contact

For security-related questions or concerns:
- Email: [fldx123456@163.com](mailto:fldx123456@163.com)
- GitHub Security Advisory: [Security Advisories](https://github.com/Dragon/VideoDub/security/advisories)

We appreciate responsible disclosure and will acknowledge your contribution in our release notes (unless you prefer to remain anonymous).