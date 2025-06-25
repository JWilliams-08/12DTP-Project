from flask import Flask, render_template, jsonify, request, redirect 
import sqlite3


#create the flask app
app = Flask(__name__)

# Function to get a database connection
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
    # get players from a selected team
    conn = get_db_connection()
    players = conn.execute('''
        SELECT player_name
        FROM PlayerTeam
        WHERE team_name = ?
    ''', (team_name,)).fetchall()
    conn.close()
    return jsonify({'players': [p[0] for p in players]})


@app.route('/submit_request', methods=['POST'])

def submit_request():
    #submit a fill-in request
    date = request.form['date']
    team = request.form['team']
    player = request.form['player']
    conn = get_db_connection()
    conn.execute('''
                 INSERT INTO FillInRequest (date, team_name, player_name)
                 VALUES (?, ?, ?)
''' , (date, team, player))
    conn.commit()
    conn.close()

    #redirect user to results page
    return redirect('/results', team=team, date=date, player=player)

@app.route('/results')
def results():
    conn = get_db_connection()
    # get fill-in requests 

    return render_template('results.html', title='RESULTS')
if __name__ == '__main__':
    app.run(debug=True)