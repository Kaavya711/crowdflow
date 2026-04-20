import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# Configure Gemini
api_key = "AIzaSyA526-tYs_3xmBhWQyRH_zF3zwWblEwglc"
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

VENUE_CONTEXT = """
You are the AI Operations Assistant for CrowdFlow, an enterprise stadium management system.
Total Capacity: 40,000. Current Attendance: 37,856.
Gates: Gate A (Clear), Gate B (Clear), Gate C (Clear), Gate D (Medium), Gate E (Critical - Scanner Failure), Gate F (Clear).
Density: North Stand (92% - Critical), Main Concourse (88% - High), East Wing (74%), Food Court (68%).
Food: Burger House (10m wait), Green Bowl (2m wait), Combo Corner (5m wait - 20% discount active).
Provide concise, authoritative, and actionable responses. Prioritize safety and crowd dispersion.
"""

@app.route('/')
def dashboard():
    return render_template('dashboard.html', recommendation=None, seat_section=None)

@app.route('/dashboard', methods=['POST'])
def dashboard_post():
    seat_section = request.form.get('seat_section')
    density = request.form.get('density')
    need = request.form.get('need')
    prompt = f"""
    {VENUE_CONTEXT}
    A visitor is at: {seat_section}
    Current crowd density: {density}
    They need: {need}
    Give a specific routing recommendation in 2-3 sentences.
    """
    try:
        response = model.generate_content(prompt)
        recommendation = response.text
    except Exception as e:
        recommendation = f"Unable to compute route: {str(e)}"
    return render_template('dashboard.html', recommendation=recommendation, seat_section=seat_section)

@app.route('/map')
def stadium_map():
    return render_template('map.html')

@app.route('/gates')
def gates():
    return render_template('gates.html')

@app.route('/food')
def food():
    return render_template('food.html')

@app.route('/assistant')
def assistant():
    return render_template('ai.html')

@app.route('/alerts')
def alerts():
    return render_template('alerts.html')

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.json
    if not data:
        return jsonify({"reply": "Invalid request."}), 400

    messages = data.get('messages', [])
    conversation = VENUE_CONTEXT + "\n\n"

    for msg in messages:
        role = msg.get('role', '').upper()
        content = msg.get('content', '')
        conversation += f"{role}: {content}\n"

    try:
        response = model.generate_content(conversation)
        reply = response.text
    except Exception as e:
        reply = f"Error generating response: {str(e)}"

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True)
