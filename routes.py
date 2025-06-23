from flask import Flask, render_template, jsonify
import sqlite3


#create the flask app
app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('fill-ins.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    # Connect to the SQLite database
    conn = get_db_connection()
    dates = conn.execute('SELECT DISTINCT date FROM Draw').fetchall()
    teams = conn.execute('SELECT name FROM Team').fetchall()
    conn.close()
    return render_template('home.html', title='HOME', dates=dates, teams=teams)

@app.route('/get_players/<team_name>')
def get_players(team_name):
    conn = get_db_connection()
    players = conn.execute('''
        SELECT player_name
        FROM PlayerTeam
        WHERE team_name = ?
    ''', (team_name,)).fetchall()
    conn.close()
    return jsonify({'players': [p[0] for p in players]})

@app.route('/results')
def results():

    return render_template('results.html', title='RESULTS')
if __name__ == '__main__':
    app.run(debug=True)