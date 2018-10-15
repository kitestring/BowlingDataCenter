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

def basic(df, seasonleagues, y_col, y_lbl, bowler, default_fig_size=default_fig_size, default_fig_dpi=default_fig_dpi):
    
    fig = Figure(figsize=default_fig_size, dpi=default_fig_dpi)
    ax = fig.add_subplot(1,1,1)
    ax.set_prop_cycle('color',plt.cm.Dark2(np.linspace(0,1,9))) #@UndefinedVariable
    
    for sl in seasonleagues:
        y_ss = df[y_col][df['Season_League'] == sl]
        x_days = df['Days'][df['Season_League'] == sl]
        
        ax.plot(x_days, y_ss, label=sl, linestyle='-', linewidth=2.0, 
                       marker='s', markersize=4, markeredgecolor='black')
        
    # high & low values
#     ax.text(10600, 410, r'm/z = $\mathregular{C_2*TOF^2 + C_1*TOF + C_0}$', fontsize=14)
    
    # drop axis borders    
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    
    # label y-axes & axes title
    ax.set_ylabel('{l}\n'.format(l=y_lbl))
    ax.set_title(bowler)
    
    # Turn on y-axis grid
    ax.grid(b=True, axis='y', linestyle='--', linewidth=0.7, alpha=0.3)
    
    # Turn off x-axis tick labels
    ax.set_xticklabels([])
    
    # drop ticks
    ax.tick_params(axis="both", which="both", bottom="off", top="off",    
            labelbottom="on", left="off", right="off", labelleft="on")
    
    # Add legend to subplot
    ax.legend()
         
    return fig

def game(df, seasonleagues, y_lbl, bowler, default_fig_size=default_fig_size, default_fig_dpi=default_fig_dpi):
    
    fig = Figure(figsize=default_fig_size, dpi=default_fig_dpi)
    ax = fig.add_subplot(1,1,1)
    ax.set_prop_cycle('color',plt.cm.Dark2(np.linspace(0,1,9))) #@UndefinedVariable
    
    for sl in seasonleagues:
        
        for g in ['Gm1', 'Gm2', 'Gm3']:
            
            y_ss = df[g][df['Season_League'] == sl]
            x_days = df['Days'][df['Season_League'] == sl]
            ax.plot(x_days, y_ss, label=g + ' ' + sl, linestyle='-', linewidth=2.0, 
                           marker='s', markersize=4, markeredgecolor='black')
    
    # drop axis borders    
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    
    # label y-axes & axes title
    ax.set_ylabel('{l}\n'.format(l=y_lbl))
    ax.set_title(bowler)
    
    # Turn on y-axis grid
    ax.grid(b=True, axis='y', linestyle='--', linewidth=0.7, alpha=0.3)
    
    # Turn off x-axis tick labels
    ax.set_xticklabels([])
    
    # drop ticks
    ax.tick_params(axis="both", which="both", bottom="off", top="off",    
            labelbottom="on", left="off", right="off", labelleft="on")
    
    # Add legend to subplot
    ax.legend()
         
    return fig

def report_plot(df, seasonleagues, y_axis_columns, bowler, plots, plotimagefilepath):
#     y_axis_columns = {'Average: Total': ['Avg_After'], 'Average: Per-Day': ['Avg_Today'], 'Series: Scratch': ['SS'], 
#                                 'Series: Handicap': ['HS'], 'Game Comparison': ['Gm1', 'Gm2', 'Gm3'], 'Average: Delta': ['Avg_Delta']}
    
    # Closes the Bowling ball start-up plot
    closeplot()
    
    # Size the figure based upon the number of selected sub-plots
    fig_h = len(plots) * 4
    fig_size = (10, fig_h)
    
    fig = plt.figure(figsize=fig_size)
    ax = []
    
    for i, p in enumerate(plots):
        ax.append(fig.add_subplot(len(plots), 1, i+1))
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
#         ax[i].set_title(bowler)
         
        # Turn on y-axis grid
        ax[i].grid(b=True, axis='y', linestyle='--', linewidth=0.7, alpha=0.3)
         
        # Turn off x-axis tick labels
        ax[i].set_xticklabels([])
         
        # drop ticks
        ax[i].tick_params(axis="both", which="both", bottom="off", top="off",    
                labelbottom="on", left="off", right="off", labelleft="on")
        

#     plt.legend()
    plt.suptitle(bowler, fontsize=20)
#     plt.savefig(plotimagefilepath, bbox_inches='tight')
        
        
    plt.show(block=False)
#     print('hello')
#     plt.close()

def starting_plot():
    # Draws a bowling ball using circles on a plot
    ball = plt.Circle((0.5, 0.5), 0.49, color='#2A5DEF')
    finger1 = plt.Circle((0.78, 0.63), 0.06, color='black')
    finger2 = plt.Circle((0.63, 0.78), 0.06, color='black')
    thumb = plt.Circle((0.5, 0.5), 0.08, color='black')
    
    fig, ax = plt.subplots(figsize=(4,4), dpi=default_fig_dpi)
    
    ax.add_artist(ball)
    ax.add_artist(finger1)
    ax.add_artist(finger2)
    ax.add_artist(thumb)
    
    # Remove axis borders
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    
    # Remove axis labels and tick markers
    plt.tick_params(bottom="off", labelbottom="off", left="off", labelleft="off") 

    return fig

def closeplot():
    plt.close()

def writepdf(imagelist, pdffilepath):
    pdf = FPDF()
    
    # imagelist is the list with all image filenames
#     imagelist = ['c:\\Users\\Ken_Kite\\Pictures\\IMG_1720_20140505_195042.JPG']
    x,y,w,h = 0,0,210,297
    
    for image in imagelist:
        pdf.add_page()
        pdf.image(image,x,y,w,h)
    pdf.output(pdffilepath, "F")
















