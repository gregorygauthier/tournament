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
    def __init__(self, value=''):
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
    MODIFIED_BRADLEY_TERRY_EPSILON = 1e-5
    
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
        self._is_modified_bradley_terry_dirty = False
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
    
    def score_table_entry(self, player):
        return self._score_table[player]
    
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
        self._is_modified_bradley_terry_dirty = True
    
    def do_tournament_initialization(self, *args, **kwargs):
        raise NotImplementedError
    
    def next_pairing(self):
        raise NotImplementedError
    
    """Generates a ranking of the players in the tournament.
    
    The ranking takes the form of a dict mapping each player to a value
    that serves as a sort key.  The sort keys
    are arranged such that (a) players with higher-valued keys are ranked above
    players with lower-valued keys and (b) players with equal keys are ranked
    as tied.  The keys may have additional meaning depending on the tournament
    (for example, it may be the number of wins or the estimated ability of
    the player based on the games played), or the keys may be arbitrary.
    """
    def ranking(self):
        raise NotImplementedError
    
    """Computes the modified Bradley-Terry ratings with a fictional 0.5 win
    and 0.5 loss against a team of fixed 1.0 rating.
    
    This method computes the modified Bradley-Terry ratings of the players
    based on the games played and a fictitious 0.5 win and 0.5 loss against
    a team with a fixed 1.0 rating.  This modification ensures that the
    rating is well-defined even when the adjacency digraph is not strongly
    connected.  For the general Bradley-Terry recursion formula, see
    R. A. Bradley and M. E. Terry, "Rank Analysis of Incomplete Block Designs:
    I. The Method of Paired Comparisons", Biometrika 39:324-345 (1952)
    and R. A. Bradley, "Science, Statistics, and Paired Comparisons" (1975)
    available at
    http://stat.fsu.edu/techreports/scanned%20in%20reports/M337.pdf
    """
    def modified_bradley_terry_ratings(self, player=None):
        if not self._is_modified_bradley_terry_dirty:
		    if player is None:
		        return self._modified_bradley_terry_ratings.copy()
		    else:
		        return self._modified_bradley_terry_ratings[player]
        old_ratings = self._modified_bradley_terry_ratings
        done = False
        while not done:
            new_ratings = {x:(self.score_table_entry(x) + 0.5)/
                (sum([0 if y == x else
                (self.win_matrix_entry(x, y) + self.win_matrix_entry(y, x)) /
                (old_ratings[x] + old_ratings[y])
                for y in self.players]) + (1 / (1 + old_ratings[x])))
                for x in self.players}
            s = sum(new_ratings.values())
            done = True
            for x in self.players:
                if abs(new_ratings[x] - old_ratings[x]) > (
                    self.MODIFIED_BRADLEY_TERRY_EPSILON):
                    done = False
                    break
            old_ratings = new_ratings
        self._modified_bradley_terry_ratings = new_ratings
        self._is_modified_bradley_terry_dirty = False
        if player is None:
		    return new_ratings.copy()
        else:
            return new_ratings[player]

class RoundRobinPairedTournament(PairedTournament):
    def do_tournament_initialization(self, *args, **kwargs):
        pass
    
    def next_pairing(self):
        r = self.rounds_complete % (len(self.players) - 1)
        pairings = set()
        k = len(self.players) - r - 1
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
    
    def ranking(self):
        return {x: self.score_table_entry(x) for x in self.players}

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
    
    def ranking(self):
        return {x: self.score_table_entry(x) for x in self.players}

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
        return self._wf(self, first_player, second_player)
    
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
    
    def ranking(self):
        return self.modified_bradley_terry_ratings()

class SwissPairsMatchingTournament(MatchingPairedTournament):
    def weight(self, first_player, second_player):
        if (self.win_matrix_entry(first_player, second_player) +
            self.win_matrix_entry(second_player, first_player)) > 0:
            raise ImpossibleMatch
        else:
            return -abs(self.score_table[first_player] -
                self.score_table[second_player])

class PowerMatchedTournament(PairedTournament):
    """Initialize a power-matched tournament with the given card
    system and final card rankings.
    
    card_system is a sequence of sets of tuples: each set of tuples is
    a partition of {0, 1, ..., len(players)-1}.  After each match, the winner
    gets the card closer to 0 and the loser gets the card closer to
    len(players)-1.
    
    final_card_rankings is a tuple of length len(players) and
    values real numbers.  At the end of the tournament, the ranking is
    determined by mapping each player to the ranking corresponding to his
    final card.
    """
    def do_tournament_initialization(self, card_system,
        final_card_rankings, *args, **kwargs):
        self._card_system = tuple(card_system)
        self._final_card_rankings = dict(final_card_rankings)
        self._total_rounds = len(self._card_system)
        self._current_cards = {self.players[i] : i
            for i in range(len(self.players))}
    
    @property
    def current_cards(self):
        return self._current_cards.copy()
    
    def current_card_entry(self, player):
        return self._current_cards[player]
    
    def push_results(self, results):
        super(PowerMatchedTournament, self).push_results(results)
        # change the cards
        for game in results:
            if self._current_cards[game[0]] > self._current_cards[game[1]]:
                tmp = self._current_cards[game[1]]
                self._current_cards[game[1]] = self._current_cards[game[0]]
                self._current_cards[game[0]] = tmp
    
    def next_pairing(self):
        current_card_scheme = self._card_system[self.rounds_complete]
        reverse_current_cards = {x[1] : x[0] for x in
            self._current_cards.items()}
        pairs = []
        for match in current_card_scheme:
            pairs.append(frozenset([reverse_current_cards[n] for n in match]))
        return frozenset(pairs)
    
    def ranking(self):
        return {x : self._final_card_rankings[self._current_cards[x]]
            for x in self.players}

def reinstein_power_matching(num_players, num_rounds):
    pairs = []
    number_of_factors_of_two = 0
    tmp = num_players
    while tmp % 2 == 0:
        number_of_factors_of_two += 1
        tmp /= 2
    odd_factor = tmp
    if number_of_factors_of_two == 0:
        raise PlayerParityError
    if num_rounds > number_of_factors_of_two:
        raise NotImpelementedError
    groups_and_records = [{x: 0} for x in range(num_players)]
    rounds_paired = 0
    while (rounds_paired < number_of_factors_of_two and
        rounds_paired < num_rounds):
        #print("Starting pairing for round {0}...".format(rounds_paired + 1))
        #print(groups_and_records)
        new_groups_and_records = []
        current_pairing = []
        while len(groups_and_records) > 0:
            first_group = groups_and_records.pop(0)
            second_group = groups_and_records.pop()
            temp_pairs = pair_two_groups(first_group, second_group)
            current_pairing.extend(temp_pairs)
            new_groups_and_records.append(updated_records(temp_pairs, 
                dict(first_group.items() + second_group.items())))
        groups_and_records = new_groups_and_records
        pairs.append(tuple(current_pairing))
        rounds_paired += 1
    # Step 2, if m > 1, pair one more round (if needed)
    if rounds_paired < num_rounds and odd_factor > 1:
        new_groups_and_records = []
        current_pairing = []
        # first pair the triple of groups
        pass
        # then do pairs as before (need to break this out to a separate
        # function)
        pass
    return tuple(pairs)

def pair_two_groups(first_group, second_group):
    pairs = zip([y[0] for y in sorted(first_group.items(),
        key=lambda x:(x[1], x[0]))], 
        [y[0] for y in sorted(second_group.items(),
        key=lambda x:(x[1], -x[0]))])
    return pairs

def updated_records(pairing, combined_groups):
    result = dict()
    for p in pairing:
        if p[0] < p[1]:
            winner = p[0]
            loser = p[1]
        else:
            winner = p[1]
            loser = p[0]
        if combined_groups[winner] == combined_groups[loser]:
            result[winner] = combined_groups[winner] + 2
            result[loser] = combined_groups[loser]
        elif abs(combined_groups[winner] - combined_groups[loser]) >= 3:
            raise NoValidPairingError
        elif abs(combined_groups[winner] - combined_groups[loser]) == 2:
            if combined_groups[winner] % 2 != 0:
                raise NoValidPairingError
            x = (combined_groups[winner] + combined_groups[loser])//2
            result[winner] = x + 1
            result[loser] = x
        else:
            x = combined_groups[winner] + combined_groups[loser]
            if x % 4 == 1:
                x = (x + 1) // 2
            else:
                x = (x - 1) // 2
            result[winner] = x + 2
            result[loser] = x
    return result
