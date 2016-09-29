import json
import sqlite3
from xyhandler import xYHandler
import configparser

handle = xYHandler("auth.csv")

config = configparser.ConfigParser()
config.read('config.ini')
# Add your League_Key to the config.ini for this to work.
league_key = config.get('Yahoo', 'League_Key')
# Select how you want text output. Default is "Print". "Save" will append the text to a file named under saved_text
output_mode = "Save"
saved_text = "default_fantasy_stats.txt"

# Create the database
db_name = 'fantasy_stats.sqlite'
conn = sqlite3.connect(db_name)
cur = conn.cursor()
cur.executescript('''

    CREATE TABLE IF NOT EXISTS FanStats (
        week         INTEGER NOT NULL,
        teamname     TEXT NOT NULL,
        teamkey      TEXT NOT NULL,
        teamid       INTEGER NOT NULL,
        playername   TEXT NOT NULL,
        disp_position TEXT NOT NULL,
        position      TEXT NOT NULL,
        points        FLOAT NOT NULL,
        unique (week, playername)
    );
    ''')


def get_teams():
    """Get the list of teams from Yahoo's API."""
    # Get the team info
    team_uri = 'league/{}/teams'.format(league_key)
    d = handle.api_req(team_uri).json()
    # Get the number of teams in the league
    num_teams = d['fantasy_content']['league'][0]['num_teams']
    # Store team key, id, and name for each team in a list
    team_list = []
    for i in range(num_teams):
        #
        teamkey = d['fantasy_content']['league'][1]['teams'][str(i)]['team'][0][0]['team_key']
        teamid = d['fantasy_content']['league'][1]['teams'][str(i)]['team'][0][1]['team_id']
        teamname = d['fantasy_content']['league'][1]['teams'][str(i)]['team'][0][2]['name']
        team_list.append((teamkey, teamid, teamname))
    return team_list


def get_scores(team_list, week):
    """Gather scores and other data from each team's roster and add them to a database."""
    for team in team_list:
        # Get the roster data
        roster_uri = 'team/{}/roster;week={}/players/stats;type=week;week={}'.format(team[0], week, week)
        r = handle.api_req(roster_uri).json()
        # Get number of players on roster
        player_count = r['fantasy_content']['team'][1]['roster']['0']['players']['count']
        for n in range(player_count):
                # Player's full name
                full_name = r['fantasy_content']['team'][1]['roster']['0']['players'][str(n)]['player'][0][2]['name'][
                    'full']
                # Get the position the player is displayed as. (Their normal position)
                display_position = get_disp_position(r, n)
                # Get the position the player is taking on the roster. (Includes BN For Bench and W/R/T for Flex)
                position = r['fantasy_content']['team'][1]['roster']['0']['players'][str(n)]['player'][1]['selected_position'][1][
                    'position']
                # Get the points the player scored for the given week
                player_points = get_points(r, n)
                # Add all the stats to the database
                cur.execute('''INSERT OR REPLACE INTO FanStats
                    (week, teamname, teamkey, teamid, playername, disp_position, position, points) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?)''',
                            (week, team[0], team[1], team[2], full_name, display_position, position, player_points))
                conn.commit()


def get_disp_position(roster, n):
    """Get the displayed position of a player."""
    for i in range(14):
        for k in roster['fantasy_content']['team'][1]['roster']['0']['players'][str(n)]['player'][0][i]:
            if 'display_position' in k:
                return roster['fantasy_content']['team'][1]['roster']['0']['players'][str(n)]['player'][0][i][
                        'display_position']


def get_points(roster, n):
    """Get the points scored for a player."""
    for i in range(1, 4):
        for k in roster['fantasy_content']['team'][1]['roster']['0']['players'][str(n)]['player'][i]:
            if 'player_points' in k:
                return roster['fantasy_content']['team'][1]['roster']['0']['players'][str(n)]['player'][i][
                        'player_points']['total']


def get_info(week):
    """Print various statistics for the week, across all teams in the league."""
    # Get all roster positions and their counts
    positions = get_positions()
    # A list of positions to consider regarding benched player performance
    bpositions = ['QB', 'WR', 'RB', 'TE']
    # Header
    make_output('\nWEEK {} LEADERS\n'.format(week))
    # Top Guys
    make_output('{:-^30}\n'.format('Best Starters'))
    for pos in positions:
        templist = []
        for row in cur.execute('SELECT * FROM FanStats WHERE position = ? AND week = ? ORDER BY points DESC LIMIT ?', (pos[0], week, pos[1])):
            templist.append(row)
        if pos[1] == 1:
            make_output('The top {} was {} ({}) with {} points.\n'.format(
                pos[0], templist[0][4], templist[0][3], templist[0][7]))
        elif pos[1] == 2:
            make_output('The top 2 {}s were {} ({}) with {} points and {} ({}) with {} points.\n'.format(
                pos[0], templist[0][4], templist[0][3], templist[0][7], templist[1][4], templist[1][3], templist[1][7]))
        # Allow for more than 'top 2', but disregard benched players.
        elif pos[1] > 2 and pos[0] != 'BN':
            phrase = '{} ({}) with {} points, '
            full_phrase = ''
            for i in range(pos[1]-2):
                full_phrase += phrase.format(templist[i+1][4], templist[i+1][3], templist[i+1][7])
            make_output('The top {} {}s were {} ({}) with {} points, {}and {} ({}) with {} points.\n'.format(
                pos[1], pos[0], templist[0][4], templist[0][3], templist[0][7], full_phrase,
                templist[-1][4], templist[-1][3], templist[-1][7]))
    make_output('\n')
    # Benchwarmers
    make_output('{:-^30}\n'.format('Hottest Benchwarmers'))
    for pos in bpositions:
        templist = []
        for row in cur.execute('SELECT * FROM FanStats WHERE position = "BN" AND disp_position = ? AND week = ? ORDER BY points DESC LIMIT 2', (pos, week)):
            templist.append(row)
        make_output('The top two benchwarming {}s were {} ({}) with {} points and {} ({}) with {} points.\n'.format(
            pos, templist[0][4], templist[0][3], templist[0][7], templist[1][4], templist[1][3], templist[1][7]))
    make_output('\n')
    # Scrubs
    make_output('{:-^30}\n'.format('Worst Starters'))
    for pos in positions:
        templist = []
        for row in cur.execute('SELECT * FROM FanStats WHERE position = ? AND week = ? ORDER BY points ASC LIMIT 1',
                           (pos[0], week)):
            templist.append(row)
        make_output('The worst {} was {} ({}) with {} points.\n'.format(pos[0], templist[0][4], templist[0][3], templist[0][7]))

    conn.commit()


def get_positions():
    """Get the roster positions for a given league as a list of tuples."""
    # Get the roster settings
    roster_settings_uri = 'league/{}/settings'.format(league_key)
    r = handle.api_req(roster_settings_uri).json()
    # Get the roster positions data
    rost_pos = r['fantasy_content']['league'][1]['settings'][0]['roster_positions']
    # Return the positions and their counts as a list of tuples.
    poslist = []
    for pos in rost_pos:
        poslist.append((pos['roster_position']['position'], pos['roster_position']['count']))
    return poslist


def make_output(s):
    if output_mode == "Print":
        print(s)
    elif output_mode == "Save":
        with open(saved_text, 'a') as openfile:
            openfile.write(s + '\n')


def jsondump(filename, querystring):
    """Save json as txt file, for testing purposes."""
    with open('{}.txt'.format(filename), 'w') as outfile:
        json.dump(handle.api_req(querystring).json(), outfile, sort_keys=True, indent=4, ensure_ascii=False)


def rostest(filename):
    """Read json from saved files, for testing purposes."""
    with open('{}.txt'.format(filename), 'r') as openfile:
        return json.load(openfile)


def run(week_list):
    """Input is a list of ints."""
    team_list = get_teams()
    for week in week_list:
        get_scores(team_list, week)
        get_info(week)


while True:
    try:
        week_list = [int(x) for x in input(
            "Please enter the week(s) you would like to obtain data for. Separate numbers with a space.").split()]
        break
    except ValueError:
        print("Invalid input. Example input: 1 2 10")
        continue

run(week_list)

