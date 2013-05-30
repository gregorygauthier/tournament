import tourney
import tourney_sim
import Tkinter as tk
import ttk

# Adapted from the following resource:
# http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/minimal-app.html

class TourneySimApplication(ttk.Frame):
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    
    def createWidgets(self):
        self._lbl_num_players = ttk.Label(self,
            text='Number of players:')
        self._lbl_num_players.grid(row=0, column=0, sticky=tk.W)
        self._ent_num_players = tk.Spinbox(self, from_=4, to=256, increment=2,
            width=4)
        self._ent_num_players.grid(row=0, column=1)
        self._lbl_num_rounds = ttk.Label(self,
            text='Number of rounds:')
        self._lbl_num_rounds.grid(row=1, column=0, sticky=tk.W)
        self._ent_num_rounds = tk.Spinbox(self, from_=1, to=100, increment=1,
            width=4)
        self._ent_num_rounds.grid(row=1, column=1)
        self._run_button = ttk.Button(self, text='Run tournament',
            command=self.run_tournament)
        self._run_button.grid(columnspan=2, sticky=tk.W + tk.E)
        self._quit_button = ttk.Button(self,
            text='Quit this application', command=self.quit)
        self._quit_button.grid(columnspan=2, sticky=tk.W + tk.E)
    
    @property
    def num_players(self):
        return int(self._ent_num_players.get())
    
    @property
    def num_rounds(self):
        return int(self._ent_num_rounds.get())
    
    def run_tournament(self):
        players = tourney_sim.get_players(self.num_players)
        t = tourney.MatchingPairedTournament(players, weight_function2)
        print("Starting a tournament with {0} players and {1} rounds".format(
            self.num_players, self.num_rounds))
        tourney_sim.test_harness(t, self.num_rounds)
    
def weight_function2(x, y, win_matrix, scores):
    num_previous_matches = win_matrix[(x, y)] + win_matrix[(y, x)]
    repeat_penalty = 0 if num_previous_matches == 0 else (
        2 * num_previous_matches + 1)
    score_penalty = 2 * abs(scores[x] - scores[y])
    return -(repeat_penalty + score_penalty)

def main():
    app = TourneySimApplication()
    app.master.title("Tourney simulation")
    app.mainloop()

if __name__ == "__main__":
    main()
