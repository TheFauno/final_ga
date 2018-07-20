import Db
import random
import math
import numpy as np
import sys
from deap import base, creator, tools, algorithms

class Second_ga():
    #inicializar parametros
    timeNow = ''
    N_TRUCKS = 0
    N_SHOVELS = 0
    MIN = 0      # used for minimal quantity from 0 in simulator for shovels and others...
    #connection configuration
    cdata = {
        "host": "localhost",
        "username": "root",
        "password": "",
        "database": "simio"
    }

    def __init__(self, formData):
        #sets actual simulation time
        self.timeNow = formData['timeNow']

    def createGA(self):
        #N_TRUCKS in system

        ''' [                        c1  c2  c3  c4
            palas                   [0, 1,   2,   2] 
            posicion en cola        [1,  1,  2,   1]
            tiempo estimado llegada [13.00, 13.20, ]
        ]'''

        conn = Db.Connect(self.cdata)
        self.truckTypes = conn.getTruckTypes()
        for tt in self.truckTypes:
            self.N_TRUCKS += tt[5]
        #individual structure
        #define fitness function, minimize in this case, weight negative stands for minimizing fitness
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", np.ndarray, fitness = creator.FitnessMin)

        #population config
        toolbox = base.Toolbox()
        #toolbox.register("attr_int", random.randint, self.MIN, self.N_SHOVELS) #cell value type
        toolbox.register("individual", self.InitMatrix, creator.Individual) # define individuo
        toolbox.register("population", tools.initRepeat, list, toolbox.individual) #crea la poblacion
        toolbox.register("evaluate", self.evalMin)
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", tools.mutUniformInt, low=1, up=self.N_SHOVELS, indpb=0.05)
        toolbox.register("select", tools.selTournament, tournsize=3)
        conn.disconnect()
        pop = toolbox.population(n=10)
        hof = tools.HallOfFame(1)
        pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=2500, halloffame=hof, verbose=False)
        print pop
        return 'hola mundo'

    def InitMatrix(self, container):
        IND = np.zeros((3, self.N_TRUCKS))
        conn = Db.Connect(self.cdata)
        truckStates = conn.getTruckStates()
        truckTypes = conn.getTruckTypes()
        conn.disconnect()
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
                if i==2:
                    #row 3: estimated arrival time se mantiene con valores generados, aun no se calcularan tiempos estimados
                    # hora de simulacion + sumatoria de camiones en una pala
                    #observar los estados de todos los camiones
                    #separar por palas
                    #por cada pala ir obeniendo el t_max_s#
                    
        print(IND)
        return container(IND)

    def evalMin(self, individual):
        #funcion fitness basada en MTCT
        #debiese considerar camiones que estan cargando y descargando minerales
        print 'individuo:'
        print(type(individual))
        print(individual)
        return 1
    
    #limpiar memoria
    def clear(self, toolbox):
        #this function purpose is unregister elements in toolbox
        '''toolbox.unregister("attr_int")
        toolbox.unregister("individual")
        toolbox.unregister("population")
        toolbox.unregister("evaluate")
        toolbox.unregister("mate")
        toolbox.unregister("mutate")
        toolbox.unregister("select")'''
        return 'clear'