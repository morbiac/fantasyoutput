# **Synopsis**

This small project allows you to get a readout of statistics for your Yahoo! Fantasy Football league. It will give you a list of the leaders for the week at various positions, missed opportunities such as benchwarmers who performed well, and the equally-demoralizing list of starters who performed the worst at each position.

# **Usage**

First, rename config_example.ini to config.ini and open it in your preferred text editor. Register an app on https://developer.yahoo.com/apps/create/ making sure to check the API Permissions box for reading Fantasy Sports. You will be given a consumer key and secret key that can be copied and pasted into the config.ini. You will also need to add your **league_key**, which is made up of a game key and league ID. Search your league settings or look in the Yahoo! url for your league to find the league ID. If your league ID is 123456, your league_key for the current season would be **nfl.l.123456**. You can also get data from previous seasons by using the correct numerical game key instead of "nfl". A non-updated list of some years can be found at https://developer.yahoo.com/fantasysports/guide/game-resource.html

output_mode is set to "Save" by default, and will append the output to a text file called default_fantasy_stats.txt by default. This can be changed to "Print" to print text in the console.

To use, simply run fantasyoutput.py. It will ask you for the weeks you want data for and, hopefully, will give you that data without breaking. You will also be prompted to log into your Yahoo! account and allow access to your league data.

# **Sample Output**

WEEK 3 LEADERS


--------Best Starters---------

The top QB was Drew Brees (Gronky Kong) with 26.94 points.

The top 2 WRs were T.Y. Hilton (The Walking Dez) with 23.4 points and T.Y. Hilton (The Walking Dez) with 23.4 points.

The top 2 RBs were Devonta Freeman (Keenan and Bell) with 26.7 points and Devonta Freeman (Keenan and Bell) with 26.7 points.

The top TE was Coby Fleener (Gronky Kong) with 16.9 points.

The top W/R/T was Marvin Jones Jr. (Jamaal Rats) with 32.5 points.

The top K was Justin Tucker (Living on a Prater) with 17.0 points.

The top DEF was Kansas City (Armed Rodgery) with 35.0 points.


-----Hottest Benchwarmers-----

The top two benchwarming QBs were Matthew Stafford (Living on a Prater) with 27.5 points and Jameis Winston (Full Hauschka) with 26.5 points.

The top two benchwarming WRs were DeSean Jackson (The Tolbert Report) with 15.6 points and Sterling Shepard (The Walking Dez) with 13.3 points.

The top two benchwarming RBs were Tevin Coleman (Gronky Kong) with 26.9 points and Carlos Hyde (RussellMania) with 24.5 points.

The top two benchwarming TEs were Zach Miller (Gronky Kong) with 19.8 points and Jimmy Graham (The Tolbert Report) with 14.0 points.



--------Worst Starters--------

The worst QB was Ryan Fitzpatrick (Keenan and Bell) with 3.72 points.

The worst WR was Kelvin Benjamin (Keenan and Bell) with 0.0 points.

The worst RB was Ryan Mathews (Gronky Kong) with -0.5 points.

The worst TE was Vance McDonald (Luck Ness Monster) with 0.4 points.

The worst W/R/T was Rashad Jennings (Gronky Kong) with 0.0 points.

The worst K was Nick Novak (Jamaal Rats) with 0.0 points.

The worst DEF was Pittsburgh (Full Hauschka) with -1.0 points.

The worst BN was Devin Funchess (Jamaal Rats) with 0.0 points.

# **Motivation**

This is my first github project, so expect to run into bugs. I will do my best to keep this updated with fixes for common problems.