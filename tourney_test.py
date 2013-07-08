from __future__ import division
import tourney
import tourney_sim
import math
import multiprocessing

def test1():
    players = tourney_sim.get_players()
    t = tourney.RoundRobinPairedTournament(players)
    rounds = (len(players) - 1)
    tourney_sim.test_harness(t, rounds)

def weight_function(t, x, y):
    if t.win_matrix_entry(x, y) > 0 or t.win_matrix_entry(y, x) > 0:
        raise tourney.ImpossibleMatch
    else:
        return -abs(t.score_table[x] - t.score_table[y])

def weight_function2(t, x, y):
    num_previous_matches = t.win_matrix[(x, y)] + t.win_matrix[(y, x)]
    repeat_penalty = 0 if num_previous_matches == 0 else (
        2 * num_previous_matches + 1)
    score_penalty = 2 * abs(t.score_table[x] - t.score_table[y])
    return -(repeat_penalty + score_penalty)

def weight_function3(t, x, y):
    num_previous_matches = t.win_matrix_entry(x, y) + t.win_matrix_entry(y, x)
    repeat_divisor = 1 << num_previous_matches
    rx = t.modified_bradley_terry_ratings(x)
    ry = t.modified_bradley_terry_ratings(y)
    score = (rx * ry) / ((rx + ry)**2)
    return score/repeat_divisor

def weight_function4(t, x, y):
    alpha = 1
    num_previous_matches = t.win_matrix_entry(x, y) + t.win_matrix_entry(y, x)
    rx = t.modified_bradley_terry_ratings(x)
    ry = t.modified_bradley_terry_ratings(y)
    return (math.log(rx) + math.log(ry) - 2 * math.log(rx + ry) -
        alpha * num_previous_matches)

def weight_function5(t, x, y):
    alpha = 0.5
    num_previous_matches = t.win_matrix_entry(x, y) + t.win_matrix_entry(y, x)
    rx = t.modified_bradley_terry_ratings(x)
    ry = t.modified_bradley_terry_ratings(y)
    return (1 + alpha * num_previous_matches) * (math.log(rx) + math.log(ry) -
        2 * math.log(rx + ry))

def test2():
    
    players = tourney_sim.get_players(20)
    t = tourney.MatchingPairedTournament(players, weight_function5)
    rounds = 4 * (len(players) - 1)
    
    tourney_sim.test_harness(t, rounds, True, True)

def test3():
    NUM_TRIALS = 500
    PLAYERS = 20
    ROUNDS = 19
    ranks = {x : [] for x in ('round_robin', 'matching1', 'matching2')}
    print("Round robin data")
    print("----------------")
    for trial in range(NUM_TRIALS):
        players = tourney_sim.get_players(PLAYERS)
        t = tourney.RoundRobinPairedTournament(players)
        rc = tourney_sim.test_harness(t, ROUNDS, verbose=False)[
            'rank_coefficient']
        print("{0:8.6f}".format(rc))
        ranks['round_robin'].append(rc)
    
    print("")
    print("Matching 1 data ")
    print("----------------")
    for trial in range(NUM_TRIALS):
        players = tourney_sim.get_players(PLAYERS)
        t = tourney.MatchingPairedTournament(players, weight_function4)
        rc = tourney_sim.test_harness(t, ROUNDS, verbose=False)[
            'rank_coefficient']
        print("{0:8.6f}".format(rc))
        ranks['matching1'].append(rc)
    
    print("")
    print("Matching 2 data ")
    print("----------------")
    for trial in range(NUM_TRIALS):
        players = tourney_sim.get_players(PLAYERS)
        t = tourney.MatchingPairedTournament(players, weight_function5)
        rc = tourney_sim.test_harness(t, ROUNDS, verbose=False)[
            'rank_coefficient']
        print("{0:8.6f}".format(rc))
        ranks['matching2'].append(rc)
    print("")
    print("Summary stats   ")
    print("----------------")
    
    #print(ranks['round_robin'])
    #print(ranks['random_swiss'])
    #print(ranks['matching'])
    
    means = {x : sum(ranks[x])/len(ranks[x]) for x in
        ('round_robin', 'matching1', 'matching2')}
    
    sample_stds = {x : (sum([(y - means[x])**2 for y in ranks[x]])/
        (len(ranks[x]) - 1)) ** 0.5
        for x in ('round_robin', 'matching1', 'matching2')}
    
    print('   Method      Mean   Std.Dev.')
    print('------------ -------- --------')
    print('Round robin  {0:0.6f} {1:0.6f}'.format(means['round_robin'],
        sample_stds['round_robin']))
    print('Matching 1   {0:0.6f} {1:0.6f}'.format(means['matching1'],
        sample_stds['matching1']))
    print('Matching 2   {0:0.6f} {1:0.6f}'.format(means['matching2'],
        sample_stds['matching2']))

#to make this pickleable
def run_test(tup):
    #tup[0] is a tournament, tup[1] is the number of rounds
    return tourney_sim.test_harness(tup[0], tup[1], verbose=False)[
        tup[2]]

def test4(num_trials=10, num_players=20, num_rounds=19,
    test_statistic='rank_coefficient'):
    # A multithreaded test
    player_sets = [tourney_sim.get_players(num_players)
        for x in range(3 * num_trials)]
    tourneys = []
    for i in range(num_trials):
        tourneys.append((tourney.RoundRobinPairedTournament(player_sets[i]),
            num_rounds, test_statistic))
    for i in range(num_trials, 2 * num_trials):
        tourneys.append((tourney.MatchingPairedTournament(player_sets[i],
            weight_function4), num_rounds, test_statistic))
    for i in range(2 * num_trials, 3 * num_trials):
        tourneys.append((tourney.MatchingPairedTournament(player_sets[i],
            weight_function5), num_rounds, test_statistic))
    pool = multiprocessing.Pool(None)
    results = pool.map(run_test, tourneys)
    print('Round Robin,wf4,wf5')
    for i in range(num_trials):
        print(','.join(['{0:0.6f}'.format(results[i + num_trials * x]) for
            x in range(3)]))

if __name__ == "__main__":
    #test4(num_trials=1000)
    #test4(num_trials=1000, num_players=40, num_rounds=39)
    #test2()
    #test4(num_trials=1000, num_players=40, num_rounds=39)
    test4(num_trials=10, num_players=10, num_rounds=9, test_statistic=
        'win_share')
