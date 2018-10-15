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
    season_best = 'Season - League\tHigh Game\tLow Game\tHigh Series\tLow Series'
    for sl in seasonleagues:
        # Determine high and low games & series for season league
        Gm1 = df['Gm1'][df['Season_League'] == sl]
        Gm2 = df['Gm2'][df['Season_League'] == sl]
        Gm3 = df['Gm3'][df['Season_League'] == sl]
        
        highgame = str(max([Gm1.max(), Gm2.max(), Gm3.max()]))
        highgame = highgame + (" " * (9 - len(highgame))) # uses spaces and monotype font to get the text alignment correct \t doesnt work in matplotlib 
        lowgame = str(min([Gm1.min(), Gm2.min(), Gm3.min()]))
        lowgame = lowgame + (" " * (8 - len(lowgame))) # uses spaces and monotype font to get the text alignment correct \t doesnt work in matplotlib 

        seriesscratch = df['SS'][df['Season_League'] == sl]
        highseries = str(seriesscratch.max())
        highseries = highseries + (" " * (11 - len(highseries))) # uses spaces and monotype font to get the text alignment correct \t doesnt work in matplotlib 
        lowseries = str(seriesscratch.min())
        
        season_best = season_best + '\n' + sl[:15] + "\t" + highgame + "\t" + lowgame + "\t" + highseries + "\t" + lowseries
    
    season_best = season_best.replace("\t", "    ")
        
    for i, p in enumerate(plots):
        ax.append(fig.add_subplot(len(plots)+1, 1, i+1))
        ax[i].set_prop_cycle('color',plt.cm.Dark2(np.linspace(0,1,9))) #@UndefinedVariable
        
        for sl in seasonleagues:
            
            
            
            for col in y_axis_columns[p]:
                y_ss = df[col][df['Season_League'] == sl]
                x_days = df['Days'][df['Season_League'] == sl]
                
                # labels are different for Game Comparison because it has 3 lines pre season league rather then just 1
                if p != 'Game Comparison':
                    lbl = sl
                else:
                    lbl = col + ' ' + sl
                
                ax[i].plot(x_days, y_ss, label=lbl, linestyle='-', linewidth=2.0, 
                               marker='s', markersize=4, markeredgecolor='black')
        
        # Add legend to subplot
        ax[i].legend()       
        
        # drop axis borders    
        ax[i].spines['right'].set_visible(False)
        ax[i].spines['top'].set_visible(False)
        ax[i].spines['left'].set_visible(False)
        ax[i].spines['bottom'].set_visible(False)
         
        # label y-axes & axes title
        ax[i].set_ylabel('{l}\n'.format(l=p))
         
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
    ax[len(plots)].text(-0.1, 0.8, season_best, fontsize=12, family='monospace')
    
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
    
    
    
    