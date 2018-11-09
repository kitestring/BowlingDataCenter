import tkinter as tk
from tkinter import ttk
import calendar
import datetime
from tkinter import filedialog
from tkinter import messagebox

import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

import plotter # @unresolvedimport
from jsonAPI import JSON_Tools # @unresolvedimport
from SQLiteAPI import BowlingDB # @unresolvedimport

class Window(tk.Frame):
    


    def __init__(self, master, bowlinginstancedata, jsonfilepath, utils_directory):
        tk.Frame.__init__(self, master)
        
        self.master = master
        self.contentframe = ttk.Frame(self.master, padding=(5, 5, 5, 5))
        
        self.master.file = bowlinginstancedata['db_filepath']
        self.saved_reports = bowlinginstancedata['reports']
        self.saved_plots = bowlinginstancedata['plots']
        self.jsonfilepath = jsonfilepath
        self.utils_directory = utils_directory
        self.defaultsave_directory = os.path.join('T:\\', 'TC', 'Documents', 'BowlingLeagues')
        
        
        self.calendar_selection = {}
        
        self.season_league = []
        self.season_league_strvar = tk.StringVar(value=self.season_league)
        self.season_league_entry = tk.StringVar()
        
        self.bowlers = []
        self.bowlers_strvar = tk.StringVar(value=self.bowlers)
        self.bowler_selection_type_intvar = tk.IntVar()
        
        self.primary_yaxis = []
        self.primary_yaxis_strvar = tk.StringVar(value=self.primary_yaxis)
        
        self.secondary_yaxis = []
        self.secondary_yaxis_strvar = tk.StringVar(value=self.secondary_yaxis)
        
        self.plots = []
        self.plots_strvar = tk.StringVar(value=self.plots)
        
        self.reports = []
        self.reports_strvar = tk.StringVar(value=self.reports)
        
        self.statusmsg = tk.StringVar()
        
        self.init_window()
        
    def init_window(self):
        
        # Create db object
        self.bowling_db = BowlingDB(self.master.file)
        
        # Set frame title & close protocol
        self.master.title("Bowling Data Center v2")
        self.master.protocol("WM_DELETE_WINDOW", self._delete_window)
               
        # Create and grid the outer content frame
        self.contentframe.grid(column=0, row=0, sticky=(tk.N,tk.W,tk.E,tk.S))
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(0, weight=1)
        
        # Initialize the canvas and grit it 
        self.update_canvas(plotter.starting_plot())
        
        ## Create Season_League Widget Group
        self.seasonleague_lbox = tk.Listbox(self.contentframe, listvariable=self.season_league_strvar, height=4, width=25,
                                 exportselection=tk.FALSE, selectmode=tk.EXTENDED, name="seasonleague")
        seasonleague_lbl = tk.Label(self.contentframe, text='Season League', anchor=tk.W)
        addseasonleague_lbl = tk.Label(self.contentframe, text='Add Season League', anchor=tk.W)
        seasonleague_btn = tk.Button(self.contentframe, text='Add', command=self.add_season_league)
        seasonleague_lbl_entry = tk.Entry(self.contentframe, textvariable=self.season_league_entry, width=19)
        
        ## Create primary y-axis Widget Group
        self.pri_yaxis_lbox = tk.Listbox(self.contentframe, listvariable=self.primary_yaxis_strvar, height=4, width=25,
                                 exportselection=tk.FALSE, selectmode=tk.EXTENDED, name="primary_yaxis")
        pri_yaxis_lbl = tk.Label(self.contentframe, text='Primary y-axis', anchor=tk.W)
        
        ## Create Plot queue Widget Group
        self.plots_lbox = tk.Listbox(self.contentframe, listvariable=self.plots_strvar, height=4, width=25,
                                 exportselection=tk.FALSE, selectmode=tk.EXTENDED, name="plots")
        plots_lbl = tk.Label(self.contentframe, text='Plot Queue', anchor=tk.W)
        addplot_btn = tk.Button(self.contentframe, text='Add', command=self.temp)
        removeplot_btn = tk.Button(self.contentframe, text='Remove', command=self.temp)
        
        ## Create bowler Widget Group
        self.bowlers_lbox = tk.Listbox(self.contentframe, listvariable=self.bowlers_strvar, height=4, width=25, exportselection=tk.FALSE, name="bowler")
        bowlers_lbl = tk.Label(self.contentframe, text='Bowlers', anchor=tk.W)
        bowlers_selection_lbl = tk.Label(self.contentframe, text='Bowler Selection Type', anchor=tk.W)
        self.individual_radio = tk.Radiobutton(self.contentframe, text="Individual", padx=0, variable=self.bowler_selection_type_intvar, value=0, command=self.bowlingRadioSelection)
        self.team_radio = tk.Radiobutton(self.contentframe, text="Team", padx=0, variable=self.bowler_selection_type_intvar, value=1, command=self.bowlingRadioSelection)
        
        ## Create secondary y-axis Widget Group
        self.sec_yaxis_lbox = tk.Listbox(self.contentframe, listvariable=self.secondary_yaxis_strvar, height=4, width=25,
                                 exportselection=tk.FALSE, selectmode=tk.EXTENDED, name="secondary_yaxis")
        sec_yaxis_lbl = tk.Label(self.contentframe, text='Secondary y-axis', anchor=tk.W)
        
        ## Create Saved Reports queue Widget Group
        self.reports_lbox = tk.Listbox(self.contentframe, listvariable=self.reports_strvar, height=4, width=25,
                                 exportselection=tk.FALSE, selectmode=tk.EXTENDED, name="reports")
        reports_lbl = tk.Label(self.contentframe, text='Saved Reports', anchor=tk.W)
        savereport_btn = tk.Button(self.contentframe, text='Save', command=self.temp)
        removeremove_btn = tk.Button(self.contentframe, text='Remove', command=self.temp)
        
        ## Final Buttons row Widget Group
        preview_btn = tk.Button(self.contentframe, text='Preview', command=self.temp)
        buildreport_btn = tk.Button(self.contentframe, text='Build Report', command=self.temp)
        export_btn = tk.Button(self.contentframe, text='Export csv', command=self.temp)
        
        # Status message output
        status = tk.Label(self.contentframe, textvariable=self.statusmsg, anchor=tk.W)
        
        # Grid widgets
        seasonleague_lbl.grid(column=1, row=0, sticky=(tk.S, tk.W))
        self.seasonleague_lbox.grid(column=1, row=1, sticky=(tk.S, tk.E, tk.W))
        addseasonleague_lbl.grid(column=1, row=2)
        seasonleague_btn.grid(column=1, row=3, sticky=(tk.S, tk.W))
        seasonleague_lbl_entry.grid(column=1, row=3, sticky=(tk.S, tk.E))
        
        pri_yaxis_lbl.grid(column=1, row=4, sticky=(tk.S, tk.W))
        self.pri_yaxis_lbox.grid(column=1, row=5, sticky=(tk.S, tk.E, tk.W))
        
        plots_lbl.grid(column=1, row=6, sticky=(tk.S, tk.W))
        self.plots_lbox.grid(column=1, row=7, sticky=(tk.S, tk.E, tk.W))
        addplot_btn.grid(column=1, row=8, sticky=(tk.S, tk.W))
        removeplot_btn.grid(column=1, row=8, padx=34, sticky=(tk.S, tk.W))
        
        bowlers_lbl.grid(column=3, row=0, sticky=(tk.S, tk.W))
        self.bowlers_lbox.grid(column=3, row=1, sticky=(tk.S, tk.E, tk.W))
        bowlers_selection_lbl.grid(column=3, row=2)
        self.individual_radio.grid(column=3, row=3, sticky=(tk.S, tk.W))
        self.team_radio.grid(column=3, row=3, sticky=(tk.S, tk.E))
        
        sec_yaxis_lbl.grid(column=3, row=4, sticky=(tk.S, tk.W))
        self.sec_yaxis_lbox.grid(column=3, row=5, sticky=(tk.S, tk.E, tk.W))
        
        reports_lbl.grid(column=3, row=6, sticky=(tk.S, tk.W))
        self.reports_lbox.grid(column=3, row=7, sticky=(tk.S, tk.E, tk.W))
        savereport_btn.grid(column=3, row=8, sticky=(tk.S, tk.W))
        removeremove_btn.grid(column=3, row=8, padx=36, sticky=(tk.S, tk.W))
        
        preview_btn.grid(column=1, row=10, sticky=(tk.S, tk.W))
        buildreport_btn.grid(column=1, row=10, padx=54, columnspan=3, sticky=(tk.S, tk.W))
        export_btn.grid(column=1, row=10, padx=133, columnspan=3, sticky=(tk.S, tk.W))
        
        status.grid(column=0, row=11, columnspan=5, sticky=(tk.W, tk.E))
        
        
        # Season League Scroll bar    
        seasonleague_sb = tk.Scrollbar(self.contentframe)
        seasonleague_sb.grid(column=2, row=1, ipady=9, sticky=(tk.S))
        self.seasonleague_lbox.configure(yscrollcommand=seasonleague_sb.set)
        seasonleague_sb.config(command=self.seasonleague_lbox.yview)
        
        # Primary y-axis Scroll bar    
        pri_yaxis_sb = tk.Scrollbar(self.contentframe)
        pri_yaxis_sb.grid(column=2, row=5, ipady=9, sticky=(tk.S))
        self.pri_yaxis_lbox.configure(yscrollcommand=pri_yaxis_sb.set)
        pri_yaxis_sb.config(command=self.pri_yaxis_lbox.yview)
        
        # Plot Queue Scroll bar    
        plots_sb = tk.Scrollbar(self.contentframe)
        plots_sb.grid(column=2, row=7, ipady=9, sticky=(tk.S))
        self.plots_lbox.configure(yscrollcommand=plots_sb.set)
        plots_sb.config(command=self.plots_lbox.yview)
        
        # Bowler Scroll bar    
        bowlers_sb = tk.Scrollbar(self.contentframe)
        bowlers_sb.grid(column=4, row=1, ipady=9, sticky=(tk.S))
        self.bowlers_lbox.configure(yscrollcommand=bowlers_sb.set)
        bowlers_sb.config(command=self.bowlers_lbox.yview)
        
        # Secondary y-axis Scroll bar    
        sec_yaxis_sb = tk.Scrollbar(self.contentframe)
        sec_yaxis_sb.grid(column=4, row=5, ipady=9, sticky=(tk.S))
        self.sec_yaxis_lbox.configure(yscrollcommand=sec_yaxis_sb.set)
        sec_yaxis_sb.config(command=self.sec_yaxis_lbox.yview)
        
        # Saved Reports Scroll bar    
        reports_sb = tk.Scrollbar(self.contentframe)
        reports_sb.grid(column=4, row=7, ipady=9, sticky=(tk.S))
        self.reports_lbox.configure(yscrollcommand=reports_sb.set)
        reports_sb.config(command=self.reports_lbox.yview)
        
        
        ### Tab Menu
        # Tab Menu of the main frame
        tab_menu = tk.Menu(self.master) 
        self.master.config(menu=tab_menu)
        
        # Create DataBase tab object
        Database_tab = tk.Menu(tab_menu)
        Load_tab = tk.Menu(tab_menu) #@unusedvariable
        
        # create tab commands for Database tab
        # Commands will be list in the order they are added from 1st is top
        Database_tab.add_command(label='New', command=self.new_database)
        Database_tab.add_command(label='Connect', command=self.connect_db)
        Database_tab.add_command(label='Current', command=self.display_current_db)
        
        tab_menu.add_cascade(label='Database', menu=Database_tab) # Add Database tab object to tab_menu
        
        # Create Load tab object
        Load_tab = tk.Menu(tab_menu)
        
        # create tab commands for Load tab
        Load_tab.add_command(label='Set Dataset Date', command=self.set_load_date)
        Load_tab.add_command(label='Bowling Data', command=self.load_bowling_data)
        Load_tab.add_command(label='Match Points', command=self.temp)
        
        tab_menu.add_cascade(label='Load', menu=Load_tab) # Add Load tab object to tab_menu
        
        
        ### Set event bindings for when a plot selection is made
        self.seasonleague_lbox.bind('<<ListboxSelect>>', self.select_seasonleague_lbox)
        self.pri_yaxis_lbox.bind('<<ListboxSelect>>', self.lboxtemp)
        self.plots_lbox.bind('<<ListboxSelect>>', self.lboxtemp)
        self.bowlers_lbox.bind('<<ListboxSelect>>', self.lboxtemp)
        self.sec_yaxis_lbox.bind('<<ListboxSelect>>', self.lboxtemp) 
        self.reports_lbox.bind('<<ListboxSelect>>', self.lboxtemp)
        
        ## Initialize the list boxes, note the bowler list box
        # will not be initialized because it is dependent on the 
        # season league selection
        self.update_seasonleague_lbox()
        self.update_yaxis_lboxes()
        self.update_plots_lbox()
        self.update_reports_lbox()
        
        
        
        self.statusmsg.set("Some Bullisht")
        
    def select_seasonleague_lbox(self, e):
        self.update_bowlers_lbox()
    
    def update_seasonleague_lbox(self, new_seasonleague_entry=None):
        # Query DB to get a unique list of all season leagues
        # if there is only 1 a string will be returned, otherwise a list will be returned
        new_season_league_values = self.bowling_db.getuniquevalues(colummn='Season_League', table='bowling')['Season_League'].tolist()
        
        # If a new season league was entered append it to the list
        if new_seasonleague_entry != None:
            new_season_league_values.append(new_seasonleague_entry)
        
        # new values must be a new_season_league_values, this verifies that the 
        # returned values is a list and not just a string
        if isinstance(new_season_league_values, str) == True:
            new_season_league_values = [new_season_league_values]
        
        # Create unique list from the new_values and the existing list items
        new_season_league_values.extend(self.season_league)
        self.season_league = sorted(list(set(new_season_league_values)))
        self.season_league_strvar.set(value=self.season_league)
        
        # set the row background colors to alternate for the sake of readability
        for i in range(0,len(self.season_league),2):
                self.seasonleague_lbox.itemconfigure(i, background='#f0f0ff')
                
    def update_bowlers_lbox(self):
        ## Returns the bowlers that were in the selected season league(s)
        # Check the radio buttons to see if selections should be made by 
        # individual bowler or by team
        
        # Get season league selections
        seasonleagues = self.getSeasonLeagueSelections()
        
        # Verify that at least 1 season league is selected
        if len(seasonleagues)<1:
            pass
        else:
            
            # Query depends on the radio button selection
            if self.bowler_selection_type_intvar.get() == 0: # Individual Bowler Selection
                new_bowlers = self.bowling_db.getUniqueBowlerValuesWhenSeasonLeague(seasonleagues)['Bowler'].tolist()
            elif self.bowler_selection_type_intvar.get() == 1: # Team Bowler Selection
                # fix when the db is updated
                #### the query below must be updated!!!
                new_bowlers = self.bowling_db.getUniqueBowlerValuesWhenSeasonLeague(seasonleagues)['Bowler'].tolist()
            
            # new values must be a new_season_league_values, this verifies that the 
            # returned values is a list and not just a string
            if isinstance(new_bowlers, str) == True:
                new_bowlers = [new_bowlers]
            
            # Update bowlers values in the list box 
            self.bowlers = sorted(new_bowlers)
            self.bowlers_strvar.set(value=self.bowlers)
            
            # set the row background colors to alternate for the sake of readability
            for i in range(0,len(self.bowlers),2):
                    self.bowlers_lbox.itemconfigure(i, background='#f0f0ff')
    
    def update_yaxis_lboxes(self):
        # Query the db and get all the analytically plotable columns (for the y-axis)
        all_db_columns = self.bowling_db.getColumns('bowling')
        non_analytical_columns = ['Bowler_Date', 'Team', 'Days', 'Date', 'Season_League', 'Bowler']
        analytical_columns = [c for c in all_db_columns if c not in non_analytical_columns]       
        
        # Update pri_yaxis & sec_yaxis values in the list boxes 
        self.primary_yaxis = sorted(analytical_columns)
        self.primary_yaxis_strvar.set(value=self.primary_yaxis)
        
        self.secondary_yaxis = sorted(analytical_columns)
        self.secondary_yaxis_strvar.set(value=self.secondary_yaxis)
        
        # set the row background colors to alternate for the sake of readability
        for i in range(0,len(self.secondary_yaxis),2):
                self.pri_yaxis_lbox.itemconfigure(i, background='#f0f0ff')
                self.sec_yaxis_lbox.itemconfigure(i, background='#f0f0ff')
            
    
    def update_plots_lbox(self):
        pass
    
    def update_reports_lbox(self):
        pass
    
    def parce_seasonleague_lbox(self):
        # Returns each seasonleague selection as a list
        # If none are selected then ['None'] is returned
        
        seasonleague_indx_raw = self.seasonleague_lbox.curselection()
        if len(seasonleague_indx_raw)!=0:
            seasonleagues_idxs = [int(i) for i in seasonleague_indx_raw]
            return [self.season_league[i] for i in seasonleagues_idxs]
        else:
            return ['None']

    def bowlingRadioSelection(self):
        # 0 = Individual Bowler Selection
        # 1 = Team Bowler Selection
        # print(self.bowler_selection_type_intvar.get())
        self.update_bowlers_lbox()
            
    def lboxtemp(self, event=None):
        print('Temp Shit')
        
    def getSeasonLeagueSelections(self):
        seasonleague_selections = self.seasonleague_lbox.curselection()
        
        if len(seasonleague_selections)!=0:
            seasonleagues_idxs = [int(i) for i in seasonleague_selections] #@unusedvariable
            return [self.season_league[i] for i in seasonleagues_idxs]
        else:
            return ['None']
    
    def new_database(self):
        self.statusmsg.set("Define New Database Connection\n\n")
        
        temp_db_file = self.file_save(dialogtitle='Create New Database', ftype='db', 
                                      fdescription='Database Files', 
                                      defalut_db_path=self.utils_directory)
        
        if temp_db_file == None:
            self.statusmsg.set("Action Aborted: Database not created.\n\n")
        else:
            self.statusmsg.set("New Database created: {f}\n\n".format(f=temp_db_file))
            self.master.file = temp_db_file
            
            # Update json file with new db location
            self.master.file = temp_db_file
            # The use of the None here is totally confusing
            # This should be implied as the JSON_Tools self object
            # However it throws an error when I don't put a "place holder" parameter here???
            JSON_Tools.dump_Data_To_File(None, self.jsonfilepath, db_filepath = self.master.file,
                                reports = self.saved_reports, plots=self.saved_plots)

            
            # disconnect from current db then connect to selected db
            self.bowling_db.closeDBConnection()
            self.bowling_db = None
            self.bowling_db = BowlingDB(self.master.file)
            
            # Clear bowling & season league list boxes
            self.season_league = []
            self.season_league_strvar.set(value=self.season_league)
 
            self.bowlers = []
            self.bowlers_strvar.set(value=self.bowlers)
            
    def connect_db(self):
        self.statusmsg.set("Define Database Connection\n\n")
        temp_db_file = self.open_file(dialogtitle='Select Database Connection', ftype='db', 
                                      fdescription='Database Files', 
                                      defalut_db_path=self.utils_directory)
        
        if temp_db_file == None:
            self.statusmsg.set("Action Aborted: Database connection not established.\n\n")
        else:
            self.statusmsg.set("New Database connection: {f}\n\n".format(f=temp_db_file))
            
            # Update json file with new db location
            self.master.file = temp_db_file
            # The use of the None here is totally confusing
            # This should be implied as the JSON_Tools self object
            # However it throws an error when I don't put a "place holder" parameter here???
            JSON_Tools.dump_Data_To_File(None, self.jsonfilepath, db_filepath = self.master.file,
                                reports = self.saved_reports, plots=self.saved_plots)
            
            # disconnect from current db then connect to selected db
            self.bowling_db.closeDBConnection()
            self.bowling_db = None
            self.bowling_db = BowlingDB(self.master.file)
            
            # Clear bowling & season league list boxes
            self.season_league = []
            self.season_league_strvar.set(value=self.season_league)

            self.bowlers = []
            self.bowlers_strvar.set(value=self.bowlers)
            
            # refresh season league list box & referesh y-axis list boxes  
            self.update_seasonleague_lbox()
            self.update_yaxis_lboxes()
            
    def display_current_db(self):
        try:
            self.statusmsg.set('Current Database Connection: {db}\n\n'.format(db=self.master.file))
        except AttributeError:
            self.statusmsg.set('No Database Connection Established\n\n')
    
    
    def open_files(self, dialogtitle, ftype, fdescription, defalut_db_path):
        f = filedialog.askopenfilenames(initialdir = defalut_db_path, 
                                                            title = dialogtitle, filetypes=((fdescription, ftype),))
        return f
    
    def open_file(self, dialogtitle, ftype, fdescription, defalut_db_path):    
        f = filedialog.askopenfilename(initialdir = defalut_db_path, 
                                                            title = dialogtitle, filetypes=((fdescription, ftype),))
        if f == None or f == '':
            return None
        else:
            return f
    
    
    def file_save(self, dialogtitle, ftype, fdescription, defalut_db_path):
        
        f = filedialog.asksaveasfilename(initialdir = defalut_db_path, 
                                        title = dialogtitle, filetypes=((fdescription, '*.' + ftype),))
        if f == None or f == '':
            return None
        elif f.split('.')[-1] == ftype:
            return f
        elif f.split('.')[-1] != ftype:
            return f + '.' + ftype
        
    
    def _delete_window(self):
        self.bowling_db.closeDBConnection() 
        try:
            self.master.destroy()
        except:
            pass
    
    def set_load_date(self):
        child = tk.Toplevel()
        Calendar(child, self.calendar_selection)
        
    def load_bowling_data(self):
        
        # Verify that a single season league has been selected
        seasonleague_selections = self.parce_seasonleague_lbox()
        if seasonleague_selections == ['None'] or len(seasonleague_selections) > 1:
            self.statusmsg.set('Invalid selection: Must select a single season league to load data.\n\n')
            return None
        
        
        # Verify a date has been selected
        if self.calendar_selection == {}:
            self.statusmsg.set("Must define the data set date prior to loading bowling data.\n\n")
            return None
        
        
        # Confirm with user that the date is correct
        long_date = str(self.calendar_selection['month_name']) + " " + str(self.calendar_selection['day_selected']) + ", " + str(self.calendar_selection['year_selected'])
        warningmessage = 'You have selected the following dataset date.\nDo you wish to proceed?\n\n{d}'.format(d=long_date)
        MsgBox = tk.messagebox.askquestion('Confirm Data Set Date',warningmessage ,icon = 'warning')
        if MsgBox == 'no':
            self.statusmsg.set("Action Aborted.\n\n")
            return None
        
        
        # Get list of bowling csv files
        csv_file_paths = self.open_files(dialogtitle='Select BowlerList & LeagueSummary csv Files', ftype='csv', 
                                      fdescription='comma separated values', 
                                      defalut_db_path=self.defaultsave_directory)
        
        ## Verify that the selected files are BowlerList.csv & LeagueSummary.csv
        # First check that only 2 files have been selected
        if len(csv_file_paths) != 2:
            self.statusmsg.set('Must select BowlerList.csv & LeagueSummary.csv only.\n\n')
            return None
        
        # Get file names only
        f1 = csv_file_paths[0].split('/')[-1]
        f2 = csv_file_paths[1].split('/')[-1]
        
        # checks that both files are either BowlerList or LeagueSummary
        if not (('BowlerList' in f1 or 'LeagueSummary' in f1) and ('BowlerList' in f2 or 'LeagueSummary' in f2)):
            self.statusmsg.set('One or more of the selected files are invalid.  Must select BowlerList.csv & LeagueSummary.csv only.\n\n')
            return None
        
        # checks that f1 & f2 aren't duplicates of the same "valid" file
        # instead of selected one of each valid file type
        elif ('BowlerList' in f1 and 'BowlerList' in f2) or ('LeagueSummary' in f1 and 'LeagueSummary' in f2):
            self.statusmsg.set('One or more of the selected files are invalid.  Must select BowlerList.csv & LeagueSummary.csv only.\n\n')
            return None
        
        
        ## Selection Validation Complete Begin Extraction & Cleaning
        
        # read both csv files into dataframes
        BowlerList_df = pd.read_csv(csv_file_paths[0])
        LeagueSummary_df = pd.read_csv(csv_file_paths[1])
        
        print(BowlerList_df[BowlerList_df['TM'] == 22].head(5))
        print('\n\n********************\n\n')
        print(LeagueSummary_df[LeagueSummary_df['TM'] == 22].head(5))
        
        
        self.statusmsg.set('Here we go bitch.  I really need to cum.\n\n')
        
        
    def update_canvas(self, fig):
        canvas = FigureCanvasTkAgg(fig, self.contentframe)
        canvas.show()
        canvas.get_tk_widget().grid(column=0, row=0, rowspan=11, sticky=(tk.N,tk.S,tk.E,tk.W))
    
    def add_season_league(self):
        # Get user entered season league value
        new_season_league_user_entry = self.season_league_entry.get()
        
        # Check if entry is already there and that it's not an empty string
        if not new_season_league_user_entry in self.season_league and new_season_league_user_entry != '':
            
            self.statusmsg.set(value='New season league added: {sl}\n\n'.format(sl=new_season_league_user_entry))
            
            # Adds new value to list box then clears the entry
            self.update_seasonleague_lbox(new_season_league_user_entry)
            self.season_league_entry.set(value='')
            
        else:
            self.statusmsg.set(value='Invalid Season League Entry "{sl}". Value either already exists or is blank.\n\n'.format(sl=new_season_league_user_entry))
            
    
    def temp(self):
        print("Oh, hello there")
    
    
class Calendar:
    def __init__(self, parent, values):
        self.values = values
        self.parent = parent
        self.cal = calendar.TextCalendar(calendar.SUNDAY)
        self.year = datetime.date.today().year
        self.month = datetime.date.today().month
        self.wid = []
        self.day_selected = 1
        self.month_selected = self.month
        self.year_selected = self.year
        self.day_name = ''
         
        self.setup(self.year, self.month)
         
    def clear(self):
        for w in self.wid[:]:
            w.grid_forget()
            #w.destroy()
            self.wid.remove(w)
     
    def go_prev(self):
        if self.month > 1:
            self.month -= 1
        else:
            self.month = 12
            self.year -= 1
        #self.selected = (self.month, self.year)
        self.clear()
        self.setup(self.year, self.month)
 
    def go_next(self):
        if self.month < 12:
            self.month += 1
        else:
            self.month = 1
            self.year += 1
         
        #self.selected = (self.month, self.year)
        self.clear()
        self.setup(self.year, self.month)
         
    def selection(self, day, name):
        self.day_selected = day
        self.month_selected = self.month
        self.year_selected = self.year
        self.day_name = name
         
        #data
        self.values['day_selected'] = day
        self.values['month_selected'] = self.month
        self.values['year_selected'] = self.year
        self.values['day_name'] = name
        self.values['month_name'] = calendar.month_name[self.month_selected]
         
        self.clear()
        self.setup(self.year, self.month)
         
    def setup(self, y, m):
        left = tk.Button(self.parent, text='<', command=self.go_prev)
        self.wid.append(left)
        left.grid(row=0, column=1)
         
        header = tk.Label(self.parent, height=2, text='{}   {}'.format(calendar.month_abbr[m], str(y)))
        self.wid.append(header)
        header.grid(row=0, column=2, columnspan=3)
         
        right = tk.Button(self.parent, text='>', command=self.go_next)
        self.wid.append(right)
        right.grid(row=0, column=5)
         
        days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        for num, name in enumerate(days):
            t = tk.Label(self.parent, text=name[:3])
            self.wid.append(t)
            t.grid(row=1, column=num)
         
        for w, week in enumerate(self.cal.monthdayscalendar(y, m), 2):
            for d, day in enumerate(week):
                if day:
                    #print(calendar.day_name[day])
                    b = tk.Button(self.parent, width=1, text=day, command=lambda day=day:self.selection(day, calendar.day_name[(day-1) % 7]))
                    self.wid.append(b)
                    b.grid(row=w, column=d)
                     
        sel = tk.Label(self.parent, height=2, text='{} {} {} {}'.format(
            self.day_name, calendar.month_name[self.month_selected], self.day_selected, self.year_selected))
        self.wid.append(sel)
        sel.grid(row=8, column=0, columnspan=7)
         
        ok = tk.Button(self.parent, width=5, text='OK', command=self.kill_and_save)
        self.wid.append(ok)
        ok.grid(row=9, column=2, columnspan=3, pady=10)
         
    def kill_and_save(self):
        self.parent.destroy()

if __name__ == '__main__':

    # Initialize ProgramData directory & json file, if either doesn't exist then create the missing item
    # Note, the JSON file contains db file path and all other instance data.  
    # If JSON file not found then the default path will be used
    utils_directory=os.path.join('C:\\', 'ProgramData', 'BowlingData')
    jsonfilepath = os.path.join(utils_directory, 'bowlinginstancedata.txt')
    
    # If default ProgramData directory is not found then create it
    # and a new db will be created in the default DB location. 
    if os.path.isdir(utils_directory) == False:
        os.makedirs(utils_directory)
    
    if os.path.exists(jsonfilepath) == False:
        db_filepath = os.path.join(utils_directory, 'bowling.db') 
        JSON_Tools().dump_Data_To_File(jsonfilepath, 
                                       db_filepath = os.path.join(utils_directory, 'bowling.db'),
                                       reports = {}, plots={})
        
    bowlinginstancedata = JSON_Tools().Load_Data(jsonfilepath)

    # Create GUI
    root = tk.Tk()
    bowling_app = Window(root, bowlinginstancedata, jsonfilepath, utils_directory)
    root.mainloop()