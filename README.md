# Sentinel AI Platform

**AI-Powered Multi-Camera Safety and Intelligence System**

⚠️ **ACADEMIC PROJECT ONLY** ⚠️

This system is designed exclusively for educational and research purposes as a final-year engineering project. It uses synthetic data and simulated scenarios only.

## ⚠️ Ethical Notice

- Uses ONLY synthetic/fake identities
- All "criminals" and "missing persons" are simulated characters
- NO real-world biometric data processing
- NOT for deployment on real public surveillance systems
- NOT a real law-enforcement tool

## Features

✅ Multi-camera video ingestion and processing
✅ Anonymous person detection and cross-camera tracking
✅ Synthetic watchlist management
✅ Masked/helmet face detection
✅ Face liveness and anti-spoofing
✅ Deepfake detection
✅ Behavioral anomaly detection
✅ Emotion-linked search
✅ Age progression for synthetic missing persons
✅ Offline-capable operation
✅ Federated learning demonstration
✅ Camera health monitoring
✅ Multi-modal alerts (visual, voice, email)
✅ Adaptive learning with bias correction
✅ Explainable AI (XAI)

## System Requirements

- **OS**: Ubuntu 20.04+ (tested on Jammy Jellyfish)
- **CPU**: AMD Ryzen 5 or equivalent
- **RAM**: 8GB minimum
- **Storage**: 50GB free space
- **Python**: 3.10 or higher
- **Node.js**: 16+ (for frontend)

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/sentinel-ai-platform.git
cd sentinel-ai-platform
```

### 2. Run Setup

```bash
chmod +x setup.sh
./setup.sh
```

### 3. Start Backend

```bash
chmod +x run_backend.sh
./run_backend.sh
```

### 4. Start Frontend (new terminal)

```bash
chmod +x run_frontend.sh
./run_frontend.sh
```

### 5. Access Application

Open browser: `http://localhost:3000`

**Default Credentials:**
- Admin: `admin` / `admin123`
- Operator: `operator` / `operator123`

## Project Structure

```
sentinel-ai-platform/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
├── data/             # Data storage
├── scripts/          # Utility scripts
├── tests/            # Test suite
└── docs/             # Documentation
```

## Documentation

- [Setup Guide](docs/SETUP.md)
- [API Reference](docs/API_REFERENCE.md)
- [ML Models](docs/ML_MODELS.md)
- [User Guide](docs/USER_GUIDE.md)

## Testing

```bash
# Backend tests
pytest tests/

# Integration tests
pytest tests/test_integration/
```

## Demo Workflow

```bash
python3 scripts/demo_workflow.py
```

## License

MIT License - Academic Use Only

## Disclaimer

This software is provided for educational purposes only. The developers are not responsible for any misuse of this software. This system must not be used for real-world surveillance without proper legal authorization and consent.
```

## 8. ETHICS_DISCLAIMER.md

```markdown
# Ethical Use Disclaimer

## Purpose

This project, **Sentinel AI Platform**, is developed strictly for:
- Academic research and education
- Final-year engineering project demonstration
- Understanding AI safety and privacy concepts
- Exploring federated learning and explainable AI

## What This System IS

✅ An educational demonstration using synthetic data
✅ A learning tool for computer vision and AI concepts
✅ A showcase of privacy-preserving techniques
✅ A simulation environment with fake identities

## What This System IS NOT

❌ A real-world surveillance system
❌ A law enforcement tool
❌ A mass surveillance platform
❌ A system for processing real biometric data without consent

## Synthetic Data Only

All data used in this system is synthetic:
- **Faces**: Generated or from synthetic datasets
- **Identities**: Completely fictional characters
- **Behaviors**: Simulated scenarios
- **Watchlists**: Fake "criminals" and "missing persons"

## Privacy Principles

1. **No Real Biometrics**: Never use real people's biometric data
2. **Consent Required**: Any real data requires explicit consent
3. **Transparency**: Always disclose when AI systems are in use
4. **Purpose Limitation**: Use only for stated academic purposes
5. **No Harm**: Ensure the system cannot cause harm to individuals

## Legal Compliance

Users must:
- Comply with local privacy laws (GDPR, CCPA, etc.)
- Obtain proper authorization before any real-world deployment
- Respect intellectual property rights
- Follow institutional ethics board guidelines

## Responsible Development

As developers and researchers, we commit to:
- Never deploying this on real public cameras without authorization
- Not using this to identify or track real individuals
- Clearly labeling all demonstrations as synthetic
- Educating users about ethical AI development

## If You Plan to Use This Code

⚠️ **Warning**: Before any adaptation for real-world use:

1. Consult with legal experts
2. Obtain ethics board approval
3. Ensure compliance with data protection laws
4. Implement proper consent mechanisms
5. Conduct bias and fairness audits
6. Establish accountability frameworks

## Reporting Misuse

If you become aware of this system being misused, please report it to:
- Your institution's ethics board
- Local data protection authorities
- The original developers

## Acknowledgment

By using this system, you acknowledge that:
- You have read and understand this disclaimer
- You will use this system ethically and legally
- You will not use this for surveillance without proper authorization
- You understand the limitations and synthetic nature of this project

---

**Remember**: With great power comes great responsibility. AI technology must be developed and deployed ethically, with respect for human rights, privacy, and dignity.
```