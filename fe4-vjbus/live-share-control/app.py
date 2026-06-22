from flask import Flask, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def index():
    if os.path.exists("share_link.txt"):
        with open("share_link.txt", "r") as f:
            link = f.read().strip()
        return f"<h2>Current Live Share Link:</h2><a href='{link}' target='_blank'>{link}</a>"
    return "<p>No session link found.</p>"

@app.route('/restart')
def restart():
    # Call the script
    subprocess.call(["./restart_liveshare.sh"])
    return "<p>Live Share session restarted. <a href='/'>Click here</a> to get the new link.</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
