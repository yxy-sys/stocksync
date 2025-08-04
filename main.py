from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def index():
    return "Flask server is running."

@app.route("/ebay-notify", methods=["GET", "POST"])
def ebay_notify():
    verification_token = request.args.get("verification_token")
    expected_token = "tenko_verify_token_20250803_secure_key_9999"

    if verification_token == expected_token:
        print(f"✅ 验证成功！Token 为: {verification_token}")
        return "Verification success", 200
    else:
        print(f"❌ 验证失败！Token 为: {verification_token}")
        return "Verification failed", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
