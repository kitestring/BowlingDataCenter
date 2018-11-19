from jsonAPI import JSON_Tools  # @unresolvedimport
from SQLiteAPI import BowlingDB  # @unresolvedimport

import sys
import pandas as pd
from subprocess import check_output
import matplotlib.pyplot as plt
import numpy as np





default_fig_size = (10,4)
default_fig_dpi = 300

def speciality_plot_SeriesScratch():
     
    # Query DB based upon the user selections, create plot, then update canvas with new plot
    print('speciality_plot_SeriesScratch')
    print('bowlers_selections - ', bowlers_selections)
    
def speciality_plot_CumulativeMatchPoints():
     
    # Query DB based upon the user selections, create plot, then update canvas with new plot
    print('speciality_plot_CumulativeMatchPoints')
    print('bowlers_selections - ', bowlers_selections)
    
def speciality_plot_GameComparison():
     
    # Query DB based upon the user selections, create plot, then update canvas with new plot
    print('speciality_plot_GameComparison')
    print('bowlers_selections - ', bowlers_selections)
    
def speciality_plot_TeamHandycapTotal():
    
    # Verify that on the bowler list box that a team(s) selection has been
    # made not an individual bowler(s) selection
    if individualbowlerselection == True:
        print('Invalid selection: Must make a team selection and not an individual bowler selection.\n\n\n\n')
        return None
        
    # Query DB based upon the user selections, create plot, then update canvas with new plot
    bowling_df = bowling_db.teamHandicap_query(bowlers_selections, season_leagues_selections)
    
    # If team 22 is included, remove week 1 because we only had 3 of 5 bowlers
    if '22' in bowlers_selections:
        bowling_df = bowling_df[bowling_df['Days'] != 0]

    print(bowling_df)
    
def speciality_plot_SummaryTable():
     
    # Query DB based upon the user selections, create plot, then update canvas with new plot
    print('speciality_plot_SummaryTable')
    print('bowlers_selections - ', bowlers_selections)
    
    
if __name__ == '__main__':
    
    # Initialize passed arguments & load JSON Data
    # Get parameters for each plot in the report, formatted in JSON data
    jsonfilepath = sys.argv[1]
    pdffilepath = sys.argv[2]
    dbfilepath = sys.argv[3]
    bowling_db = BowlingDB(dbfilepath)
    bowlinginstancedata = JSON_Tools().Load_Data(jsonfilepath)
    plot_dict = bowlinginstancedata['plots']
    
    speciality_plots_method_dict = {'Cumulative Match Points': speciality_plot_CumulativeMatchPoints,
                                             'Game Comparison': speciality_plot_GameComparison,
                                             'Team Handicap Total': speciality_plot_TeamHandycapTotal,
                                             'Summary Table': speciality_plot_SummaryTable,
                                             "Series Scratch": speciality_plot_SeriesScratch}
    
    
    fig = plt.figure(figsize=(default_fig_size), dpi=default_fig_dpi)
    num_plots = len(plot_dict['KeyOrder'])
    ax = []
    
    for p, plot_name in enumerate(plot_dict['KeyOrder']):
        # Parse plot parameters
        season_leagues_selections = plot_dict[plot_name]['season_leagues_selections']
        bowlers_selections = plot_dict[plot_name]['bowlers_selections']
        individualbowlerselection = plot_dict[plot_name]['individualbowlerselection'] 
        primary_yaxis_fields = plot_dict[plot_name]['primary_yaxis_fields']
        sp = plot_dict[plot_name]['sp']
        
        # add subplot
        ax.append(fig.add_subplot(num_plots, 1, 1 + p))
        ax[p].set_prop_cycle('color',plt.cm.Dark2(np.linspace(0,1,9))) #@UndefinedVariable
        
        print('plot_name - ', plot_name)
    
        # Decision tree
        # If --> speciality plots
        # elif --> invalid selections
        # else --> custom plots
        if sp != 'None' and season_leagues_selections != ['None'] and bowlers_selections != ['None']:
            print('Speciality Who-Hoo')
            speciality_plots_method_dict[sp]()
            
        elif season_leagues_selections == ['None'] or bowlers_selections == ['None'] or primary_yaxis_fields == ['None']:
            print('Invalid selection: Must select at least a single season league, bowler, and primary y-axis field to create a plot.\n\n\n\n')
        
        else:
            print('ok normal custom plot')
        
#         print('plot_name - ', plot_name)
#         print('season_leagues_selections - ', season_leagues_selections)
#         print('bowlers_selections - ', bowlers_selections)
#         print('individualbowlerselection - ', individualbowlerselection)
#         print('primary_yaxis_fields - ', primary_yaxis_fields)
#         print('sp - ', sp)
#         print('\n')
    plt.show()
        
#     print(plot_dict)