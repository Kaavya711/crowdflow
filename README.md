# CrowdFlow – AI Stadium Operations Assistant

## Chosen Vertical
Smart Venue & Stadium Operations Management

## Overview
CrowdFlow is an AI-powered stadium operations assistant designed to monitor live crowd density, gate congestion, and food queue metrics to provide real-time recommendations.

The assistant helps improve:
- Crowd safety
- Operational efficiency
- Food stall load balancing
- Gate traffic optimization

## Google Services Used
- Google Gemini API (Generative AI)
- Dynamic AI reasoning based on live venue telemetry context

## How It Works
The system:
1. Injects live venue telemetry into a system context.
2. Accepts user queries from the dashboard interface.
3. Sends structured conversation context to Gemini.
4. Generates actionable, concise operational recommendations.

Example:
- Advises crowd redirection if density exceeds threshold.
- Suggests promoting low-wait food stalls.
- Recommends optimal exit gates.

## Assumptions
- Live telemetry data is simulated.
- Venue capacity and density metrics are pre-configured.
- AI prioritizes safety and crowd dispersion.

## Tech Stack
- Python
- Flask
- Google Gemini API
- HTML/CSS

## Security Considerations
- API key stored securely via environment variables
- No sensitive data exposed in repository

## How to Run
1. Install dependencies:
   pip install -r requirements.txt

2. Set environment variable:
   set GEMINI_API_KEY=your_api_key

3. Run:
   python app.py

4. Open:
   http://127.0.0.1:5000
