import random
import array
import numpy
import sys
from deap import base, creator, tools, algorithms

class Test:

    def cxTwoPointCopy(self, ind1, ind2):
        """Execute a two points crossover with copy on the input individuals. The
        copy is required because the slicing in numpy returns a view of the data,
        which leads to a self overwritting in the swap operation. It prevents
        ::
        
            >>> import numpy
            >>> a = numpy.array((1,2,3,4))
            >>> b = numpy.array((5.6.7.8))
            >>> a[1:3], b[1:3] = b[1:3], a[1:3]
            >>> print(a)
            [1 6 7 4]
            >>> print(b)
            [5 6 7 8]
        """
        size = len(ind1)
        cxpoint1 = random.randint(1, size)
        cxpoint2 = random.randint(1, size - 1)
        if cxpoint2 >= cxpoint1:
            cxpoint2 += 1
        else: # Swap the two cx points
            cxpoint1, cxpoint2 = cxpoint2, cxpoint1

        ind1[cxpoint1:cxpoint2], ind2[cxpoint1:cxpoint2] \
            = ind2[cxpoint1:cxpoint2].copy(), ind1[cxpoint1:cxpoint2].copy()
            
        return ind1, ind2

    def main(self):

        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        #creator.create("Individual", array.array, typecode='b', fitness=creator.FitnessMax)
        creator.create("Individual", numpy.ndarray, fitness=creator.FitnessMax)
        toolbox = base.Toolbox()

        # Attribute generator
        toolbox.register("attr_bool", random.randint, 0, 1)

        # Structure initializers
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, 100)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        def evalOneMax(individual):
            return sum(individual),

        toolbox.register("evaluate", evalOneMax)
        toolbox.register("mate", self.cxTwoPointCopy)
        toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
        toolbox.register("select", tools.selTournament, tournsize=3)

        random.seed(64)
        
        pop = toolbox.population(n=300)
        #hof = tools.HallOfFame(1)
        hof = tools.HallOfFame(1, similar=numpy.array_equal)
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", numpy.mean)
        stats.register("std", numpy.std)
        stats.register("min", numpy.min)
        stats.register("max", numpy.max)
        
        pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=40, stats=stats, halloffame=hof, verbose=True)
        return 'hola'
        #return pop, log, hof