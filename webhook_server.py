from flask import Flask, request

app = Flask(__name__)

# eBay 会发送的验证 token
VERIFICATION_TOKEN = "ebay_webhook_verify"

@app.route("/webhook", methods=["GET"])
def verify_token():
    challenge = request.args.get("challenge_code")
    token = request.args.get("verification_token")
    endpoint = request.args.get("endpoint")

    if token == VERIFICATION_TOKEN:
        return {
            "challengeResponse": challenge
        }, 200
    else:
        return "Invalid token", 400

@app.route("/webhook", methods=["POST"])
def handle_notification():
    print("✅ 接收到 eBay 通知：", request.json)
    return "", 200

if __name__ == "__main__":
    app.run()

