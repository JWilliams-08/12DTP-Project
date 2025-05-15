from flask import Flask, render_template
import sqlite3


#create the flask app
app = Flask(__name__)


@app.route('/')
def home():
    # Connect to the SQLite database
    conn = sqlite3.connect('fill-ins.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT date FROM Draw')
    dates = cursor.fetchall()
    # Close the connection
    conn.close()
    return render_template('home.html', title='HOME', dates=dates)


if __name__ == '__main__':
    app.run(debug=True)