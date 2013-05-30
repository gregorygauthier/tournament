import random
import networkx as nx
import itertools
"""
Special exception class to handle a paired tournament created with an
odd number of players.
"""
class PlayerParityError(Exception):
    """Create the exception with the specified value text"""
    def __init__(self, value):
        self.value = value
    
    """Returns a string representation of the value text"""
    def __str__(self):
        return repr(self.value)

"""
Special exception class to handle a tournament where no full pairing can be
made.
"""
class NoValidPairingError(Exception):
    """Create the exception with the specified value text"""
    def __init__(self, value):
        self.value = value
    
    """Returns a string representation of the value text"""
    def __str__(self):
        return repr(self.value)

"""
Special exception class to handle an impossible pairing.
If the weight function raises this, then no edge is created.
"""
class ImpossibleMatch(Exception):
    pass


"""
Abstract base class for a paired tournament.

The PairedTournament class represents management of a tournament
wherein all players are paired round by round.  The PairedTournament
intends to include an algorithm that deterministically pairs
players based upon the results of previous rounds.  Examples of
such algorithms include:
* round-robin tournaments
* Swiss pairs
* minimum-weight matching based algorithms
The algorithm also contains a winner function that returns a frozenset
of one or more players who are declared winners based upon the scoreboard
"""
class PairedTournament(object):
    MODIFIED_BRADLEY_TERRY_EPSILON = 1e-6
    
    def __init__(self, players, *args, **kwargs):
        if len(players) % 2 != 0:
            raise PlayerParityError(
"Algorithm must have an even number of players; {0} provided".format(
len(players)))
        self._players = players[:]
        self._scoreboard = []
        self._rounds_complete = 0
        self._win_matrix = (
            {(x, y):0 for x in self._players for y in self._players})
        self._score_table = {x:0 for x in self._players}
        self._modified_bradley_terry_ratings = {x:1.0 for x in self._players}
        self.do_tournament_initialization(*args, **kwargs)
    
    @property
    def players(self):
        return self._players[:]
    
    # scoreboard is a list of frozenset of tuple
    @property
    def scoreboard(self):
        return [r for r in self._scoreboard]
    
    @property
    def rounds_complete(self):
        return self._rounds_complete
    
    @property
    def score_table(self):
        """table = {}
        for p in self.players:
            table[p] = 0
        for result in self.scoreboard:
            for match in result:
                table[match[0]] += 1
        return table"""
        return self._score_table.copy()
    
    @property
    def win_matrix(self):
        return self._win_matrix.copy()
    
    def win_matrix_entry(self, first_player, second_player):
        return self._win_matrix[(first_player, second_player)]
    
    def push_results(self, results):
        self._scoreboard.append(results[:])
        for game in results:
            self._win_matrix[tuple(game)] += 1
            self._score_table[game[0]] += 1
        self._rounds_complete += 1
    
    def do_tournament_initialization(self, *args, **kwargs):
        raise NotImplementedError
    
    def next_pairing(self):
        raise NotImplementedError

    def winner(self):
        raise NotImplementedError
    
    """Computes the modified Bradley-Terry ratings with a fictional 0.5 win
    and 0.5 loss against a team of fixed 1.0 rating.
    
    This method computes the modified Bradley-Terry ratings of the players
    based on the games played and a fictitious 0.5 win and 0.5 loss against
    a team with a fixed 1.0 rating.  This modification ensures that the
    rating is well-defined even when the adjacency digraph is not strongly
    connected.  For the general Bradley-Terry recursion formula, see
    R. A. Bradley and M. E. Terry, "Rank Analysis of Incomplete Block Designs:
    I. The Method of Paired Comparisons", Biometrika 39:324-345 (1952).
    """
    def modified_bradley_terry_ratings(self):
        pass #I'll find the algorithm tomorrow to put in the citation

class RoundRobinPairedTournament(PairedTournament):
    def do_tournament_initialization(self, *args, **kwargs):
        pass
    
    def next_pairing(self):
        if self.rounds_complete >= len(self.players) - 1:
            raise NoValidPairingError
        pairings = set()
        k = len(self.players) - self.rounds_complete - 1
        pairings.add(frozenset([self.players[0],
            self._players[k]]))
        for i in range(1, len(self.players)/2):
            x = k + i
            if x >= len(self.players):
                x -= len(self.players) - 1
            y = k - i
            if y <= 0:
                y += len(self.players) - 1
            pairings.add(frozenset([self.players[x], self.players[y]]))
        return frozenset(pairings)
    
    def winner(self):
        table = self.score_table()
        most_wins = max(table.values())
        winners = set()
        for p in players:
            if win_count[p] == most_wins:
                winners.add(p)
        return frozenset(winners)

class SwissPairedTournament(PairedTournament):
    def do_tournament_initialization(self, *args, **kwargs):
        if 'total_rounds' in kwargs.keys():
            self._total_rounds = kwargs['total_rounds']
        else:
            r = 0
            p = len(self.players) - 1
            while p > 0:
                r += 1
                p >>= 1
            self._total_rounds = r
    
    @property
    def total_rounds(self):
        return self._total_rounds
    
    def have_met(self, p, q):
        if p not in self.players or q not in self.players:
            return False
        for r in self.scoreboard:
            if (p, q) in r or (q, p) in r:
                return True
        return 
    
    def next_pairing(self):
        raise NotImplementedError
    
    def winner(self):
        table = self.score_table()
        most_wins = max(table.values())
        winners = set()
        for p in players:
            if win_count[p] == most_wins:
                winners.add(p)
        return frozenset(winners)

"""
Implementation of Swiss pairs.

Pairings occur from high score group to low.  Within each score group,
the pairings are random.  This algorithm makes no attempt to avoid
repeat pairings.
"""
class RandomSwissPairedTournamentWithRepeats(SwissPairedTournament):
    def next_pairing(self):
        table = self.score_table
        score_groups = {}
        for player, wins in table.items():
            if wins in score_groups.keys():
                score_groups[wins].add(player)
            else:
                score_groups[wins] = set([player])
        candidates = []
        high_score = max(score_groups.keys())
        for score in reversed(sorted(score_groups.keys())):
            players_in_group = list(score_groups[score])
            random.shuffle(players_in_group)
            candidates.extend([(p, score) for p in players_in_group])
        return self.do_pairing(candidates, high_score)
    
    def do_pairing(self, candidates, score_threshold):
        c = candidates[:]
        pairings = set()
        while len(c) > 0:
            p1 = c.pop()
            p2 = c.pop()
            pairings.add(frozenset([p1[0], p2[0]]))
        return frozenset(pairings)

'''Abstract tournament where maximum-weight matchings determine pairings.

This class sets up a framework for tournaments in which pairings are
determined by a maximum-weight matching on a graph where the edge weights
(and existence thereof) are determined by a function of the results thus far.
'''
class MatchingPairedTournament(PairedTournament):
    '''Creates the tournament with the given weight function.
    
    Creates a tournament with the given weight function.  The weight function
    should have four parameters: two players, a win matrix (stored as a dict
    with tuple keys), and a score table (stored as a dict).
    These are passed to the given function when weight(x, y) is called.
    '''
    def do_tournament_initialization(self, weight_function, *args, **kwargs):
        self._wf = weight_function
    
    def weight(self, first_player, second_player):
        return self._wf(first_player, second_player, self.win_matrix,
            self.score_table)
    
    def next_pairing(self):
        graph = nx.Graph()
        graph.add_nodes_from(self.players)
        edges = set()
        for x in itertools.combinations(self.players, 2):
            try:
                w = self.weight(x[0], x[1])
                edges.add((x[0], x[1], w))
            except ImpossibleMatch:
                pass
        graph.add_weighted_edges_from(edges)
        matching_dict = nx.max_weight_matching(graph, maxcardinality=True)
        pl = self.players[:]
        pairing = set()
        while len(pl) > 0:
            p = pl.pop()
            if p not in matching_dict:
                raise NoValidPairingError
            else:
                pairing.add(frozenset([p, matching_dict[p]]))
                pl.remove(matching_dict[p])
        return frozenset(pairing)

class SwissPairsMatchingTournament(MatchingPairedTournament):
    def weight(self, first_player, second_player):
        if (self.win_matrix_entry(first_player, second_player) +
            self.win_matrix_entry(second_player, first_player)) > 0:
            raise ImpossibleMatch
        else:
            return -abs(self.score_table[first_player] -
                self.score_table[second_player])
