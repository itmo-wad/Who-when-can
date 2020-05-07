from flask import Flask


app = Flask(__name__)
app.secret_key = 'hello_world'
app.config.from_object(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/task3_database"

from main import views
