from przepisy import app
import os

app.secret_key = os.urandom(24)
port = int(os.environ.get("PORT"))
app.run(host="0.0.0.0", port=port)