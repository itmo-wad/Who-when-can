from flask import Flask

app = Flask(__name__)
app.secret_key = 'jkdsgfh87w45tu834jeqT@#$5234#$2#R567j56967u45679084j76$^&%3456'
app.config.from_object(__name__)

from main import views
