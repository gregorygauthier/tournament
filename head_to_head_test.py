from __future__ import division
import tourney
import random
import argparse

DEFAULT_NUM_PLAYERS = 6
DEFAULT_NUM_TRIALS = 100000

class PlayerWithAbility(object):
    def __init__(self, name, ability):
        self._name = name
        self._ability = ability
    
    def __init__(self, name):
        self._name = name
        self._ability = random.gauss(0, 1)
    
    @property
    def name(self):
        return self._name
    
    @property
    def ability(self):
        return self._ability

def simulate_round(pairs):
    results = [list(pair) for pair in pairs]
    for r in results:
        noise = random.gauss(0, 1)
        if r[0].ability + noise < r[1].ability:
            r.reverse()
    return results

def main(num_players, num_trials):
    NUM_PLAYERS = num_players
    NUM_TRIALS = num_trials
    num_head_to_head_successes = 0
    num_head_to_head_failures = 0
    num_not_head_to_head_tie = 0
    assert(NUM_PLAYERS % 2 == 0)
    PLAYER_NAMES_LIST = ['Andrea', 'Barry', 'Chantal', 'Dorian', 'Erin',
        'Fernand', 'Gabrielle', 'Humberto', 'Ingrid', 'Jerry', 'Karen',
        'Lorenzo', 'Melissa', 'Nestor', 'Olga', 'Pablo', 'Rebekah',
        'Sebastien', 'Tanya', 'Van']
    for trial_number in range(NUM_TRIALS):
        players = [PlayerWithAbility(name)
            for name in PLAYER_NAMES_LIST[0:NUM_PLAYERS]]
        t = tourney.RoundRobinPairedTournament(players)
        NUM_ROUNDS = NUM_PLAYERS - 1
        for r in range(1, NUM_ROUNDS + 1):
            results = simulate_round(t.next_pairing())
            t.push_results(results)
        st = t.score_table
        high_score = max(st.values())
        tied_top_players = filter(lambda x:st[x] == high_score, players)
        #print(tied_top_players)
        if len(tied_top_players) != 2:
            num_not_head_to_head_tie += 1
            continue
        tied_top_players.sort(key=lambda x:-x.ability)
        if t.win_matrix_entry(*tied_top_players) == 1:
            num_head_to_head_successes += 1
        elif t.win_matrix_entry(*reversed(tied_top_players)) == 1:
            num_head_to_head_failures += 1
        else:
            print("This isn't supposed to happen!")
    print("Number of players         : {0:7d}".format(NUM_PLAYERS))
    print("Total trials              : {0:7d}".format(NUM_TRIALS))
    print("Trials with 2 tied leaders: {0:7d}".format(
        num_head_to_head_successes + num_head_to_head_failures))
    print("Head-to-head successes    : {0:7d}".format(
        num_head_to_head_successes))
    print("Head-to-head failures     : {0:7d}".format(
        num_head_to_head_failures))
    print("Success percentage        : {0:7.4f}".format(
        num_head_to_head_successes / (num_head_to_head_successes +
        num_head_to_head_failures) * 100))
    std_dev = 0.5 * (num_head_to_head_successes +
        num_head_to_head_failures)**0.5
    z_score = (num_head_to_head_successes - num_head_to_head_failures) / (2 *
        std_dev)
    print("z-score                   :{0:8.4f}".format(z_score))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Run a head-to-head round-robin test')
    parser.add_argument('--players', type=int, dest='num_players', # nargs='?',
        default=DEFAULT_NUM_PLAYERS, help='the number of players, up to 20')
    parser.add_argument('--trials', type=int, dest='num_teams', # nargs='?',
        default=DEFAULT_NUM_TRIALS, help='the number of trials')
    args = parser.parse_args()
    main(args.num_players, args.num_teams)
