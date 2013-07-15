from __future__ import division
import random
import tourney
import itertools
import scipy.stats

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

def print_pairing(pairing, t=None):
    print("Pairing")
    print("=======")
    for pair in pairing:
        if not t:
            print("{0:10} v. {1:10}".format(*[p.name for p in pair]))
        else:
            args = []
            for p in pair:
                args.extend([p.name, t.score_table_entry(p)])
            print("{0:10} [{1:2d}] v. {2:10} [{3:2d}]".format(*args))

def print_results(results):
    print("Results")
    print("=======")
    for match in results:
        print("{0:10} beat {1:10}".format(*[p.name for p in match]))

def print_score_table(t, print_scoreboard=False):
    print("Score table")
    print("===========")
    if not print_scoreboard:
        print("   Name    Ability   Score  ")
        print("---------- ------- ---------")
    else:
        print("   Name    Ability   Score   Results")
        print("---------- ------- --------- -------")
    rkg = t.ranking()
    for v, k in sorted(zip(rkg.values(), rkg.keys()),
        key=lambda x:(-x[0], x[1])):
        if not print_scoreboard:
            print("{0:10} {1:7.4f} {2:9.5f}".format(
                k.name, k.ability, v))
        else:
            result_string = ""
            for r in t.scoreboard:
                matches = filter(lambda x:k in x, r)
                if len(matches) == 0:
                    result_string += "."
                    continue
                m = filter(lambda x:k in x, r)[0]
                if m[0] == k:
                    result_string += m[1].name[0].upper()
                else:
                    result_string += m[0].name[0].lower()
            print("{0:10} {1:7.4f} {2:9.5f} {3}".format(
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

def compute_spearman_rank_coefficient(t):
    rkg = t.ranking()
    pairs = sorted([(x, rkg[x]) for x in t.players], key=lambda x:-x[1])
    abilities = [x[0].ability for x in pairs]
    rank_keys = [x[1] for x in pairs]
    ability_ranks = rank_list(abilities)
    ranks = rank_list(rank_keys)
    # compute the spearman (defeats tank) coefficient
    return spearman(ability_ranks, ranks)

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

def compute_closeness_value(t):
    total = 0.0
    for pair in itertools.combinations(t.players, 2):
        total += (t.win_matrix_entry(pair[0], pair[1]) +
            t.win_matrix_entry(pair[1], pair[0])) * (
            pair[0].ability - pair[1].ability)**2
    return total

def compute_match_information(t):
    # See Glickman and Jensen 2005
    total = 0.0
    for pair in itertools.combinations(t.players, 2):
        p = scipy.stats.norm.cdf(pair[0].ability - pair[1].ability)
        total += (t.win_matrix_entry(pair[0], pair[1]) +
            t.win_matrix_entry(pair[1], pair[0])) * (
            p * (1-p))
    return total

def compute_win_share(t):
    # 1/n if the top ability player finishes tied for 1st with n players
    # 0 otherwise
    #players = t.players
    #best_player = players[0]
    #for p in players[1:]:
    #    if p.ability > best_player.ability:
    #        best_player = p
    players = t.players
    best_player = [p for p in players if p.ability ==
        max([q.ability for q in players])][0]
    # this may not be well-defined if we have floating-point problems, but
    # it will have to do for now
    ranking = t.ranking()
    highest_ranked_players = [p for p in players if ranking[p] ==
        max([ranking[q] for q in players])]
    if best_player in highest_ranked_players:
        return 1.0/len(highest_ranked_players)
    else:
        return 0.0

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
            print_pairing(pairs, t)
        results = simulate_round(pairs)
        if verbose:
            print_results(results)
        t.push_results(results)
        if verbose:
            print_score_table(t, print_scoreboard)
    return_dict = {}
    rank_coeff = compute_spearman_rank_coefficient(t)
    return_dict['rank_coefficient'] = rank_coeff
    if verbose:
        print("Rank coefficient (raw scores): {0:7.4f}".format(
            rank_coeff))
    cv = compute_closeness_value(t)
    return_dict['closeness_value'] = cv
    if verbose:
        print("Closeness value: {0:9.4f}".format(cv))
    match_information = compute_match_information(t)
    return_dict['match_information'] = match_information
    if verbose:
        print("Match information: {0:9.4f}".format(match_information))
    win_share = compute_win_share(t)
    return_dict['win_share'] = win_share
    if verbose:
        print("Win share: {0:7.4f}".format(win_share))
    return return_dict
