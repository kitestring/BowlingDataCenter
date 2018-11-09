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

def closeplot():
    plt.close()
