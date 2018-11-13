import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
matplotlib.use("TkAgg")
import pandas as pd
import random
import numpy as np
from fpdf import FPDF

default_fig_size = (10,4)
default_fig_dpi = 100



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

def custom_plot_primaryaxisonly(bowling_df, primary_yaxis, bowlers, isIndividualBowlerSelection, season_leagues):
    # Generate plot labels/titles
    plot_title, plotlabels_lst = plotlabels(bowling_df, primary_yaxis, bowlers, isIndividualBowlerSelection, season_leagues)
    plot = 0
    
    ## Create figure, add Sub-plot, and set colors
    fig = plt.figure(figsize=(default_fig_size), dpi=default_fig_dpi)
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.set_prop_cycle('color',plt.cm.Dark2(np.linspace(0,1,9))) #@UndefinedVariable
    
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
                
                ax1.plot(xaxis, yaxis, label=plotlabels_lst[plot], linestyle='-', linewidth=2.0,
                                   marker='s', markersize=4, markeredgecolor='black')
                plot+=1
                
    # drop axis borders    
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    
    # label y-axes
#     a1[i].set_ylabel('Pins')
    
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
    plt.suptitle(plot_title, fontsize=16)
    
    return fig

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
    
    print(plot_title)
    print(plotlabels_lst)
    
    return plot_title, plotlabels_lst
                
        
        

def closeplot():
    plt.close()
