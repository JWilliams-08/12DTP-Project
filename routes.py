from flask import Flask, render_template, jsonify, request, redirect, url_for
import sqlite3


#Create the flask app
app = Flask(__name__)

#Functions

def get_db_connection():
    #Connect to the SQLite database
    conn = sqlite3.connect('fill-ins.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_valid_fillins(team, date, player):
    #get all valid fill-ins
    grade_order = [10,12,14,18]
    conn = get_db_connection()

    #get information about the team
    team = conn.execute('SELECT * FROM Team WHERE name = ?', (team,)).fetchone()
    if not team:
        conn.close()
        return []
    grade = int(team['grade'])
    div = int(team['division'])
    day = team['day']
    time = team['time']
    print(grade, div, day, time)

    #workout the next youngest age grade
    try:
        target_index = grade_order.index(grade)
    except ValueError:
        conn.close()
        return []
    next_younger_grade = grade_order[target_index - 1] if target_index > 0 else None

    print(next_younger_grade)
    #Query eleible teams:
    if next_younger_grade: #if there is a younger age group, query both that and lower divisions of same grade
        eligible_teams = conn.execute('''
            SELECT * FROM Team
            WHERE (grade = ? AND division < ?)
            OR (grade = ?)                     
        ''',(str(grade), (div), str(next_younger_grade))).fetchall() 

    else: #if no younger age groups, query lower divisions of same grade
        eligible_teams = conn.execute('''
            SELECT * FROM Team
            WHERE grade = ? AND division < ?
        ''', (str(grade), str(div))).fetchall()

    #check if there are any eligible teams and if not return empty list
    if not eligible_teams:
        conn.close()
        return []
    
    #filter out any teams playing at the same time unless players > 4
    valid_team_names = []
    for team in eligible_teams:
        if team['day'] != day or team['time'] != time:
            valid_team_names.append(team['name'])
        else:
            player_count = conn.execute('SELECT COUNT(*) FROM PlayerTeam WHERE team_name = ?', (team['name'],)).fetchone()[0]
            if player_count > 4:
                valid_team_names.append(team['name'])
    
    #if not teams are valid, return empty list
    if not valid_team_names:
        conn.close()
        return []
    print(valid_team_names)



@app.route('/')
def home():
    #Connect to the SQLite database
    conn = get_db_connection()
    dates = conn.execute('SELECT DISTINCT date FROM Draw').fetchall()
    teams = conn.execute('SELECT name FROM Team').fetchall()
    conn.close()
    return render_template('home.html', title='HOME', dates=dates, teams=teams)


@app.route('/get_players/<team_name>')
def get_players(team_name):
    #get players from a selected team
    conn = get_db_connection()
    players = conn.execute('''
        SELECT player_name
        FROM PlayerTeam
        WHERE team_name = ?
    ''', (team_name,)).fetchall()
    conn.close()
    return jsonify({'players': [p[0] for p in players]})


@app.route('/results', methods=['POST'])
def results():
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

    #call function to get valid fill-ins
    valid_players = get_valid_fillins(team, date, player)
    # get fill-in requests 

    return render_template('results.html', date=date, team=team, valid_players=valid_players)
if __name__ == '__main__':
    app.run(debug=True)