from jsonAPI import JSON_Tools  # @unresolvedimport
from SQLiteAPI import BowlingDB  # @unresolvedimport

import os
import sys
import pandas as pd
from subprocess import check_output
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
from datetime import date

subplot_fontsize = 13
default_fig_size = (10,4)
default_fig_dpi = 100

def speciality_plot_SeriesScratch(**kwargs):
    
    # parse out variables
    individualbowlerselection = kwargs['individualbowlerselection']
    season_leagues_selections = kwargs['season_leagues_selections']
    bowlers_selections = kwargs['bowlers_selections']
    bowling_db = kwargs['bowling_db']
    ax1 = kwargs['ax1']
     
    # Query DB based upon the user selections, create plot, then update canvas with new plot
    bowling_df = bowling_db.seriesScratch_query(['SS', 'Avg_Total'], bowlers_selections, individualbowlerselection, season_leagues_selections)
    
    build_axes(bowling_df, ['SS', 'Avg_Total'], bowlers_selections, individualbowlerselection, season_leagues_selections, ax1, specilization=['red_avg_line'])
    
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
    build_axes(bowling_df, ['Gm1', 'Gm2', 'Gm3', 'Avg_Before'], bowlers_selections, individualbowlerselection, season_leagues_selections, ax1, specilization=['red_avg_line', 'NumericMarkers_byfours'])
    
    
def speciality_plot_TeamSeriesHCP(**kwargs):
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
    
    
    build_axes(bowling_df, ['Team_Handicap'], bowlers_selections, individualbowlerselection, season_leagues_selections, ax1, specilization=['PlotLines_BlueOrange_Matching'])
    
def speciality_plot_TeamGameHCP(**kwargs):
    
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
    bowling_df = bowling_db.teamGameHCP_query(bowlers_selections, season_leagues_selections)
    
    # Changing this column name makes it cooperate with plot_TeamHandycapTotal()
    bowling_df['Bowler'] = bowling_df.apply(false_bowler_column_for_TeamHandycapTotal, axis=1)
    
    # If team 22 is included, remove week 1 because we only had 3 of 5 bowlers
    if '22' in bowlers_selections:
        bowling_df = bowling_df[bowling_df['Days'] != 0]
    
    build_axes(bowling_df, ['Gm1_Tm_HCP', 'Gm2_Tm_HCP', 'Gm3_Tm_HCP'], bowlers_selections, individualbowlerselection, season_leagues_selections, ax1, specilization=['PlotLines_BlueOrangeFamilies', 'NumericMarkers_bythrees'])
    

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
    
    # When match point is plotted only have tick labels for 0, 1, 2, 3, & 4
    if 'Match_Points' in primary_yaxis_fields:
        specilization = 'y_ticklabels_0_4'
    
    # otherwise use default tick labels
    else: 
        specilization = []
    
    # Query DB based upon the user selections, create plot, then update canvas with new plot
    bowling_df = bowling_db.previewplot_query(primary_yaxis_fields, bowlers_selections, individualbowlerselection, season_leagues_selections)
    build_axes(bowling_df, primary_yaxis_fields, bowlers_selections, individualbowlerselection, season_leagues_selections, ax1,specilization)


def build_report(utils_directory, dbfilepath, pdffilepath, isreport=True, plot_dict=None):
    
    bowling_db = BowlingDB(dbfilepath)
    
    default_axes_height = 4
    default_axes_width = 10
    default_fig_dpi = 100
    
    
    
    if isreport:
        plot_dict = bowlinginstancedata['plots']
        default_fig_dpi = 300
    
    
    speciality_plots_method_dict = {'Cumulative Match Points': speciality_plot_CumulativeMatchPoints,
                                             'Game Comparison': speciality_plot_GameComparison,
                                             'Team Series w/ Handicap': speciality_plot_TeamSeriesHCP,
                                             'Summary Table': speciality_plot_SummaryTable,
                                             "Series Scratch": speciality_plot_SeriesScratch,
                                             'Team Game w/ Handicap': speciality_plot_TeamGameHCP}
    
    plots_by_page = set_report_pages(plot_dict['KeyOrder'], plots_per_page=3) 
    plot_count_per_page = [len(l) for l in plots_by_page]
    plot_image_filepath = [os.path.join(utils_directory, 'temp_plot_{n}.jpg'.format(n=str(i))) for i in range(len(plots_by_page))]
    
    for page_no, page_plot_list in enumerate(plots_by_page):
        default_fig_size=(default_axes_width, default_axes_height * len(page_plot_list))
        fig = plt.figure(figsize=(default_fig_size), dpi=default_fig_dpi)
        num_plots = len(page_plot_list)
        ax = []
        
        for p, plot_name in enumerate(page_plot_list):
            # Parse plot parameters
            season_leagues_selections = plot_dict[plot_name]['season_leagues_selections']
            bowlers_selections = plot_dict[plot_name]['bowlers_selections']
            individualbowlerselection = plot_dict[plot_name]['individualbowlerselection'] 
            primary_yaxis_fields = plot_dict[plot_name]['primary_yaxis_fields']
            sp = plot_dict[plot_name]['sp']
            
            ax.append(fig.add_subplot(num_plots, 1, 1 + p))
            
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
                
            # route to custom plots
            else:
                custom_plot(season_leagues_selections=season_leagues_selections,
                                                 bowlers_selections=bowlers_selections,
                                                 individualbowlerselection=individualbowlerselection,
                                                 primary_yaxis_fields=primary_yaxis_fields,
                                                 bowling_db=bowling_db,
                                                 ax1=ax[p])
                
        
        # Save image 
        if isreport:
            plt.savefig(plot_image_filepath[page_no], bbox_inches='tight')
    
    if not isreport: # Preview instead of report
        return fig
        plt.close()
    else:
        create_pdf(plot_image_filepath, pdffilepath, plot_count_per_page)
        plt.close()
    
        
def plotlabels(bowling_df, primary_yaxis, bowlers, isIndividualBowlerSelection, season_leagues):
    # Each parameter that is unique will be added to the plot label
    # Each parameter that is universal will be added to the plot title
    # This is done buy checking the length of each list 
        # if it is 1 then it is universal and thus added to the plot title
        # if it is greater than 1 then is is unique and thus added to the plot label
     
    plotlabels_lst = []
    
    # if teams was selected for the bowler selection type
    # then determine the bowlers that are included in the team selection
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

def set_report_pages(plot_list, plots_per_page):
    # Takes a list with each plot name
    # Returns a list (page) of lists (plot_names)
    # The number of plots per page of the report 
    # is defined by plots_per_page parameter
    
    report_pages_plot_list = []
    
    while len(plot_list) > plots_per_page:
        remaining_items = plot_list[:]
        temp_page = []
        
        for plot in remaining_items[:plots_per_page]:
            temp_page.append(plot_list.pop(0))
            
        report_pages_plot_list.append(temp_page)
            
    else:
        report_pages_plot_list.append(plot_list)
        
    return report_pages_plot_list

def build_axes(bowling_df, primary_yaxis, bowlers, isIndividualBowlerSelection, season_leagues, ax1, specilization=[]):
    
    # Determine x axis field based upon the number of days between the 
    # first and last date.  If the difference is beyond the threshold
    # the plot will be vs Days and not Date.
    # This is because when plotting season leagues from different years
    # plotting by date mis-aligns the data visualization
    timedelta = bowling_df['Date'].max() - bowling_df['Date'].min()
    if timedelta.days > 360:
        x_axis_col = 'Days'
    else:
        x_axis_col = 'Date'
    
    # Generate plot labels/titles
    plot_title, plotlabels_lst = plotlabels(bowling_df, primary_yaxis, bowlers, isIndividualBowlerSelection, season_leagues)
    plot = 0
    
    ### Sets the color mapping
    
    # 1st 3 lines darkening shades of blue, next 3 lines darkening shades of orange
    # Note each team has 3 plots each team is assigned a color family for its three plots (blue or orange)
    # A maximum of 2 teams can be include in this type of plot
    if 'PlotLines_BlueOrangeFamilies' in specilization:
        ax1.set_prop_cycle('color',['#000FFF','#888FFF','#D2D5FF','#FF8300', '#FFAD55', '#FFD5A9']) #@UndefinedVariable
    
    # Aligns the 1st 2 colors to the first blue and first orange from the 'TeamGameHCP' color map
    # This way each team will have a consistent color scheme from 'TeamGameHCP' to "TeamSeriesHCP"
    elif "PlotLines_BlueOrange_Matching" in specilization:
        ax1.set_prop_cycle('color',['#000FFF','#FF8300', '#3ED78D', '#D73EA9', '#A3AF0A', '#FF0000']) #@UndefinedVariable
    
    # Default CM is Dark2
    else:
        ax1.set_prop_cycle('color',plt.cm.Dark2(np.linspace(0,1,9))) #@UndefinedVariable
    
    if not isIndividualBowlerSelection: # bowler list box selected by team(s) and not by bowler(s)
        bowlers = bowling_df['Bowler'].unique()
    
    
    # The denominator helps to set the numeric plot line markers 
    if 'NumericMarkers_bythrees' in specilization:
        denominator = 3
    elif 'NumericMarkers_byfours' in specilization:
        denominator = 4
    
    for b in bowlers:
        
        for sl in season_leagues:
            
            for column in primary_yaxis:
                
                # Set marker type depending on plot specilization
                if 'NumericMarkers_bythrees' in specilization or 'NumericMarkers_byfours' in specilization:
                    markersize = 6
                    if round(plot/denominator - int(plot/denominator), 2) == 0.00:
                        marker = '$1$'
                    elif round(plot/denominator - int(plot/denominator), 2) == round(1/denominator, 2):
                        marker = '$2$'
                    elif round(plot/denominator - int(plot/denominator), 2) ==round(2/denominator, 2):
                        marker = '$3$'
                else:
                    marker = 's'
                    markersize = 4
        
                # When plotting season leagues of different years use 'Days' on the x-axis rather than 'Date'
                # otherwise the scaling is terrible
                df = bowling_df[(bowling_df['Bowler'] == b) & (bowling_df['Season_League'] == sl)].copy()
                df.sort_values(by=[x_axis_col], inplace=True)
                xaxis = df[x_axis_col]
                yaxis = df[column]
                
                # If true makes plot line red and dashed
                if 'red_avg_line' in specilization and (column == 'Avg_Before' or column == 'Avg_Total'):
                    ax1.plot(xaxis, yaxis, label=plotlabels_lst[plot], linestyle=':', linewidth=2.0, color='#FF0000', 
                                       marker='s', markersize=4, markeredgecolor='black')
                
                # Else adhere to color map
                else:
                    ax1.plot(xaxis, yaxis, label=plotlabels_lst[plot], linestyle='-', linewidth=2.0,
                                       marker=marker, markersize=markersize, markeredgecolor='black')
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
    
    # For Match point plots where values can only be integers between 0 - 4 
    # set the tick labels where they can only be those values (not decimals) 
    # and customize the y-axis to it is zoomed nicely to scale
    if 'y_ticklabels_0_4' in specilization:
        ax1.set_ylim([-0.5, 4.5])
        ax1.set_yticklabels(['', 0, 1, 2, 3, 4])
                        
    # Turn on y-axis grid
    ax1.grid(b=True, axis='y', linestyle='--', linewidth=0.7, alpha=0.8)
    
    # Turn on legend
    if plotlabels_lst != ['None']:
        ax1.legend(fontsize=8, loc='center', bbox_to_anchor=(-0.03,0.98), frameon=True)
        ax1.legend(fontsize=8)
    
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

def create_pdf(imagelist, pdffilepath, plots):
    # Create a pdf using the image
    pdf = FPDF()
    
    # imagelist is the list with all image filenames
    x,y,w = 0,15,210
#     h = 84 * (len(plots)+1)
#     x,y,w,h = 0,0,210,297 this width and height fill the entire page

    # the loop allows for multiple pages on the pdf
    for p, image in enumerate(imagelist):
        h = 84 * plots[p]
        pdf.add_page()
        pdf.image(image,x,y,w,h)
    pdf.output(pdffilepath, "F")
    
    stdout = check_output('start "" {p}'.format(p=pdffilepath), shell=True, universal_newlines=True)
    
    for image in imagelist:
        os.remove(image)


def false_bowler_column_for_TeamHandycapTotal(row):
    
    if row['Team'] < 10:
        return 'Team 0' + str(row['Team'])
    else:
        return 'Team ' + str(row['Team']) 
    
def starting_plot():
    
    fig = plt.figure(figsize=(default_fig_size), dpi=default_fig_dpi)
    
    ## Left Plot - Bowling Ball #1
    ax1 = fig.add_subplot(1, 2, 1)
    
    # Draws a bowling ball using circles on a plot
    ball_1 = plt.Circle((0.5, 0.5), 0.49, color='#2A5DEF')
    finger1_1 = plt.Circle((0.78, 0.63), 0.06, color='black')
    finger2_1 = plt.Circle((0.63, 0.78), 0.06, color='black')
    thumb_1 = plt.Circle((0.5, 0.5), 0.08, color='black')
    
    # Create left bowling ball
    ax1.add_artist(ball_1)
    ax1.add_artist(finger1_1)
    ax1.add_artist(finger2_1)
    ax1.add_artist(thumb_1)
    
    # Remove axis borders
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    
    # Remove axis labels and tick markers
    ax1.tick_params(bottom="off", labelbottom="off", left="off", labelleft="off") 
    
    ## Left Plot - Bowling Ball #1
    ax2 = fig.add_subplot(1, 2, 2)
    
    # Draws a bowling ball using circles on a plot
    ball_2 = plt.Circle((0.5, 0.5), 0.49, color='#278701')
    finger1_2 = plt.Circle((0.22, 0.63), 0.06, color='black')
    finger2_2 = plt.Circle((0.37, 0.78), 0.06, color='black')
    thumb_2 = plt.Circle((0.5, 0.5), 0.08, color='black')
    
    # Create right bowling ball
    ax2.add_artist(ball_2)
    ax2.add_artist(finger1_2)
    ax2.add_artist(finger2_2)
    ax2.add_artist(thumb_2)
    
    # Remove axis borders
    ax2.spines['right'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)
    
    # Remove axis labels and tick markers
    ax2.tick_params(bottom="off", labelbottom="off", left="off", labelleft="off")

    return fig   

def closeplot():
    plt.close('all')

if __name__ == '__main__':
        
    # Initialize passed arguments & load JSON Data
    # Get parameters for each plot in the report, formatted in JSON data
    jsonfilepath = sys.argv[1]
    pdffilepath = sys.argv[2]
    dbfilepath = sys.argv[3]
    utils_directory = sys.argv[4]
    bowlinginstancedata = JSON_Tools().Load_Data(jsonfilepath)
    
    build_report(utils_directory, dbfilepath, pdffilepath)
    