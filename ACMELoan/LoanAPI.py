from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["acme_loan_app"]
applications = db["applications"]

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/apply', methods=['POST'])
def apply():
    """ ✅ Application submission with name, address, and zipcode ✅ """
    data = request.json
    name = data.get('name')
    address = data.get('address')
    zipcode = data.get('zipcode')

    if not name or not address or not zipcode:
        return jsonify({"error": "Name, address, and zipcode are required"}), 400

    application = {
        "name": name,
        "address": address,
        "zipcode": zipcode,
        "status": "received",
        "notes": []
    }

    result = applications.insert_one(application)
    return jsonify({"application_id": str(result.inserted_id), "message": "Application received"})

@app.route('/status/<application_id>', methods=['GET'])
def check_status(application_id):
    application = applications.find_one({"_id": ObjectId(application_id)})

    if not application:
        return jsonify({"status": "not found"}), 404

    return jsonify({
        "status": application["status"],
        "notes": application.get("notes", []),
        "rejection_reason": application.get("rejection_reason", "No reason provided")
    })

@app.route('/status/<application_id>', methods=['PUT'])
def change_status(application_id):
    """ ✅ Update application status ✅ """
    data = request.json
    new_status = data.get('status')

    if new_status not in ["received", "processing", "accepted", "rejected"]:
        return jsonify({"error": "Invalid status"}), 400

    result = applications.update_one(
        {"_id": ObjectId(application_id)},
        {"$set": {"status": new_status}}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Application not found"}), 404

    return jsonify({"message": "Status updated successfully"})

@app.route('/subphase/<application_id>', methods=['POST'])
def add_subphase_note(application_id):
    """ ✅ Add subphase task completion notes ✅ """
    data = request.json
    phase = data.get('phase')
    task = data.get('task')
    message = data.get('message')

    if not phase or not task or not message:
        return jsonify({"error": "Phase, task, and message are required"}), 400

    result = applications.update_one(
        {"_id": ObjectId(application_id)},
        {"$push": {"notes": {"phase": phase, "task": task, "message": message, "timestamp": datetime.utcnow()}}}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Application not found"}), 404

    return jsonify({"message": "Subphase note added successfully"})

@app.route('/notes/<application_id>', methods=['POST'])
def add_loan_note(application_id):
    """ ✅ Add loan terms notes for accepted applications ✅ """
    data = request.json
    message = data.get('message')

    result = applications.update_one(
        {"_id": ObjectId(application_id), "status": "accepted"},
        {"$push": {"notes": {"phase": "loan terms", "message": message, "timestamp": datetime.utcnow()}}}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Application not found or not accepted"}), 404

    return jsonify({"message": "Loan note added successfully"})

@app.route('/reject/<application_id>', methods=['PUT'])
def reject_application(application_id):
    """ ✅ Reject application with reason ✅ """
    data = request.json
    reason = data.get('reason')

    result = applications.update_one(
        {"_id": ObjectId(application_id)},
        {"$set": {"status": "rejected", "rejection_reason": reason}}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Application not found"}), 404

    return jsonify({"message": "Application rejected", "reason": reason})

if __name__ == '__main__':
    app.run(debug=True)
