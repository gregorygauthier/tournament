import random
import itertools
import tourney
import tourney_sim
from deap import base, creator, tools
NUM_PLAYERS = 6
NUM_ROUNDS = 4
POPULATION_SIZE = 3000
NUM_GENERATIONS = 100
REDUCTION_FACTOR = 3
FITNESS_SAMPLE_SIZE = 25

def random_permutation(n):
    r = range(n)
    random.shuffle(r)
    return r

toolbox = base.Toolbox()
toolbox.register("attribute", lambda: random_permutation(NUM_PLAYERS))
toolbox.register("individual", tools.initRepeat, list, toolbox.attribute,
    n=NUM_ROUNDS + 1)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def mate(x, y):
    for x_attr, y_attr in zip(x, y):
        tools.cxPartialyMatched(x_attr, y_attr)

def mutate(x, indpb):
    for x_attr in x:
        tools.mutShuffleIndexes(x_attr, indpb)

def evaluation_function(x):
    card_system = []
    for r in x[:-1]:
        card_system.append(tuple(zip(r[::2], r[1::2])))
    card_system = tuple(card_system)
    final_card_rankings = {a: -i for (a, i) in enumerate(x[-1])}
    total_rank_coefficient = 0.0
    for trial in range(FITNESS_SAMPLE_SIZE):
        players = tourney_sim.get_players(NUM_PLAYERS)
        t = tourney.PowerMatchedTournament(players, card_system=card_system,
            final_card_rankings=final_card_rankings)
        total_rank_coefficient += tourney_sim.test_harness(
            t, NUM_ROUNDS, False)['rank_coefficient']
    return total_rank_coefficient

def selection_function(pop, k):
    fitnesses = []
    for p in pop:
        fitnesses.append((p, evaluation_function(p)))
    random.shuffle(fitnesses)
    return [y[0] for y in sorted(fitnesses, key=lambda x:-x[1])[:k]]

#toolbox.register("evaluate", evaluation_function)
toolbox.register("mate", mate)
toolbox.register("mutate", mutate, indpb=0.1)
toolbox.register("select", selection_function,
    k=POPULATION_SIZE // REDUCTION_FACTOR)

def print_generation(pop):
    histogram = {}
    for p in pop:
        histogram[p] = histogram.get(p, 0) + 1
    
    max_individual_size = max(histogram.values())
    quota = min(len(pop) // 200, max_individual_size // 2)
    
    for key, value in sorted(filter(lambda x: x[1] >= quota,
        histogram.items()), key=lambda x:(-x[1], x[0])):
        print("{0:50}: {1:4}".format(str(key), histogram[key]))

def tupleize(p):
    result = []
    for r in p[:-1]:
        r_paired = zip(r[::2], r[1::2])
        r_paired = [tuple(sorted(x)) for x in r_paired]
        result.append(tuple(sorted(r_paired)))
    result.append(tuple(p[-1]))
    return tuple(result)

def main():
    CROSSOVER_PROBABILITY = 0.5
    MUTATION_PROBABILITY = 0.2
    pop = toolbox.population(n=POPULATION_SIZE)
    
    for generation in range(1, NUM_GENERATIONS + 1):
        print("Starting generation {}".format(generation))
        offspring = toolbox.select(pop)
        tmp = offspring[:]
        for i in range(1, REDUCTION_FACTOR):
            tmp.extend([[y[:] for y in x] for x in offspring])
        
        offspring = tmp
        
        for x, y in zip(offspring[::2], offspring[1::2]):
            if random.random() < CROSSOVER_PROBABILITY:
                toolbox.mate(x, y)
        
        for x in offspring:
            if random.random() < MUTATION_PROBABILITY:
                toolbox.mutate(x)
        
        pop[:] = offspring
        print_generation([tupleize(p) for p in pop])

if __name__ == "__main__":
    main()
