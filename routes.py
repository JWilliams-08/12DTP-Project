from flask import Flask, render_template, jsonify, request
import sqlite3


# Create the flask app
app = Flask(__name__)


def get_db_connection():
    # Connect to the SQLite database
    conn = sqlite3.connect('fill-ins.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_valid_fillins(team_name, date, player):
    # get all valid fill-ins
    GRADE_ORDER = [10, 12, 14, 18]
    conn = get_db_connection()

    # get information about the team
    team = conn.execute('SELECT * FROM Team WHERE name = ?',
                        (team_name,)).fetchone()
    if not team:
        conn.close()
        return []

    grade = int(team['grade'])
    div = int(team['division'])
    day = team['day']
    time = team['time']
    gender = team['gender']

    # workout the next youngest age grade
    try:
        target_index = GRADE_ORDER.index(grade)
    except ValueError:
        conn.close()
        return []

    younger_grade = GRADE_ORDER[target_index - 1] if target_index > 0 else None

    # Query eligible teams:
    if younger_grade:
        # Query both lower divisions and all divisions of next younger grade
        eligible_teams = conn.execute('''
            SELECT * FROM Team
            WHERE (grade = ? AND division < ? AND gender = ?)
            OR (grade = ? AND gender = ?)
        ''', (str(grade),
              (div),
              gender,
              str(younger_grade),
              gender)).fetchall()

    else:
        # query only lower divisions of same grade
        eligible_teams = conn.execute('''
            SELECT * FROM Team
            WHERE grade = ? AND division < ? AND gender = ?
        ''', (str(grade), str(div), gender)).fetchall()

    # check if there are any eligible teams and if not return empty list
    if not eligible_teams:
        conn.close()
        return []

    # filter out any teams playing at the same time unless players > 4
    valid_team_names = []
    for team in eligible_teams:
        if team['day'] != day or team['time'] != time:
            valid_team_names.append(team['name'])
        else:
            player_count = conn.execute('''
                SELECT COUNT(*)
                FROM PlayerTeam
                WHERE team_name = ?
                ''', (team['name'],)).fetchone()[0]
            if player_count > 4:
                valid_team_names.append(team['name'])

    # if not teams are valid, return empty list
    if not valid_team_names:
        conn.close()
        return []

    # get players from valid teams
    placeholders = ','.join('?' for _ in valid_team_names)
    valid_players = conn.execute(f'''
        SELECT player_name, team_name
        FROM PlayerTeam
        WHERE team_name IN ({placeholders})
    ''', valid_team_names).fetchall()
    conn.close()
    return valid_players


@app.route('/')
# homepage
def home():
    # Connect to the SQLite database
    conn = get_db_connection()
    dates = conn.execute('SELECT DISTINCT date FROM Draw').fetchall()
    teams = conn.execute('SELECT name FROM Team').fetchall()
    conn.close()
    return render_template('home.html',
                           title='Home',
                           dates=dates,
                           teams=teams)


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


@app.route('/results', methods=['POST'])
def results():
    date = request.form['date']
    team = request.form['team']
    player = request.form['player']
    conn = get_db_connection()
    conn.execute('''
                 INSERT INTO FillInRequest (date, team_name, player_name)
                 VALUES (?, ?, ?)
''', (date, team, player))
    conn.commit()
    conn.close()

    # Get valid fill-ins
    valid_players = get_valid_fillins(team, date, player)

    # Group players by team
    teams_dict = {}
    for player in valid_players:
        team_name = player['team_name']
        player_name = player['player_name']
        if team_name not in teams_dict:
            teams_dict[team_name] = []
        teams_dict[team_name].append(player_name)
    print(teams_dict)

    conn = get_db_connection()
    manager_details = {}
    for team_name in teams_dict.keys():
        details = conn.execute('''
                 SELECT DISTINCT team_manager,
                 team_manager_cell
                 FROM Team WHERE name = ?;
                 ''', (team_name,)).fetchone()
        
        manager_details[team_name] = {
            'team_manager': details['team_manager'],
            'team_manager_cell': details['team_manager_cell']
        }
    conn.close()
    print(manager_details)
    return render_template('results.html',
                           title='Results',
                           date=date,
                           team=team,
                           teams_dict=teams_dict,
                           manager_details=manager_details
                           )


@app.errorhandler(404)
# 404 Not Found
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
# 500 Internal Server Error
def internal_error(error):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)

# For mobile testing - allows connections from any device on your network
#if __name__ == '__main__':
#    app.run(
#        debug=True,
#        host='0.0.0.0',
#        port=5000,
#        threaded=True
#    )
