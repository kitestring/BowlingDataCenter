import random
from tkinter import *  # @unusedwildimport
from tkinter import ttk # @importredefinition
from tkinter import filedialog # @importredefinition
import functools
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
matplotlib.use("TkAgg")
from jsonAPI import JSON_Tools # @unresolvedimport
import os
from SQLiteAPI import BowlingDB # @unresolvedimport
from pathlib import Path
import time
import pandas as pd
import plotter # @unresolvedimport
from subprocess import check_output


class Window(Frame):
    


    def __init__(self, db_filepath, master=None):
        Frame.__init__(self, master)
        
        self.default_fig_size = (10,4)
        self.default_fig_dpi = 100
        
        self.master.file = db_filepath
        
        self.master = master
        self.contentframe = ttk.Frame(self.master, padding=(5, 5, 5, 5))
        
        self.bowlers = []
        self.bowlers_strvar = StringVar(value=self.bowlers)
         
        self.plottypes = []
        self.plottypes_strvar = StringVar(value=self.plottypes)
        
        self.statusmsg = StringVar()
        
        self.season_league = []
        self.season_league_strvar = StringVar(value=self.season_league)
        
        
        self.content = StringVar()
        
        self.init_window()
        
    def init_window(self):
        # Create db object
        self.bowling_db = BowlingDB(self.master.file)
        
        self.master.protocol("WM_DELETE_WINDOW", self._delete_window)
        self.master.title("Bowling Data Center")
               
        # Create and grid the outer content frame
        self.contentframe.grid(column=0, row=0, sticky=(N,W,E,S))
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(0, weight=1)
        
        # Initialize the canvas and grit it 
        self.update_canvas(plotter.starting_plot())
        
        # Create the remaining widgets
        seasonleague_lbox = Listbox(self.contentframe, listvariable=self.season_league_strvar, height=5, width=25,
                                 exportselection=FALSE, selectmode=EXTENDED, name="seasonleague")
        seasonleague_lbl = ttk.Label(self.contentframe, text='Season League', anchor=W)
        seasonleague_btn = Button(self.contentframe, text='Add', command=functools.partial(self.add_season_league, 
                                                                                        param=(seasonleague_lbox)))
        seasonleague_lbl_entry = Entry(self.contentframe, textvariable=self.content, width=19)
        
        plottype_lbox = Listbox(self.contentframe, listvariable=self.plottypes_strvar, height=5, width=25,
                                 exportselection=FALSE, selectmode=EXTENDED, name="plotyype")
        plot_lbl = ttk.Label(self.contentframe, text='Plot Type', anchor=W)
        
        bowlers_lbox = Listbox(self.contentframe, listvariable=self.bowlers_strvar, height=5, width=25, exportselection=FALSE, name="bowler")
        bowlers_lbl = ttk.Label(self.contentframe, text='Bowlers', anchor=W)
        
        preview_btn = Button(self.contentframe, text='Preview', command=functools.partial(self.parce_selections, event='preview', 
                                                                                          param=({'plottype_lbox': plottype_lbox, 
                                                                                            'bowlers_lbox': bowlers_lbox,
                                                                                            'seasonleague_lbox':seasonleague_lbox})))
        
        report_btn = Button(self.contentframe, text='Report', command=functools.partial(self.parce_selections, event='report', 
                                                                                        param=({'plottype_lbox': plottype_lbox, 
                                                                                            'bowlers_lbox': bowlers_lbox,
                                                                                            'seasonleague_lbox':seasonleague_lbox})))
         
        load_btn = Button(self.contentframe, text='Load', command=functools.partial(self.parce_selections, event ='load',
                                                                                    param=({'plottype_lbox': plottype_lbox, 
                                                                                            'bowlers_lbox': bowlers_lbox,
                                                                                            'seasonleague_lbox':seasonleague_lbox})))
        status = ttk.Label(self.contentframe, textvariable=self.statusmsg, anchor=W)
        
        # Grid the remaining widgets
        seasonleague_lbl.grid(column=1, row=0, sticky=(S,W))
        seasonleague_lbox.grid(column=1, row=1, sticky=(S,E,W))
        seasonleague_btn.grid(column=1, row=2, sticky=(S,W))
        seasonleague_lbl_entry.grid(column=1, row=2, sticky=(E))
        
        plot_lbl.grid(column=1, row=3, sticky=(S,W))
        plottype_lbox.grid(column=1, row=4, sticky=(S,E,W))
        bowlers_lbl.grid(column=1, row=5, sticky=(S,W))
        bowlers_lbox.grid(column=1, row=6, sticky=(S,E,W))
        
        preview_btn.grid(column=1, row=7, sticky=(S,W))
        report_btn.grid(column=1, row=7, sticky=(S))
        load_btn.grid(column=1, row=7, padx=15, sticky=(S,E))
        
        status.grid(column=0, row=8, columnspan=3, sticky=(W,E))
        
        self.contentframe.grid_columnconfigure(0, weight=1)
        self.contentframe.grid_rowconfigure(0, weight=1)
        
        ## Query DB to initialize listboxes,         
        
        # query db to get unique bowlers & unique season leages
        # Note the query returns a dataframe which is sliced into a series and 
        # then converted to a list
        Bowler = self.bowling_db.getuniquevalues(colummn='Bowler', table='bowling')['Bowler'].tolist()
        Season_League = self.bowling_db.getuniquevalues(colummn='Season_League', table='bowling')['Season_League'].tolist()
        
        # populate and refresh the Season_League & Bowler listboxes
        # Then Colorize alternating listbox rows
        self.refresh_listbox_values(Season_League, seasonleague_lbox, self.season_league_strvar)
        self.refresh_listbox_values(Bowler, bowlers_lbox, self.bowlers_strvar)
        
        self.alternate_listbox_rowcolors(seasonleague_lbox, self.season_league)
        self.alternate_listbox_rowcolors(bowlers_lbox, self.bowlers)
        
        # define plot types listbox
        # self.plottype_dbquery_columns defines which columns will need to be queried to generate the plots
        plottypes = ['Average: Total', 'Average: Per-Day', 'Series: Scratch', 'Series: Handicap', 'Game Comparison', 'Average: Delta']
        self.plottype_dbquery_columns = {'Average: Total': ['Days', 'Avg_After', 'Season_League'], 'Average: Per-Day': ['Days', 'Avg_Today', 'Season_League'], 'Series: Scratch': ['Days', 'SS', 'Season_League'], 
                                'Series: Handicap': ['Days', 'HS', 'Season_League'], 'Game Comparison': ['Days', 'Gm1', 'Gm2', 'Gm3', 'Season_League'], 'Average: Delta': ['Days', 'Avg_Delta', 'Season_League']}
        
        self.y_axis_columns = {'Average: Total': ['Avg_After'], 'Average: Per-Day': ['Avg_Today'], 'Series: Scratch': ['SS', 'Avg_After'], 
                                'Series: Handicap': ['HS', 'Match_Points'], 'Game Comparison': ['Gm1', 'Gm2', 'Gm3', 'Avg_Before'], 'Average: Delta': ['Avg_Delta']}
        
        self.refresh_listbox_values(plottypes, plottype_lbox, self.plottypes_strvar)
        self.alternate_listbox_rowcolors(plottype_lbox, self.plottypes)
        
#         seasonleagues = ['2017-18 Couples', '2018-19 Emil Schramm', '2018-19 Couples']
        
        # Season League Scroll bar    
        seasonleague_sb = ttk.Scrollbar(self.contentframe)
        seasonleague_sb.grid(column=2, row=1, ipady=17, sticky=(S))
        seasonleague_lbox.configure(yscrollcommand=seasonleague_sb.set)
        seasonleague_sb.config(command=seasonleague_lbox.yview)
        
        # Plot Type Scroll bar    
        plottype_sb = ttk.Scrollbar(self.contentframe)
        plottype_sb.grid(column=2, row=4, ipady=17, sticky=(S))
        plottype_lbox.configure(yscrollcommand=plottype_sb.set)
        plottype_sb.config(command=plottype_lbox.yview)
        
        # Bowler Scroll bar    
        bowlers_sb = ttk.Scrollbar(self.contentframe)
        bowlers_sb.grid(column=2, row=6, ipady=17, sticky=(S))
        bowlers_lbox.configure(yscrollcommand=bowlers_sb.set)
        bowlers_sb.config(command=bowlers_lbox.yview)
        
        # Set event bindings for when a plot selection is made,
        plottype_lbox.bind('<<ListboxSelect>>', 
                           functools.partial(self.parce_selections, param=({'plottype_lbox': plottype_lbox, 
                                                                            'bowlers_lbox': bowlers_lbox,
                                                                            'seasonleague_lbox':seasonleague_lbox})))
        bowlers_lbox.bind('<<ListboxSelect>>', 
                           functools.partial(self.parce_selections, param=({'plottype_lbox': plottype_lbox, 
                                                                            'bowlers_lbox': bowlers_lbox,
                                                                            'seasonleague_lbox':seasonleague_lbox})))
        seasonleague_lbox.bind('<<ListboxSelect>>', 
                           functools.partial(self.parce_selections, param=({'plottype_lbox': plottype_lbox, 
                                                                            'bowlers_lbox': bowlers_lbox,
                                                                            'seasonleague_lbox':seasonleague_lbox})))
        
        # Menu of the main frame
        main_menu = Menu(self.master) 
        self.master.config(menu=main_menu)
        
        # Create DataBase tab object
        Database_tab = Menu(main_menu)
        
        # create tab commands for Database tab
        # Commands will be list in the order they are added from 1st is top
        Database_tab.add_command(label='New', command=self.new_database)
        Database_tab.add_command(label='Connect', command=functools.partial(self.connect_db, param=({'plottype_lbox': plottype_lbox, 
                                                                                                            'bowlers_lbox': bowlers_lbox,
                                                                                                            'seasonleague_lbox':seasonleague_lbox})))
        Database_tab.add_command(label='Current', command=self.display_current_db)
        
        #####
        Database_tab.add_command(label='Load Match Points', command=self.load_excel)
        #####
         
        main_menu.add_cascade(label='Database', menu=Database_tab) # Add Database tab object to main_menu
        
        # Starting status message
        self.statusmsg.set(self.message_builder('None', ['None'], ['None']))
    
    def _delete_window(self):
        self.bowling_db.closeDBConnection() 
        try:
            self.master.destroy()
        except:
            pass
    
    def refresh_listbox_values(self, new_values, listbox, listbox_strvar):
        # update listbox list and StringVar
        
        if isinstance(new_values, str) == True:
            new_values = [new_values]
        
        # Create unique list from the new_values and the existing list items
        if str(listbox) == '.!frame.plotyype':
            new_values.extend(self.plottypes)
            self.plottypes = sorted(list(set(new_values)))
            listbox_strvar.set(value=self.plottypes)
            
        elif str(listbox) == '.!frame.bowler':
            new_values.extend(self.bowlers)
            self.bowlers = sorted(list(set(new_values)))
            listbox_strvar.set(value=self.bowlers)
            
        elif str(listbox) == '.!frame.seasonleague':
            new_values.extend(self.season_league)
            self.season_league = sorted(list(set(new_values)))
            listbox_strvar.set(value=self.season_league)
            
    def alternate_listbox_rowcolors(self, lstbox, listbox_list):
        # set the row background colors to alternate for the sake of readability
        for i in range(0,len(listbox_list),2):
                lstbox.itemconfigure(i, background='#f0f0ff')
    
    def load_data(self, bowlers_lbox, seasonleague_lbox, seasonleague_selections):
        
        # Checks if a single season league has been selected
        if seasonleague_selections == ['None'] or len(seasonleague_selections) > 1:
            self.statusmsg.set('Invalid selection: Must select a single season league to load data.\n\n')
            return None
        
        csv_file_path = self.open_file(dialogtitle='Select Bowler History Data File', ftype='*.csv', fdescription='Comma Separated Values', defalut_db_path=os.path.join('t:\\', 'TC', 'Documents', 'BowlingLeagues'))
        
        if csv_file_path == None:
            self.statusmsg.set("Action Aborted: csv file not selected.\n\n")
        else:
            # Load csv data into database
            # Monitor query time
            t0 = time.clock()
            
            self.bowling_db.loadcsvfile(csv_file_path, seasonleague_selections[0])
            self.bowling_db.CommitDB()
            
            t1 = time.clock()
            t_delta = t1 - t0

            self.statusmsg.set('Finished loading:\t%s\nTime Elapsed:\t%s\n' % (csv_file_path, round(t_delta,1)))
            
            ## Update the GUI listboxes
            # query db to get unique bowlers & unique season leages
            # Note the query returns a dataframe which is sliced into a series and 
            # then converted to a list
            Bowler = self.bowling_db.getuniquevalues(colummn='Bowler', table='bowling')['Bowler'].tolist()
            Season_League = self.bowling_db.getuniquevalues(colummn='Season_League', table='bowling')['Season_League'].tolist()
            
            # populate and refresh the Season_League & Bowler listboxes
            self.refresh_listbox_values(Season_League, seasonleague_lbox, self.season_league_strvar)
            self.refresh_listbox_values(Bowler, bowlers_lbox, self.bowlers_strvar)
            
            self.alternate_listbox_rowcolors(seasonleague_lbox, self.season_league)
            self.alternate_listbox_rowcolors(bowlers_lbox, self.bowlers)
            
    def update_canvas(self, fig):
        canvas = FigureCanvasTkAgg(fig, self.contentframe)
        canvas.show()
        canvas.get_tk_widget().grid(column=0, row=0, rowspan=8, sticky=(N,S,E,W))
        
    def create_plot_preview(self, bowler, plot, seasonleagues):
        
        # Make sure that the proper selections have been made, if not abort
        if bowler == 'None' or (plot == ['None'] or len(plot) > 1) or seasonleagues == ['None']:
            self.statusmsg.set('Invalid selection: Must select a bowler, at least 1 season league, and a single plot\n\n')
            return None
        
        else:
            
            
            query_df = self.bowling_db.previewplotquery(columns=self.plottype_dbquery_columns[plot[0]], bowler=bowler, seasonleagues=seasonleagues)
            
            
#             self.plottype_dbquery_columns = {'Average: Total': ['Days', 'Avg_After'], 'Average: Per-Day': ['Days', 'Avg_Today'], 'Series: Scratch': ['Days', 'SS'], 
#                                 'Series: Handicap': ['Days', 'HCP', 'SS'], 'Game Comparison': ['Days', 'Gm1', 'Gm2', 'Gm3'], 'Average: Delta': ['Days', 'Avg_Delta']}
            
            
            # pass the query df to the selected plotter method
            if plot[0] == 'Average: Total':
                fig = plotter.basic(query_df, seasonleagues, 'Avg_After', 'Overall Average', bowler)
                self.update_canvas(fig)
                
            elif plot[0] == 'Average: Per-Day':
                fig = plotter.basic(query_df, seasonleagues, 'Avg_Today', "Per-Day Average", bowler)
                self.update_canvas(fig)
                
            elif plot[0] == 'Series: Scratch':
                fig = plotter.basic(query_df, seasonleagues, 'SS', 'Scratch Series', bowler)
                self.update_canvas(fig)
                
            elif plot[0] == 'Series: Handicap':
                fig = plotter.basic(query_df, seasonleagues, 'HS', 'Handicap Series', bowler)
                self.update_canvas(fig)
                
            elif plot[0] == 'Game Comparison':
                fig = plotter.game(query_df, seasonleagues, 'Game Comparison', bowler)
                self.update_canvas(fig)
            
            elif plot[0] == 'Average: Delta':
                fig = plotter.basic(query_df, seasonleagues, 'Avg_Delta', "Overall Average Change", bowler)
                self.update_canvas(fig)
            
            # Provide status message
            self.statusmsg.set(self.message_builder(bowler=bowler, plots=plot, seasonleague=seasonleagues, message_appendage='\t\t\tSelected Plot Preview Created'))
            
    def create_plot_report(self, bowler, plots, seasonleagues):
        
        # Make sure that the proper selections have been made, if not abort
        if bowler == 'None' or plots == ['None'] or seasonleagues == ['None']:
            self.statusmsg.set('Invalid selection: Must select a bowler, at least 1 season league, and at least 1 plot\n\n')
            return None
        
        else:
            
            # Get all data necessary to build all the selected plots
            # create file paths for image file and json data file used to tranfser
            # plot information to python script which creates plot
            # I uses an independent python script to do this because I couldn't make it work otherwise
            # I was getting strange behavor with matplot lib:
                # closing the program when I ran - plt.savefig(plotimagefilepath, bbox_inches='tight')
                # getting suck and not continuing the script when I ran - plt.show()
            
            query_df = self.bowling_db.plotreportquery(bowler, seasonleagues)
            jsonreportdata = os.path.join(utils_directory, 'Report_data.txt')
            tempfigfilepath = os.path.join(utils_directory, 'TempFig.png')
            
            # Prompt user for pdf file path that plot will be built into
            pdffilepath = self.file_save(dialogtitle='Save Bowling Report to pdf', ftype='pdf', fdescription='pdf Files', 
                                         defalut_db_path=os.path.join('T:\\', 'TC', 'Documents', 'BowlingLeagues'))
            
            # if user provided a valid pdf file path, then create the report
            if pdffilepath != None:
                JSON_Tools.dump_Data_To_File(jsonreportdata, df=query_df.to_json(orient='records'), seasonleagues=seasonleagues, y_axis_columns=self.y_axis_columns, 
                                             bowler=bowler, plots=plots, plotimagefilepath=tempfigfilepath, pdffilepath=pdffilepath)
                
                stdout = check_output('python reportbuilder.py {r}'.format(r=jsonreportdata), shell=True, universal_newlines=True)
                print(stdout)
                
            # If no pdf file path is provided (user hits cancel) no report will be made
            else:
                self.statusmsg.set("Action Aborted, not reported created.\n\n")
                
                                
    def add_season_league(self, param):
        seasonleague_lbox = param
        new_season_league_user_entry = self.content.get()
        
        # Check if entry is already there and that it's not an empty string
        if not new_season_league_user_entry in  self.season_league and new_season_league_user_entry != '':
            
            self.statusmsg.set(value='New season league added: {sl}\n\n'.format(sl=new_season_league_user_entry))
            
            # Adds new value to list box then clears the entry
            self.refresh_listbox_values(new_season_league_user_entry, seasonleague_lbox, self.season_league_strvar)
            self.content.set(value='')
            
            # color codes the alternating rows
            self.alternate_listbox_rowcolors(seasonleague_lbox, self.season_league)
            
        else:
            self.statusmsg.set(value='Invalid Season League Entry "{sl}". Value either already exists or is blank.\n\n'.format(sl=new_season_league_user_entry))
            
        
    def parce_selections(self, event, param):
        # Gets the list box selections and sends them to the 
        # call back depending on the event
        
        # Get the currently selected index(es) for each list box 
        plot_idxs_raw = param['plottype_lbox'].curselection()
        bowler_idxs_raw = param['bowlers_lbox'].curselection()
        seasonleague_indx_raw = param['seasonleague_lbox'].curselection()
        
        # Create a list from the indexes determined above
        if len(plot_idxs_raw)!=0:
            plot_idxs = [int(i) for i in plot_idxs_raw]
            plots = [self.plottypes[i] for i in plot_idxs]
        else:
            plots = ['None']
            
        if len(bowler_idxs_raw)!=0:
            bowler = self.bowlers[int(bowler_idxs_raw[0])]
        else:
            bowler = 'None'
            
        if len(seasonleague_indx_raw)!=0:
            seasonleagues_idxs = [int(i) for i in seasonleague_indx_raw]
            seasonleagues = [self.season_league[i] for i in seasonleagues_idxs]
        else:
            seasonleagues = ['None']
        
        # Depending on the widget, call the correct method
        # call back selector
        if event == 'preview': # preview button click
            self.create_plot_preview(bowler, plots, seasonleagues)
            
        elif event == 'report': # report button click
            self.create_plot_report(bowler, plots, seasonleagues)
#             self.statusmsg.set(self.message_builder(bowler=bowler, plots=plots, seasonleague=seasonleagues, message_appendage='\t\t\tSelected Plot Report Created'))
            
        elif event == 'load': # load button click
            self.load_data(param['bowlers_lbox'], param['seasonleague_lbox'], seasonleagues)
            
        elif str(event.widget) == '.!frame.plotyype': # plottype listbox selection
            self.statusmsg.set(self.message_builder(bowler, plots, seasonleagues))
            
        elif str(event.widget) == '.!frame.bowler': # bowler listbox selection
            self.statusmsg.set(self.message_builder(bowler, plots, seasonleagues))
        
        elif str(event.widget) == '.!frame.seasonleague': # season league listbox selection
            self.statusmsg.set(self.message_builder(bowler, plots, seasonleagues))
            
    def message_builder(self, bowler, plots, seasonleague, message_appendage=''):
        plots_string = ", ".join(plots)
        seasonleague_string = ", ".join(seasonleague)
        return 'Bowler Selected: {b}\nPlots Selected: {p}\nSeason Leagues Selected: {s}{m}'.format(b=bowler, p=plots_string, s=seasonleague_string, m=message_appendage)
    
    def connect_db(self, param):
        self.statusmsg.set("Define Database Connection\n\n")
        temp_db_file = self.open_file()
        
        if temp_db_file == None:
            self.statusmsg.set("Action Aborted: Database connection not established.\n\n")
        else:
            self.statusmsg.set("New Database connection: {f}\n\n".format(f=temp_db_file))
            
            # Update json file with new db location
            self.master.file = temp_db_file
            JSON_Tools.dump_Data_To_File(jsonfilepath, db_filepath = self.master.file)
            
            # disconnect from current db then connect to selected db
            self.bowling_db.closeDBConnection()
            self.bowling_db = None
            self.bowling_db = BowlingDB(self.master.file)
            
            # Clear bowling & season league list boxes
            self.season_league = []
            self.season_league_strvar.set(value=self.season_league)

            self.bowlers = []
            self.bowlers_strvar.set(value=self.bowlers)
            
            # query db to populate and refresh bowling & season league list boxes        
            Bowler = self.bowling_db.getuniquevalues(colummn='Bowler', table='bowling')['Bowler'].tolist()
            Season_League = self.bowling_db.getuniquevalues(colummn='Season_League', table='bowling')['Season_League'].tolist()
            
            # populate and refresh the Season_League & Bowler listboxes
            self.refresh_listbox_values(Season_League, param['seasonleague_lbox'], self.season_league_strvar)
            self.refresh_listbox_values(Bowler, param['bowlers_lbox'], self.bowlers_strvar)
              
            self.alternate_listbox_rowcolors(param['seasonleague_lbox'], self.season_league)
            self.alternate_listbox_rowcolors(param['bowlers_lbox'], self.bowlers)
        
    def new_database(self):
        self.statusmsg.set("Define New Database Connection\n\n")
        temp_db_file = self.file_save()
        if temp_db_file == None:
            self.statusmsg.set("Action Aborted: Database not created.\n\n")
        else:
            self.statusmsg.set("New Database created: {f}\n\n".format(f=temp_db_file))
            self.master.file = temp_db_file
            
            # Update json file with new db location
            self.master.file = temp_db_file
            JSON_Tools.dump_Data_To_File(jsonfilepath, db_filepath = self.master.file)
            
            # disconnect from current db then connect to selected db
            self.bowling_db.closeDBConnection()
            self.bowling_db = None
            self.bowling_db = BowlingDB(self.master.file)
            
            # Clear bowling & season league list boxes
            self.season_league = []
            self.season_league_strvar.set(value=self.season_league)

            self.bowlers = []
            self.bowlers_strvar.set(value=self.bowlers)
            
    def file_save(self, dialogtitle='Create New Database', ftype='db', fdescription='Database Files', defalut_db_path=os.path.join('C:\\', 'ProgramData', 'BowlingData')):
        f = filedialog.asksaveasfilename(initialdir = defalut_db_path, 
                                                            title = dialogtitle, filetypes=((fdescription, '*.' + ftype),))
        if f == None or f == '':
            return None
        elif f.split('.')[-1] == ftype:
            return f
        elif f.split('.')[-1] != ftype:
            return f + '.' + ftype
    
    def open_file(self, dialogtitle='Select Database Connection', ftype='*.db', fdescription='Database Files', defalut_db_path=os.path.join('C:\\', 'ProgramData', 'BowlingData')):    
        f = filedialog.askopenfilename(initialdir = defalut_db_path, 
                                                            title = dialogtitle, filetypes=((fdescription, ftype),))
        if f == None or f == '':
            return None
        else:
            return f
        
    def display_current_db(self):
        try:
            self.statusmsg.set('Current Database Connection: {db}\n\n'.format(db=self.master.file))
        except AttributeError:
            self.statusmsg.set('No Database Connection Established\n\n')
            
    def load_excel(self):
        
        f = filedialog.askopenfilename(initialdir=os.path.join('T:\\', 'TC', 'Documents', 'BowlingLeagues') , 
                                                            title = "Select Excel File with Match Point Data", filetypes=(('Excel Files', '*.xlsx'), ('Excel Macro Files', '*.xlsm'),))
        
        if f == None or f == '':
            self.statusmsg.set('No Excel File Selected Action Aborted\n\n')
            return None
        
        # Extracted data from excel file
        print('hello')
        self.bowling_db.loadexcelfile(f)
        self.bowling_db.CommitDB()
        print('good bye')
        self.statusmsg.set('Excel File Loaded\n\n')
            
    
        

if __name__ == '__main__':
    
    # initialize working directory & json file, if doesn't exist then create it
    # JSON file contains db file path.  If not found the default path will be used
    utils_directory=os.path.join('C:\\', 'ProgramData', 'BowlingData')
    jsonfilepath = os.path.join(utils_directory, 'bowlinginstancedata.txt')
    JSON_Tools = JSON_Tools()
    
    if os.path.isdir(utils_directory) == False:
        os.makedirs(utils_directory)
    
    if os.path.exists(jsonfilepath) == False:
        db_filepath = os.path.join(utils_directory, 'bowling.db') 
        JSON_Tools.dump_Data_To_File(jsonfilepath, db_filepath = os.path.join(utils_directory, 'bowling.db'))
    else:
        db_filepath = JSON_Tools.Load_Data(jsonfilepath)['db_filepath']
    
    # Create GUI
    root = Tk()
    bowling_app = Window(db_filepath, root)
    root.mainloop()