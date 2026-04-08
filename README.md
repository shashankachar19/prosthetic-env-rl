---
title: Prosthetic Env RL
emoji: 🦾
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# APMS: AI-Powered Prosthetic Management System

[![OpenEnv Compliant](https://img.shields.io/badge/OpenEnv-Compliant-brightgreen.svg)]()
[![Hackathon](https://img.shields.io/badge/Meta_PyTorch_x_Scaler-Hackathon-blue.svg)]()
[![Phase](https://img.shields.io/badge/Deployment-HuggingFace-orange.svg)]()

A robust, multi-task Reinforcement Learning (RL) environment built on the Meta OpenEnv specification. APMS is designed to train intelligent agents for real-world prosthetic limb calibration, teaching them to apply precise grip forces dynamically based on varying situational intents.

---

## The Problem & Vision
Modern physical prosthetics often struggle with intent-based force modulation. A user needs a different grip strength to hold a fragile egg than they do to firmly shake a hand. 

The APMS Environment bridges this gap by providing an RL training ground where AI agents learn to modulate grip force (ranging from 0 to 10) while optimizing for efficiency and minimizing battery/time penalties. 

## Environment Tasks
To ensure comprehensive agent training, this environment randomly instantiates one of 5 distinct real-world tasks per episode. Agents receive a normalized reward (1.0) for task completion and a 0.0 reward for intermediate steps, strictly adhering to standard RL validation ranges.

1. Precision Grip: Match a dynamic, randomized mid-level force (Target: 3-7).
2. Power Grip: Apply maximum, sustained force (Target: >= 9).
3. Relaxation: Transition from a tense state to a completely relaxed state (Target: <= 1).
4. Delicate Pinch: Apply minimal, highly precise force for fragile objects (Target: Exactly 2).
5. Firm Handshake: Apply a strong, steady hold without exerting crushing maximum power (Target: Exactly 8).

## Technical Architecture
This project is fully compliant with Phase 1 and Phase 2 deep validation requirements.

* Framework: Meta openenv-core
* API / Backend: FastAPI (HTTP & WebSocket endpoints for persistent sessions)
* LLM Inference: OpenAI Client integration (inference.py)
* Deployment: Containerized via Docker and deployed serverless on Hugging Face Spaces (Port 7860).

## Repository Structure
```text
prosthetic_env/
├── Dockerfile                  # HF Space deployment instructions
├── inference.py                # Agentic evaluation script (Phase 2)
├── models.py                   # Pydantic schemas for Actions/Observations
├── openenv.yaml                # Environment metadata and spec
├── requirements.txt            # Root dependencies for automated graders
└── server/
    ├── app.py                  # FastAPI server configuration
    └── prosthetic_env_environment.py # Core environment and step() logic