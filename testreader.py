import json
import sqlite3
from xyhandler import xYHandler
import configparser

handle = xYHandler("auth.csv")

config = configparser.ConfigParser()
config.read('config.ini')
# Add your League_Key to the config.ini for this to work.
league_key = config.get('Yahoo', 'League_Key')


def get_teams():
    """Get the list of teams from Yahoo's API."""
    # Get the team info
    team_uri = 'league/{}/teams'.format(league_key)
    d = handle.api_req(team_uri).json()
    # Get the number of teams in the league
    num_teams = d['fantasy_content']['league'][0]['num_teams']
    # Store team key, id, and name for each team in a list
    teamlist = []
    for i in range(num_teams):
        #
        teamkey = d['fantasy_content']['league'][1]['teams'][str(i)]['team'][0][0]['team_key']
        teamid = d['fantasy_content']['league'][1]['teams'][str(i)]['team'][0][1]['team_id']
        teamname = d['fantasy_content']['league'][1]['teams'][str(i)]['team'][0][2]['name']
        teamlist.append((teamkey, teamid, teamname))
    return teamlist


def get_scores(teamlist, week):
    """Gather scores and other data from each team's roster and add them to a database"""
    # Create the database
    conn = sqlite3.connect('fantasy_stats.sqlite'.format(week))
    cur = conn.cursor()
    cur.executescript('''
        DROP TABLE IF EXISTS FanStats;

        CREATE TABLE FanStats (
            week         INTEGER NOT NULL,
            teamname     TEXT NOT NULL,
            teamkey      TEXT NOT NULL,
            teamid       INTEGER NOT NULL,
            playername   TEXT NOT NULL,
            disp_position TEXT NOT NULL,
            position      TEXT NOT NULL,
            points        FLOAT NOT NULL
        );
        ''')

    for team in teamlist:
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
                #print('{} -- {} -- {} -- {}'.format(full_name, display_position, position, player_points))
                # Add all the stats to the database
                cur.execute('''INSERT INTO FanStats
                    (teamname, teamkey, teamid, playername, disp_position, position, points) VALUES ( ?, ?, ?, ?, ?, ?, ?)''',
                            (team[0], team[1], team[2], full_name, display_position, position, player_points))
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
    conn = sqlite3.connect('fantasyweek{}.sqlite'.format(week))
    c = conn.cursor()
    bpositions = ['QB', 'WR', 'RB', 'TE']
    print('WEEK {} LEADERS'.format(week))
    # Benchwarmers
    for pos in bpositions:
        templist = []
        for row in c.execute('SELECT * FROM FanStats WHERE position = "BN" AND disp_position = ? ORDER BY points DESC LIMIT 2',(pos,)):
            templist.append(row)
        print('The top two benchwarming {}s were {} ({}) with {} points and {} ({}) with {} points.'.format(
            pos, templist[0][3], templist[0][2], templist[0][6], templist[1][3], templist[1][2], templist[1][6]))
    # Top Guys
    positions = get_positions()
    for pos in positions:
        templist = []
        for row in c.execute('SELECT * FROM FanStats WHERE position = ? ORDER BY points DESC LIMIT ?', (pos[0], pos[1])):
            templist.append(row)
        if pos[1] == 1:
            print('The top {} was {} ({}) with {} points.'.format(
                pos[0], templist[0][3], templist[0][2], templist[0][6]))
        elif pos[1] == 2:
            print('The top 2 {}s were {} ({}) with {} points and {} ({}) with {} points.'.format(
                pos[0], templist[0][3], templist[0][2], templist[0][6], templist[1][3], templist[1][2], templist[1][6]))
        elif pos[1] > 2:
            phrase = '{} ({}) with {} points, '
            full_phrase = ''
            for i in range(pos[1]-2):
                full_phrase += phrase.format(templist[i+1][3], templist[i+1][2], templist[i+1][6])
            print('The top {} {}s were {} ({}) with {} points, {}and {} ({}) with {} points.'.format(
                pos[1], pos[0], templist[0][3], templist[0][2], templist[0][6], full_phrase,
                templist[-1][3], templist[-1][2], templist[-1][6]))

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


def jsondump(filename, querystring):
    """Save json as txt file, for testing purposes."""
    with open('{}.txt'.format(filename), 'w') as outfile:
        json.dump(handle.api_req(querystring).json(), outfile, sort_keys=True, indent=4, ensure_ascii=False)


def rostest(filename):
    """Read json from saved files, for testing purposes."""
    with open('{}.txt'.format(filename), 'r') as openfile:
        return json.load(openfile)

teamlist = get_teams()
get_scores(teamlist, 3)
get_info(3)


