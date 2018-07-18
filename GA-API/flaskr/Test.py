import random
import array
import math
import numpy as np
import sys
from deap import base, creator, tools, algorithms

class Test:

    N_TRUCKS = 6
    N_SHOVELS = 4

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


    def InitMatrix(self, container):
        IND = np.zeros((3, self.N_TRUCKS))
        for i in range(3):
            for j in range(self.N_TRUCKS):
                if i == 0:
                    #row 1: shovels
                    ranValue = np.random.uniform(low= 0, high=self.N_SHOVELS)
                    IND[i][j] = math.floor(ranValue)
                if i == 1:
                    #row 2: queue position
                    #posibilidad de encontrar una posicion de fila entre 1 y cantidad de palas
                    ranValue = np.random.uniform(low= 1, high=self.N_SHOVELS+1)
                    IND[i][j] = math.floor(ranValue)                
                #row 3: estimated arrival time se mantiene con valores generados, aun no se calcularan tiempos estimados
                # hora de simulacion + sumatoria de camiones en una pala
        print(IND)
        return container(IND)


    def main(self):

        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        #creator.create("Individual", array.array, typecode='b', fitness=creator.FitnessMax)
        creator.create("Individual", np.ndarray, fitness=creator.FitnessMax)
        toolbox = base.Toolbox()

        # Attribute generator
        toolbox.register("attr_bool", random.randint, 0, 1)

        # Structure initializers
        toolbox.register("individual", self.InitMatrix, creator.Individual)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        def evalOneMax(individual):
            return sum(individual),

        toolbox.register("evaluate", evalOneMax)
        toolbox.register("mate", self.cxTwoPointCopy)
        toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
        toolbox.register("select", tools.selTournament, tournsize=3)

        #random.seed(64)
        
        pop = toolbox.population(n=300)
        #hof = tools.HallOfFame(1)
        hof = tools.HallOfFame(1, similar=np.array_equal)
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("std", np.std)
        stats.register("min", np.min)
        stats.register("max", np.max)
        print(type(pop))



        #pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=40, stats=stats, halloffame=hof, verbose=True)
        return 'hola'
        #return pop, log, hof