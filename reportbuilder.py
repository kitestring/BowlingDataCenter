import sys
from jsonAPI import JSON_Tools # @unresolvedimport
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
matplotlib.use("TkAgg")
import pandas as pd
import random
import numpy as np
from fpdf import FPDF
from subprocess import check_output


default_fig_size = (10,4)
default_fig_dpi = 300

if __name__ == '__main__':
    
    # Read the json data
    reportdata_jsonstring = sys.argv[1]
    JSON_Tools = JSON_Tools()
    reportdatalib = JSON_Tools.Load_Data(reportdata_jsonstring)
    
    # parce out the json data
    df = pd.read_json(reportdatalib['df'], orient='records')
    seasonleagues = reportdatalib['seasonleagues']
    y_axis_columns = reportdatalib['y_axis_columns']
    bowler = reportdatalib['bowler']
    plots = reportdatalib['plots']
    plotimagefilepath = reportdatalib['plotimagefilepath']
    pdffilepath = reportdatalib['pdffilepath']
    
    # Size the figure based upon the number of selected sub-plots
    fig_h = (len(plots) + 1) * 4
    fig_size = (10, fig_h)
    
    fig = plt.figure(figsize=fig_size)
    ax = []
    
    # Build season bests string
    season_best = 'Season - League\tHigh Game\tLow Game\tHigh Series\tLow Series\tAverage\tMatch Pts'
    for sl in seasonleagues:
        # Determine high and low games & series for season league
        Gm1 = df['Gm1'][df['Season_League'] == sl]
        Gm2 = df['Gm2'][df['Season_League'] == sl]
        Gm3 = df['Gm3'][df['Season_League'] == sl]
        
        CurrentAverage = df['Avg_After'][df['Date'] == df['Date'].max()].tolist()
        CurrentAverage = str(CurrentAverage[0]) + (" " * (5 - len(CurrentAverage)))
        
        highgame = str(max([Gm1.max(), Gm2.max(), Gm3.max()]))
        highgame = highgame + (" " * (9 - len(highgame))) # uses spaces and monotype font to get the text alignment correct \t doesnt work in matplotlib 
        lowgame = str(min([Gm1.min(), Gm2.min(), Gm3.min()]))
        lowgame = lowgame + (" " * (8 - len(lowgame))) # uses spaces and monotype font to get the text alignment correct \t doesnt work in matplotlib 
        
        seriesscratch = df['SS'][df['Season_League'] == sl]
        highseries = str(seriesscratch.max())
        highseries = highseries + (" " * (11 - len(highseries))) # uses spaces and monotype font to get the text alignment correct \t doesnt work in matplotlib 
        lowseries = str(seriesscratch.min()) 
        lowseries = lowseries + (" " * (10 - len(lowseries)))
        
        MatchPts = str(df['Match_Points'][df['Season_League'] == sl].sum())
        
        season_best = season_best + '\n' + sl[:15] + "\t" + highgame + "\t" + lowgame + "\t" + highseries + "\t" + lowseries + "\t" + CurrentAverage + "\t" + MatchPts
    
    season_best = season_best.replace("\t", " " * 3)
        
    for i, p in enumerate(plots):
        ax.append(fig.add_subplot(len(plots)+1, 1, i+1))
        ax[i].set_prop_cycle('color',plt.cm.Dark2(np.linspace(0,1,9))) #@UndefinedVariable
        
        for sl in seasonleagues:
            
            
            
            for col in y_axis_columns[p]:
                y_ss = df[col][df['Season_League'] == sl]
                x_days = df['Days'][df['Season_League'] == sl]
                
                # each plot will have its own section to add a plot
                # this will make it a bit more readable
                # customize the labels for a given plot
                if p == 'Series: Handicap':
                    if col == 'HS':
                        ax[i].plot(x_days, y_ss, label="Series Handicap", linestyle='-', linewidth=2.0, color='#ff5700',
                                       marker='s', markersize=4, markeredgecolor='black')
                    elif col == 'Match_Points':
                        ax2 = ax[i].twinx()
                        ax2.plot(x_days, y_ss, label="Match Points", linestyle='-', linewidth=2.0, color="#00ffff", 
                                       marker='s', markersize=4, markeredgecolor='black')
                        
                        ax[i].set_ylabel('Series Handicap\n')
                        ax2.set_ylabel('\nMatch Points')
                        
                        # Add legend to subplot
                        ax2.legend(fontsize=9)       
                        
                        # drop axis borders    
                        ax2.spines['right'].set_visible(False)
                        ax2.spines['top'].set_visible(False)
                        ax2.spines['left'].set_visible(False)
                        ax2.spines['bottom'].set_visible(False)
                         
#                         # Turn off x-axis tick labels
                        
                        ax2.set_ylim([-0.25,4.25])
                        ax2.set_yticklabels(['', '', '', 1, '', 2, '',3, '',4])
                         
                        # drop ticks
                        ax2.tick_params(axis="both", which="both", bottom="off", top="off",    
                                labelbottom="on", left="off", right="off", labelleft="off")
                        
                        # Drop legends
                        ax[i].legend(fontsize=10, loc='center', bbox_to_anchor=(0.0,-0.05), frameon=True)
                        ax2.legend(fontsize=10, loc='center', bbox_to_anchor=(1.0,-0.05), frameon=True)
                        
                    
                else:
                
                    if p == 'Series: Scratch':
                        if col == 'SS':
                            lbl = 'Series'
                        elif col == 'Avg_After':
                            lbl = 'Average - After'
                    elif p == 'Game Comparison':
                        lbl = col.replace('m', 'ame ').replace('g_Before', 'erage - Before')
                        
                        
                    else:
                        lbl = sl
                    
                    # gets average series by multiplyting average  by 3
                    # plots using a dotted line and a red marker
                    if col == 'Avg_After' and p == 'Series: Scratch':
                        y_ss = df[col][df['Season_League'] == sl] * 3
                        
                        ax[i].plot(x_days, y_ss, label=lbl, linestyle=':', linewidth=2.0, color='#FF0000', 
                                       marker='s', markersize=4, markeredgecolor='black')
                        
                    # if case is true creates the red dotted line for average
                    elif col == 'Avg_Before' and p == 'Game Comparison':
                        ax[i].plot(x_days, y_ss, label=lbl, linestyle=':', linewidth=2.0, color='#FF0000', 
                                       marker='s', markersize=4, markeredgecolor='black')
                    else:
                        ax[i].plot(x_days, y_ss, label=lbl, linestyle='-', linewidth=2.0, 
                                       marker='s', markersize=4, markeredgecolor='black')
        
        # drop axis borders    
        ax[i].spines['right'].set_visible(False)
        ax[i].spines['top'].set_visible(False)
        ax[i].spines['left'].set_visible(False)
        ax[i].spines['bottom'].set_visible(False)
        
        # Add legend to subplot
        # label y-axes & axes title
        if p != 'Series: Handicap': 
            ax[i].set_ylabel('{l}\n'.format(l=p))
            ax[i].legend(fontsize=10)
         
        # Turn on y-axis grid
        ax[i].grid(b=True, axis='y', linestyle='--', linewidth=0.7, alpha=0.3)
         
        # Turn off x-axis tick labels
        ax[i].set_xticklabels([])
         
        # drop ticks
        ax[i].tick_params(axis="both", which="both", bottom="off", top="off",    
                labelbottom="on", left="off", right="off", labelleft="on")
    
    # Title for plt    
    plt.suptitle(bowler, fontsize=20)
    
    
    ## Add season bests data to last empty plot
    ax.append(fig.add_subplot(len(plots)+1, 1, len(plots)+1))
    ax[len(plots)].plot([0,1] , [0,1], color='white')
    
    # Add season best text on plot
    ax[len(plots)].text(-0.12, 0.85, season_best, fontsize=11, family='monospace')
    
    ## Remove all graph like stuff from plot
    # drop axis borders    
    ax[len(plots)].spines['right'].set_visible(False)
    ax[len(plots)].spines['top'].set_visible(False)
    ax[len(plots)].spines['left'].set_visible(False)
    ax[len(plots)].spines['bottom'].set_visible(False)
    # drop ticks
    ax[len(plots)].tick_params(axis="both", which="both", bottom="off", top="off",    
            labelbottom="off", left="off", right="off", labelleft="off")
    
    # Save image
    plt.savefig(plotimagefilepath, bbox_inches='tight')
    
    # Create a pdf using the image
    pdf = FPDF()
    imagelist = [plotimagefilepath]
    
    # imagelist is the list with all image filenames
    x,y,w = 0,0,210
    h = 84 * (len(plots)+1)
#     x,y,w,h = 0,0,210,297 this width and height fill the entire page
    
    # the loop allows for multiple pages on the pdf
    for image in imagelist:
        pdf.add_page()
        pdf.image(image,x,y,w,h)
    pdf.output(pdffilepath, "F")
    
    stdout = check_output('start "" {p}'.format(p=pdffilepath), shell=True, universal_newlines=True)
    
    
    
    