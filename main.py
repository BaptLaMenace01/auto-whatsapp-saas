from flask import Flask, request, jsonify
from worker import launch_campaign

app = Flask(__name__)

@app.route("/api/send-whatsapp", methods=["POST"])
def send_whatsapp():
    try:
        data = request.get_json()
        campaign_id = data["campaign_id"]
        user_id = data["user_id"]
        contacts = data["contacts"]
        message = data["message"]
        options = data.get("options", {})

        result = launch_campaign(campaign_id, contacts, message, options)

        return jsonify({
            "success": True,
            "campaign_id": campaign_id,
            "results": result
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
