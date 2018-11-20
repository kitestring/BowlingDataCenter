from jsonAPI import JSON_Tools  # @unresolvedimport
from SQLiteAPI import BowlingDB  # @unresolvedimport

import sys
import pandas as pd
from subprocess import check_output
import matplotlib.pyplot as plt
import numpy as np

subplot_fontsize = 13


def speciality_plot_SeriesScratch(**kwargs):
    
    # parse out variables
    individualbowlerselection = kwargs['individualbowlerselection']
    season_leagues_selections = kwargs['season_leagues_selections']
    bowlers_selections = kwargs['bowlers_selections']
    bowling_db = kwargs['bowling_db']
    ax1 = kwargs['ax1']
     
    # Query DB based upon the user selections, create plot, then update canvas with new plot
    bowling_df = bowling_db.seriesScratch_query(['SS', 'Avg_Total'], bowlers_selections, individualbowlerselection, season_leagues_selections)
    
    build_axes(bowling_df, ['SS', 'Avg_Total'], bowlers_selections, individualbowlerselection, season_leagues_selections, ax1, red_avg_line = True)
    
def speciality_plot_CumulativeMatchPoints(**kwargs):
    # parse out variables
    individualbowlerselection = kwargs['individualbowlerselection']
    season_leagues_selections = kwargs['season_leagues_selections']
    bowlers_selections = kwargs['bowlers_selections']
    bowling_db = kwargs['bowling_db']
    ax1 = kwargs['ax1']
     
    # Query DB based upon the user selections, and create plot
    bowling_df = bowling_db.matchPointsCumSum_query(bowlers_selections, individualbowlerselection, season_leagues_selections)
    
    build_axes(bowling_df, ['Cumulative_Match_Points'], bowlers_selections, individualbowlerselection, season_leagues_selections, ax1)
    
    
def speciality_plot_GameComparison(**kwargs):
    # parse out variables
    individualbowlerselection = kwargs['individualbowlerselection']
    season_leagues_selections = kwargs['season_leagues_selections']
    bowlers_selections = kwargs['bowlers_selections']
    bowling_db = kwargs['bowling_db']
    ax1 = kwargs['ax1']
    
    # Query DB based upon the user selections, create plot, then update canvas with new plot
    bowling_df = bowling_db.GameComparison_query(bowlers_selections, individualbowlerselection, season_leagues_selections)
    build_axes(bowling_df, ['Gm1', 'Gm2', 'Gm3', 'Avg_Before'], bowlers_selections, individualbowlerselection, season_leagues_selections, ax1, red_avg_line = True)
    
    
def speciality_plot_TeamHandycapTotal(**kwargs):
    # parse out variables
    individualbowlerselection = kwargs['individualbowlerselection']
    season_leagues_selections = kwargs['season_leagues_selections']
    bowlers_selections = kwargs['bowlers_selections']
    bowling_db = kwargs['bowling_db']
    ax1 = kwargs['ax1']
    
    # Verify that on the bowler list box that a team(s) selection has been
    # made not an individual bowler(s) selection
    if individualbowlerselection == True:
        print('Invalid selection: Must make a team selection and not an individual bowler selection.\n\n\n\n')
        return None
         
    # Query DB based upon the user selections, create plot, then update canvas with new plot
    bowling_df = bowling_db.teamHandicap_query(bowlers_selections, season_leagues_selections)
    
    # Changing this column name makes it cooperate with plot_TeamHandycapTotal()
    bowling_df['Bowler'] = bowling_df.apply(false_bowler_column_for_TeamHandycapTotal, axis=1)
    
    # If team 22 is included, remove week 1 because we only had 3 of 5 bowlers
    if '22' in bowlers_selections:
        bowling_df = bowling_df[bowling_df['Days'] != 0]
    
    
    build_axes(bowling_df, ['Team_Handicap'], bowlers_selections, individualbowlerselection, season_leagues_selections, ax1)

    
def speciality_plot_SummaryTable(**kwargs):
     
    # parse out variables
    individualbowlerselection = kwargs['individualbowlerselection']
    season_leagues_selections = kwargs['season_leagues_selections']
    bowlers_selections = kwargs['bowlers_selections']
    bowling_db = kwargs['bowling_db']
    ax1 = kwargs['ax1']
    
    bowling_df = bowling_db.summaryTable_query(bowlers_selections, individualbowlerselection, season_leagues_selections)
    
    buildSummaryTable_axes(bowling_df, ax1)
    
def custom_plot(**kwargs):
     
    # parse out variables
    individualbowlerselection = kwargs['individualbowlerselection']
    season_leagues_selections = kwargs['season_leagues_selections']
    bowlers_selections = kwargs['bowlers_selections']
    primary_yaxis_fields = kwargs['primary_yaxis_fields']
    bowling_db = kwargs['bowling_db']
    ax1 = kwargs['ax1']
    
    # Query DB based upon the user selections, create plot, then update canvas with new plot
    bowling_df = bowling_db.previewplot_query(primary_yaxis_fields, bowlers_selections, individualbowlerselection, season_leagues_selections)
    build_axes(bowling_df, primary_yaxis_fields, bowlers_selections, individualbowlerselection, season_leagues_selections, ax1)


def build_report(isreport=True, plot_dict=None):
    
    bowling_db = BowlingDB(dbfilepath)
    
    default_axes_height = 4
    default_aexe_width = 10
#     default_fig_dpi = 300
    
    
    
    if isreport:
        plot_dict = bowlinginstancedata['plots']
    
    default_fig_size=(default_aexe_width, default_axes_height * len(plot_dict['KeyOrder']))
    
    speciality_plots_method_dict = {'Cumulative Match Points': speciality_plot_CumulativeMatchPoints,
                                             'Game Comparison': speciality_plot_GameComparison,
                                             'Team Handicap Total': speciality_plot_TeamHandycapTotal,
                                             'Summary Table': speciality_plot_SummaryTable,
                                             "Series Scratch": speciality_plot_SeriesScratch}
    
    
    
    # create a new list for each report page
#     fig = plt.figure(figsize=(default_fig_size), dpi=default_fig_dpi)
    fig = plt.figure(figsize=(default_fig_size))
    num_plots = len(plot_dict['KeyOrder'])
    ax = []
    
    for p, plot_name in enumerate(plot_dict['KeyOrder']):
#         print('*****************')
#         print(plot_name)
        # Parse plot parameters
        season_leagues_selections = plot_dict[plot_name]['season_leagues_selections']
        bowlers_selections = plot_dict[plot_name]['bowlers_selections']
        individualbowlerselection = plot_dict[plot_name]['individualbowlerselection'] 
        primary_yaxis_fields = plot_dict[plot_name]['primary_yaxis_fields']
        sp = plot_dict[plot_name]['sp']
        
#         print('season_leagues_selections', season_leagues_selections)
#         print('bowlers_selections: ', bowlers_selections)
#         print('individualbowlerselection: ', individualbowlerselection)
#         print('primary_yaxis_fields: ', primary_yaxis_fields)
#         print('sp: ', sp)
#         
#         print('\n')
        
        ax.append(fig.add_subplot(num_plots, 1, 1 + p))
        ax[p].set_prop_cycle('color',plt.cm.Dark2(np.linspace(0,1,9))) #@UndefinedVariable
        
        # Decision Tree
            # If --> speciality plots
            # elif --> invalid selections 
            # else --> custom plots
            
        # routes to speciality plots
        if sp != 'None' and season_leagues_selections != ['None'] and bowlers_selections != ['None']:
            
            speciality_plots_method_dict[sp](season_leagues_selections=season_leagues_selections,
                                             bowlers_selections=bowlers_selections,
                                             individualbowlerselection=individualbowlerselection,
                                             bowling_db=bowling_db,
                                             ax1=ax[p])
        
        
        # Validate user inputs
        elif season_leagues_selections == ['None'] or bowlers_selections == ['None'] or primary_yaxis_fields == ['None']:
            print('Invalid selection: Must select at least a single season league, bowler, and primary y-axis field to create a plot.\n\n\n\n')
            
        # routes to custom plots
        else:
            custom_plot(season_leagues_selections=season_leagues_selections,
                                             bowlers_selections=bowlers_selections,
                                             individualbowlerselection=individualbowlerselection,
                                             primary_yaxis_fields=primary_yaxis_fields,
                                             bowling_db=bowling_db,
                                             ax1=ax[p])
            
    
        
    if isreport:
        plt.show()
        
def plotlabels(bowling_df, primary_yaxis, bowlers, isIndividualBowlerSelection, season_leagues):
    # Each parameter that is unique will be added to the plot label
    # Each parameter that is universal will be added to the plot title
    # This is done buy checking the length of each list 
        # if it is 1 then it is universal and thus added to the plot title
        # if it is greater than 1 then is is unique and thus added to the plot label
     
    plotlabels_lst = []
    
    # if teams was selected for the bowler selection type
    # the determine the bowlers that are included in the selection
    if not isIndividualBowlerSelection: # bowler list box selected by team(s) and not by bowler(s)
        bowlers = bowling_df['Bowler'].unique()
    
    # Initialize the boolean to determine if a field will be 
    # used in the label or the title 
    if len(bowlers) < 2:
        add_bowler_to_label = False
    else:
        add_bowler_to_label = True
        
    if len(season_leagues) < 2:
        add_sealsonleague_to_label = False
    else:
        add_sealsonleague_to_label = True        
                
    if len(primary_yaxis) < 2:
        add_column_to_label = False
    else:
        add_column_to_label = True
    
    # If at least one field will be added to the label iterate below
    # to generate each of the plot legend labels
    if add_bowler_to_label or add_sealsonleague_to_label or add_column_to_label:
        
        for b in bowlers:
            
            for sl in season_leagues:
                
                for column in primary_yaxis:
                        
                    temp_label_list  = []
                    
                    if add_bowler_to_label:
                        temp_label_list.append(b)
                        
                    if add_sealsonleague_to_label:
                        temp_label_list.append(sl)
                    
                    if add_column_to_label:
                        temp_label_list.append(column)
                        
                    plotlabels_lst.append(' - '.join(temp_label_list))
    
    # if none of the fields will be used for the label
    # return ['None'] to deactivate the displayed legend             
    else:
        plotlabels_lst = ['None']
        
                    
    # Using the universal fields create the plot title
    temp_title_list  = []
                    
    if not add_bowler_to_label:
        temp_title_list.append(bowlers[0])
        
    if not add_sealsonleague_to_label:
        temp_title_list.append(season_leagues[0])
    
    if not add_column_to_label:
        temp_title_list.append(primary_yaxis[0])
        
    plot_title = ' - '.join(temp_title_list)
    
    
    # Remove underscores to make labels/title more aesthetically pleasing
    plot_title = plot_title.replace('_', " ")
    plotlabels_lst = [i.replace('_', " ") for i in plotlabels_lst]
    
    return plot_title, plotlabels_lst

def build_axes(bowling_df, primary_yaxis, bowlers, isIndividualBowlerSelection, season_leagues, ax1, red_avg_line = False):
    
    # Generate plot labels/titles
    plot_title, plotlabels_lst = plotlabels(bowling_df, primary_yaxis, bowlers, isIndividualBowlerSelection, season_leagues)
    plot = 0
    
    if not isIndividualBowlerSelection: # bowler list box selected by team(s) and not by bowler(s)
        bowlers = bowling_df['Bowler'].unique()
    
    for b in bowlers:
        
        for sl in season_leagues:
            
            for column in primary_yaxis:
                # To plot season leagues of different years use 'Days' on the x-axis rather than 'Date'
                df = bowling_df[(bowling_df['Bowler'] == b) & (bowling_df['Season_League'] == sl)].copy()
                df.sort_values(by=['Date'], inplace=True)
                xaxis = df['Date']
                yaxis = df[column]
                
                # If true makes line red and dashed
                if red_avg_line == True and (column == 'Avg_Before' or column == 'Avg_Total'):
                    ax1.plot(xaxis, yaxis, label=plotlabels_lst[plot], linestyle=':', linewidth=2.0, color='#FF0000', 
                                       marker='s', markersize=4, markeredgecolor='black')
                
                # Else adheres to color map
                else:
                    ax1.plot(xaxis, yaxis, label=plotlabels_lst[plot], linestyle='-', linewidth=2.0,
                                       marker='s', markersize=4, markeredgecolor='black')
                plot+=1
                
    # drop axis borders    
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    
    # Turn off x axis tick labels
    ax1.set_xticklabels([])
    
    # drop ticks
    ax1.tick_params(axis="both", which="both", bottom="off", top="off",    
            labelbottom="on", left="off", right="off", labelleft="on")
    
    # Turn on y-axis grid
    ax1.grid(b=True, axis='y', linestyle='--', linewidth=0.7, alpha=0.8)
    
    # Turn on legend
    if plotlabels_lst != ['None']:
        ax1.legend(fontsize=8, loc='center', bbox_to_anchor=(-0.03,0.98), frameon=True)
    
    # Title for plt    
    plt.title(plot_title, fontsize=subplot_fontsize)

def buildSummaryTable_axes(df, ax1):
    
    bowlers = sorted(df['Bowler'].unique().tolist())
    season_leagues = sorted(df['Season_league'].unique().tolist())
    
    # Build season bests string
    season_best = 'Season - League\tBowler Name\tL. Gm\tH. Gm\tL. Ser\tH. Ser\tSt. Avg\tCur. Avg\tMatch Pts\tRank'
    season_best = season_best.replace("\t", " " * 4)
    season_best = season_best + '\n' +  ('-' * len(season_best))
    
    for b in bowlers:
        if len(b) < 11:
            bwl = b + (" " * (11 - len(b)))
        else:
            bwl = b[:11]
        
        for sl in season_leagues:
            try:
                # The static number is the length of the corresponding header
                lg = str(df['Low_Game'][(df['Season_league'] == sl) & (df['Bowler'] == b)].tolist()[0]) 
                lg = lg + (" " * (5 - len(lg)))
                hg = str(df['High_Game'][(df['Season_league'] == sl) & (df['Bowler'] == b)].tolist()[0])
                hg = hg + (" " * (5 - len(hg)))
                ls = str(df['Low_series'][(df['Season_league'] == sl) & (df['Bowler'] == b)].tolist()[0])
                ls = ls + (" " * (6 - len(ls)))
                hs = str(df['High_series'][(df['Season_league'] == sl) & (df['Bowler'] == b)].tolist()[0])
                hs = hs + (" " * (6 - len(hs)))
                sa = str(df['Start_Avg'][(df['Season_league'] == sl) & (df['Bowler'] == b)].tolist()[0])
                sa = sa + (" " * (7 - len(sa)))
                ca = str(df['Current_Avg'][(df['Season_league'] == sl) & (df['Bowler'] == b)].tolist()[0])
                ca = ca + (" " * (8 - len(ca)))
                mp = str(int(df['Match_Pts'][(df['Season_league'] == sl) & (df['Bowler'] == b)].tolist()[0]))
                mp = mp + (" " * (9 - len(mp)))
                rk = str(df['Rank'][(df['Season_league'] == sl) & (df['Bowler'] == b)].tolist()[0])
                
                season_best = season_best + '\n' + sl[:15] + "\t" + bwl + "\t" + lg + "\t" + hg + "\t" + ls + "\t" + hs + "\t" + sa + "\t" + ca + "\t" + mp + "\t" + rk 
            
            except IndexError:
                # If the user defined query conditions returns a null row 
                # this handles the index error
                pass
            
    season_best = season_best.replace("\t", " " * 4)
    
    ax1.plot([0,1] , [0,1], color='white')
    
    # Add season best text on plot
    ax1.text(-0.13, 0.4, season_best, fontsize=9, family='monospace')
    
    ## Remove all graph like stuff from plot
    # drop axis borders    
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    # drop ticks
    ax1.tick_params(axis="both", which="both", bottom="off", top="off",    
            labelbottom="off", left="off", right="off", labelleft="off")

def false_bowler_column_for_TeamHandycapTotal(row):
    
    if row['Team'] < 10:
        return 'Team 0' + str(row['Team'])
    else:
        return 'Team ' + str(row['Team'])    

if __name__ == '__main__':
        
    # Initialize passed arguments & load JSON Data
    # Get parameters for each plot in the report, formatted in JSON data
    jsonfilepath = sys.argv[1]
    pdffilepath = sys.argv[2]
    dbfilepath = sys.argv[3]
    bowlinginstancedata = JSON_Tools().Load_Data(jsonfilepath)
    
    build_report()
    