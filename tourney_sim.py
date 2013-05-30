import random
import tourney

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

def print_pairing(pairing, score_table=None):
    print("Pairing")
    print("=======")
    for pair in pairing:
        if score_table == None:
            print("{0:10} v. {1:10}".format(*[p.name for p in pair]))
        else:
            args = []
            for p in pair:
                args.extend([p.name, score_table[p]])
            print("{0:10} [{1:2d}] v. {2:10} [{3:2d}]".format(*args))

def print_results(results):
    print("Results")
    print("=======")
    for match in results:
        print("{0:10} beat {1:10}".format(*[p.name for p in match]))

def print_score_table(score_table, scoreboard=None):
    print("Score table")
    print("===========")
    if scoreboard == None:
        print("   Name    Ability Score")
        print("---------- ------- -----")
    else:
        print("   Name    Ability Score Results")
        print("---------- ------- ----- -------")
    for v, k in sorted(zip(score_table.values(), score_table.keys()),
        key=lambda x:(-x[0], x[1])):
        if scoreboard == None:
            print("{0:10} {1:7.4f} {2:^5d}".format(
                k.name, k.ability, v))
        else:
            result_string = ""
            for r in scoreboard:
                m = filter(lambda x:k in x, r)[0]
                if m[0] == k:
                    result_string += m[1].name[0].upper()
                else:
                    result_string += m[0].name[0].lower()
            print("{0:10} {1:7.4f} {2:^5d} {3}".format(
                k.name, k.ability, v, result_string))

def rank_list(original_list):
    sorted_list = sorted(original_list)
    ranks = {}
    distinct_elements = sorted(list(set(original_list)))
    seen_elements = 0
    for e in distinct_elements:
        r = seen_elements + 1 + sorted_list.count(e) / 2.0
        ranks[e] = r
        seen_elements += sorted_list.count(e)
    return map(lambda x:ranks[x], original_list)

def compute_spearman_rank_coefficient(score_table):
    st = score_table.items()
    abilities = [x[0].ability for x in st]
    scores = [x[1] for x in st]
    ability_ranks = rank_list(abilities)
    score_ranks = rank_list(scores)
    # compute the spearman (defeats tank) coefficient
    return spearman(ability_ranks, score_ranks)

def spearman(first_rank_list, second_rank_list):
    assert(len(first_rank_list) == len(second_rank_list))
    mean = (len(first_rank_list) + 1) / 2.0
    normed_first_rank_list = [x - mean for x in first_rank_list]
    normed_second_rank_list = [x - mean for x in second_rank_list]
    numerator = sum([x[0] * x[1] for x in zip(normed_first_rank_list,
        normed_second_rank_list)])
    denominator = (sum([x**2 for x in normed_first_rank_list]) *
        sum([x**2 for x in normed_second_rank_list]))**0.5
    return numerator/denominator

def get_players(num_players=20):
    if num_players <= 20:
    # Brought to you by the Atlantic hurricane list, 2013...
        player_names = ['Andrea', 'Barry', 'Chantal', 'Dorian', 'Erin',
        'Fernand', 'Gabrielle', 'Humberto', 'Ingrid', 'Jerry', 'Karen',
        'Lorenzo', 'Melissa', 'Nestor', 'Olga', 'Pablo', 'Rebekah',
        'Sebastien', 'Tanya', 'Van'][:num_players]
    else:
        player_names = [str(x) for x in range(1, num_players + 1)]
    players = []
    for name in player_names:
        players.append(PlayerWithAbility(name))
    return players

def simulate_round(pairs):
    results = [list(pair) for pair in pairs]
    for r in results:
        noise = random.gauss(0, 1)
        if r[0].ability + noise < r[1].ability:
            r.reverse()
    return results

def test_harness(t, rounds, verbose=True, print_scoreboard=True):
    for r in range(1, rounds + 1):
        if verbose:
            print("Starting round {0}".format(r))
        pairs = t.next_pairing()
        if verbose:
            if r > 1:
                print_pairing(pairs, t.score_table)
            else:
                print_pairing(pairs)
        results = simulate_round(pairs)
        if verbose:
            print_results(results)
        t.push_results(results)
        # print the final table anyways
        if verbose or r == rounds:
            if print_scoreboard:
                print_score_table(t.score_table, t.scoreboard)
            else:
                print_score_table(t.score_table)
    print("Rank coefficient (raw scores): {0:7.4f}".format(
        compute_spearman_rank_coefficient(t.score_table)))
