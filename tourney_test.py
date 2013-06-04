from __future__ import division
import tourney
import tourney_sim

def test1():
    players = tourney_sim.get_players()
    t = tourney.RoundRobinPairedTournament(players)
    rounds = len(players) - 1
    tourney_sim.test_harness(t, rounds)

def weight_function(t, x, y):
    if t.win_matrix[(x, y)] > 0 or t.win_matrix[(y, x)] > 0:
        raise tourney.ImpossibleMatch
    else:
        return -abs(t.score_table[x] - t.score_table[y])

def weight_function2(t, x, y):
    num_previous_matches = t.win_matrix[(x, y)] + t.win_matrix[(y, x)]
    repeat_penalty = 0 if num_previous_matches == 0 else (
        2 * num_previous_matches + 1)
    score_penalty = 2 * abs(t.score_table[x] - t.score_table[y])
    return -(repeat_penalty + score_penalty)

def test2():
    
    players = tourney_sim.get_players(20)
    t = tourney.MatchingPairedTournament(players, weight_function2)
    rounds = 19
    
    tourney_sim.test_harness(t, rounds, True, True)

def test3():
    NUM_TRIALS = 1000
    PLAYERS = 20
    ROUNDS = 19
    ranks = {x : [] for x in ('round_robin', 'random_swiss', 'matching')}
    for trial in range(NUM_TRIALS):
        players = tourney_sim.get_players(PLAYERS)
        t = tourney.RoundRobinPairedTournament(players)
        ranks['round_robin'].append(
            tourney_sim.test_harness(t, ROUNDS, verbose=False)[
            'rank_coefficient'])
    
    for trial in range(NUM_TRIALS):
        players = tourney_sim.get_players(PLAYERS)
        t = tourney.RandomSwissPairedTournamentWithRepeats(players)
        ranks['random_swiss'].append(
            tourney_sim.test_harness(t, ROUNDS, verbose=False)[
            'rank_coefficient'])
    
    for trial in range(NUM_TRIALS):
        players = tourney_sim.get_players(PLAYERS)
        t = tourney.MatchingPairedTournament(players, weight_function2)
        ranks['matching'].append(
            tourney_sim.test_harness(t, ROUNDS, verbose=False)[
            'rank_coefficient'])
    
    #print(ranks['round_robin'])
    #print(ranks['random_swiss'])
    #print(ranks['matching'])
    
    means = {x : sum(ranks[x])/len(ranks[x]) for x in
        ('round_robin', 'random_swiss', 'matching')}
    
    sample_stds = {x : sum([(y - means[x])**2 for y in ranks[x]])/
        (len(ranks[x]) - 1)
        for x in ('round_robin', 'random_swiss', 'matching')}
    
    print('   Method      Mean   Std.Dev.')
    print('------------ -------- --------')
    print('Round robin  {0:0.6f} {1:0.6f}'.format(means['round_robin'],
        sample_stds['round_robin']))
    print('Random Swiss {0:0.6f} {1:0.6f}'.format(means['random_swiss'],
        sample_stds['random_swiss']))
    print('Matching     {0:0.6f} {1:0.6f}'.format(means['matching'],
        sample_stds['matching']))

if __name__ == "__main__":
    test2()
