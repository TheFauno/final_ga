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
    TRUCK_STATES = ''
    TRUCK_TYPES = ''
    #arrays de palas
    SHOVEL_0 = []
    SHOVEL_1 = []
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
        conn = Db.Connect(self.cdata)
        self.TRUCK_STATES = conn.getTruckStates()
        self.TRUCK_TYPES = conn.getTruckTypes()
        self.N_TRUCKS = len(self.TRUCK_TYPES)
        conn.disconnect()
        #assign trucks to shovels arrays
        for t in self.TRUCK_STATES:
            i = t[3].split('Pala')
            if (i[1] == '0'):
                self.SHOVEL_0.append(t)
            if (i[1] == '1'):
                self.SHOVEL_1.append(t)

    def createGA(self):
        #N_TRUCKS in system

        ''' [                        c1  c2  c3  c4
            palas                   [0, 1,   2,   2] 
            posicion en cola        [1,  1,  2,   1]
            tiempo estimado llegada [13.00, 13.20, ]
        ]'''

        conn = Db.Connect(self.cdata)
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
        #pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=2500, halloffame=hof, verbose=False)
        #print pop
        return 'hola mundo'

    def InitMatrix(self, container):
        IND = np.zeros((3, self.N_TRUCKS))
        
        for i in range(1, 3):
            for j in range(1, self.N_TRUCKS):
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
                    #for s0 in self.SHOVEL_0:
                    conn = Db.Connect(self.cdata)
                    TruckInfo = conn.getTruckInfo(j)
                    print('resultado')
                    print(TruckInfo)
                    loadRoutes = conn.getRoutesToDestination(TruckInfo[8], IND[0][j])
                    Shovel =  conn.getShovel(IND[i][j])
                    unloadRoutes = conn.getRoutesToDestination(Shovel[1], Shovel[3]) # palax, destino predefinido de la pala
                    TrucksInShovel = []
                    TrucksInUnload = [] #unload porque puede esta en vertedero o chancadora
                    #lllenado de camiones en la pala
                    if IND[0][j] == 0:
                        TrucksInShovel = self.SHOVEL_0
                    if IND[0][j] == 1:
                        TrucksInShovel = self.SHOVEL_1
                    #llenado de camiones en descarga
                    TrucksInUnload = conn.getTrucksInStation(Shovel[3])    
                    unloadStation = conn.getUnloadStation(Shovel[2])
                    conn.disconnect()
                    #tiempo de viaje desde nodo actual hasta meta + la sumatoria de camiones que esperan ser atentidos por la pala destino y camion que esta siendo cargado
                    # mas teimpo de viaje a zona de descarga predefinida por la pala + teimpo de espera de los camiones que se encuentran en la zona de descarga
                    #todo esto para saber cuanto aproximadamente se va a demorar el camion actual "j" en volver al estado C en el que podria solicitar el AG
                    loadSelectedRoute = loadRoutes[random.randint(0, len(loadRoutes))]
                    unloadSelectedRoute = unloadRoutes[random.randint(0, len(unloadRoutes))]
                    #carga
                    ts = 0
                    for tis in TrucksInShovel:
                        if tis[5] == 'Input':
                            #buscar info del tipo camion
                            if tis[2] == self.TRUCK_TYPES[0][0]:
                                ts = ts + (self.TRUCK_TYPES[0][3]) + (self.TRUCK_TYPES[0][4] * Shovel[2])
                            #caso en cola input
                        if tis[5] == 'Processing':
                            #caso siendo atendido
                            ts = ts + (self.TRUCK_TYPES[0][4] * Shovel[2])
                    tLoad = (loadSelectedRoute[3]*TruckInfo[3]) + ts
                    ts = 0
                    #descarga
                    for tiu in TrucksInUnload:
                        if tiu[3] == 'Input':
                            ts = ts + (tiu[4]*unloadStation[2]) + tiu[6]
                            #ts = ts + (self.TRUCK_TYPES[0][3]) + (self.TRUCK_TYPES[0][4] * Shovel[2])
                        if tiu[3] == 'Processing':
                            ts = ts + (tiu[4]*unloadStation[2]) + tiu[6]
                    tUnload = (unloadSelectedRoute[3]*TruckInfo[4]) + ts
                    #resultado para el alelo actual
                    cycleTime = tLoad + tUnload
                    IND[i][j] = cycleTime
        print(IND)
        sys.exit()
        return container(IND)

    def evalMin(self, individual):
        #funcion fitness basada en MTCT
        #debiese considerar camiones que estan cargando y descargando minerales
        '''print 'individuo:'
        print(type(individual))
        print(individual)'''
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