from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import anthropic

app = Flask(__name__)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

VENUE_CONTEXT = """
You are the AI Operations Assistant for CrowdFlow, an enterprise stadium management system.
Total Capacity: 40,000. Current Attendance: 37,856.
Gates: Gate A (Clear), Gate B (Clear), Gate C (Clear), Gate D (Medium), Gate E (Critical - Scanner Failure), Gate F (Clear).
Density: North Stand (92% - Critical), Main Concourse (88% - High), East Wing (74%), Food Court (68%).
Food: Burger House (10m wait), Green Bowl (2m wait), Combo Corner (5m wait - 20% discount active).
Provide concise, authoritative, and actionable responses. Prioritize safety and crowd dispersion.
"""

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    recommendation = None
    if request.method == 'POST':
        seat_section = request.form.get('seat_section')
        density = request.form.get('density')
        need = request.form.get('need')
        
        # Example hardcoded logic
        recs = []
        if density == "High":
            recs.append("Avoid Main Concourse.")
        if need == "Food":
            recs.append("Route via secondary external rings to Green Bowl per optimal queue threshold.")
        elif need == "Exit":
            recs.append("Redirect to Gate F (optimal throughput).")
        
        recommendation = " ".join(recs) if recs else f"Proceed to {need} via lowest density adjacent corridor."
        
    return render_template('dashboard.html', recommendation=recommendation, seat_section=request.form.get('seat_section', ''))

@app.route('/stadium-map')
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
    messages = data.get('messages', [])
    
    formatted_messages = []
    for msg in messages:
        formatted_messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
        
    try:
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=600,
            system=VENUE_CONTEXT,
            messages=formatted_messages
        )
        return jsonify({"reply": response.content[0].text})
    except Exception as e:
        return jsonify({'reply': 'Secure channel initializing. Operations module standing by.'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
