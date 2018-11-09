import tkinter as tk
from tkinter import ttk
import calendar
import datetime
import plotter # @unresolvedimport
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Window():
    


    def __init__(self, master=None):
        
        
        self.master = master
        self.contentframe = ttk.Frame(self.master, padding=(5, 5, 5, 5))
        
        
        
        self.season_league = []
        self.season_league_strvar = tk.StringVar(value=self.season_league)
        self.season_league_entry = tk.StringVar()
        
        self.bowlers = []
        self.bowlers_strvar = tk.StringVar(value=self.bowlers)
        self.bowler_selection_type = tk.IntVar()
        
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
        seasonleague_btn = tk.Button(self.contentframe, text='Add', command=self.temp)
        seasonleague_lbl_entry = tk.Entry(self.contentframe, textvariable=self.season_league_entry, width=19)
        
        ## Create primary y-axis Widget Group
        self.pri_yaxis = tk.Listbox(self.contentframe, listvariable=self.primary_yaxis_strvar, height=4, width=25,
                                 exportselection=tk.FALSE, selectmode=tk.EXTENDED, name="primary_yaxis")
        pri_yaxis_lbl = tk.Label(self.contentframe, text='Primary y-axis', anchor=tk.W)
        
        ## Create Plot queue Widget Group
        self.plots = tk.Listbox(self.contentframe, listvariable=self.plots_strvar, height=4, width=25,
                                 exportselection=tk.FALSE, selectmode=tk.EXTENDED, name="plots")
        plots_lbl = tk.Label(self.contentframe, text='Plot Queue', anchor=tk.W)
        addplot_btn = tk.Button(self.contentframe, text='Add', command=self.temp)
        removeplot_btn = tk.Button(self.contentframe, text='Remove', command=self.temp)
        
        ## Create bowler Widget Group
        self.bowlers_lbox = tk.Listbox(self.contentframe, listvariable=self.bowlers_strvar, height=4, width=25, exportselection=tk.FALSE, name="bowler")
        bowlers_lbl = tk.Label(self.contentframe, text='Bowlers', anchor=tk.W)
        bowlers_selection_lbl = tk.Label(self.contentframe, text='Bowler Selection Type', anchor=tk.W)
        individual_radio = tk.Radiobutton(self.contentframe, text="Individual", padx=0, variable=self.bowler_selection_type, value=0)
        team_radio = tk.Radiobutton(self.contentframe, text="Team", padx=0, variable=self.bowler_selection_type, value=1)
        
        ## Create secondary y-axis Widget Group
        self.sec_yaxis = tk.Listbox(self.contentframe, listvariable=self.secondary_yaxis_strvar, height=4, width=25,
                                 exportselection=tk.FALSE, selectmode=tk.EXTENDED, name="secondary_yaxis")
        sec_yaxis_lbl = tk.Label(self.contentframe, text='Secondary y-axis', anchor=tk.W)
        
        ## Create Saved Reports queue Widget Group
        self.reports = tk.Listbox(self.contentframe, listvariable=self.reports_strvar, height=4, width=25,
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
        self.pri_yaxis.grid(column=1, row=5, sticky=(tk.S, tk.E, tk.W))
        
        plots_lbl.grid(column=1, row=6, sticky=(tk.S, tk.W))
        self.plots.grid(column=1, row=7, sticky=(tk.S, tk.E, tk.W))
        addplot_btn.grid(column=1, row=8, sticky=(tk.S, tk.W))
        removeplot_btn.grid(column=1, row=8, padx=34, sticky=(tk.S, tk.W))
        
        bowlers_lbl.grid(column=3, row=0, sticky=(tk.S, tk.W))
        self.bowlers_lbox.grid(column=3, row=1, sticky=(tk.S, tk.E, tk.W))
        bowlers_selection_lbl.grid(column=3, row=2)
        individual_radio.grid(column=3, row=3, sticky=(tk.S, tk.W))
        team_radio.grid(column=3, row=3, sticky=(tk.S, tk.E))
        
        sec_yaxis_lbl.grid(column=3, row=4, sticky=(tk.S, tk.W))
        self.sec_yaxis.grid(column=3, row=5, sticky=(tk.S, tk.E, tk.W))
        
        reports_lbl.grid(column=3, row=6, sticky=(tk.S, tk.W))
        self.reports.grid(column=3, row=7, sticky=(tk.S, tk.E, tk.W))
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
        self.pri_yaxis.configure(yscrollcommand=pri_yaxis_sb.set)
        pri_yaxis_sb.config(command=self.pri_yaxis.yview)
        
        # Plot Queue Scroll bar    
        plots_sb = tk.Scrollbar(self.contentframe)
        plots_sb.grid(column=2, row=7, ipady=9, sticky=(tk.S))
        self.plots.configure(yscrollcommand=plots_sb.set)
        plots_sb.config(command=self.plots.yview)
        
        # Bowler Scroll bar    
        bowlers_sb = tk.Scrollbar(self.contentframe)
        bowlers_sb.grid(column=4, row=1, ipady=9, sticky=(tk.S))
        self.bowlers_lbox.configure(yscrollcommand=bowlers_sb.set)
        bowlers_sb.config(command=self.bowlers_lbox.yview)
        
        # Secondary y-axis Scroll bar    
        sec_yaxis_sb = tk.Scrollbar(self.contentframe)
        sec_yaxis_sb.grid(column=4, row=5, ipady=9, sticky=(tk.S))
        self.sec_yaxis.configure(yscrollcommand=sec_yaxis_sb.set)
        sec_yaxis_sb.config(command=self.sec_yaxis.yview)
        
        # Saved Reports Scroll bar    
        reports_sb = tk.Scrollbar(self.contentframe)
        reports_sb.grid(column=4, row=7, ipady=9, sticky=(tk.S))
        self.reports.configure(yscrollcommand=reports_sb.set)
        reports_sb.config(command=self.reports.yview)
        
        # Tab Menu of the main frame
        tab_menu = tk.Menu(self.master) 
        self.master.config(menu=tab_menu)
        
        # Create DataBase tab object
        Database_tab = tk.Menu(tab_menu)
        Load_tab = tk.Menu(tab_menu) #@unusedvariable
        
        # create tab commands for Database tab
        # Commands will be list in the order they are added from 1st is top
        Database_tab.add_command(label='New', command=self.temp)
        Database_tab.add_command(label='Connect', command=self.temp)
        Database_tab.add_command(label='Current', command=self.temp)
        
        tab_menu.add_cascade(label='Database', menu=Database_tab) # Add Database tab object to tab_menu
        
        # Create Load tab object
        Load_tab = tk.Menu(tab_menu)
        
        # create tab commands for Load tab
        Load_tab.add_command(label='Set Dataset Date', command=self.set_load_date)
        Load_tab.add_command(label='Bowling Data', command=self.temp)
        Load_tab.add_command(label='Match Points', command=self.temp)
        
        tab_menu.add_cascade(label='Load', menu=Load_tab) # Add Load tab object to tab_menu
        
        
        self.calendar_selection = {}
        
    
    def _delete_window(self):
#         self.bowling_db.closeDBConnection() 
        try:
            self.master.destroy()
        except:
            pass
    
    def set_load_date(self):
        child = tk.Toplevel()
        Calendar(child, self.calendar_selection)
        
        print('in load data set date')
        print(self.calendar_selection)
        
    def update_canvas(self, fig):
        canvas = FigureCanvasTkAgg(fig, self.contentframe)
        canvas.show()
        canvas.get_tk_widget().grid(column=0, row=0, rowspan=11, sticky=(tk.N,tk.S,tk.E,tk.W))
    
    def temp(self):
        print("Oh, hello there")
        print('Why you no work?')
        
        
    
    
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
        

    
    # Create GUI
    root = tk.Tk()
    bowling_app = Window(root)
    root.mainloop()