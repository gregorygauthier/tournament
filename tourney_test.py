import tourney
import tourney_sim

def test1():
    players = tourney_sim.get_players()
    t = tourney.RoundRobinPairedTournament(players)
    rounds = len(players) - 1
    tourney_sim.test_harness(t, rounds)

def weight_function(x, y, win_matrix, scores):
    if win_matrix[(x, y)] > 0 or win_matrix[(y, x)] > 0:
        raise tourney.ImpossibleMatch
    else:
        return -abs(scores[x] - scores[y])

def weight_function2(x, y, win_matrix, scores):
    num_previous_matches = win_matrix[(x, y)] + win_matrix[(y, x)]
    repeat_penalty = 0 if num_previous_matches == 0 else (
        2 * num_previous_matches + 1)
    score_penalty = 2 * abs(scores[x] - scores[y])
    return -(repeat_penalty + score_penalty)

def test2():
    
    players = tourney_sim.get_players(96)
    t = tourney.MatchingPairedTournament(players, weight_function2)
    rounds = 20
    
    tourney_sim.test_harness(t, rounds, False, False)

if __name__ == "__main__":
    test2()
