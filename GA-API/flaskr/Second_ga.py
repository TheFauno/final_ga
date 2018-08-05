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
        self.N_TRUCKS = conn.getTruckNumber()
        self.N_SHOVELS = conn.getShovelNumber()
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
        for i in range(0, 3):
            for j in range(1, self.N_TRUCKS):
                if i == 0:
                    #row 1: shovels
                    #ranValue = np.random.uniform(low= 0, high=self.N_SHOVELS)
                    ranValue = random.randint(0, self.N_SHOVELS-1)
                    IND[i][j] = ranValue
                    #IND[i][j] = math.floor(ranValue) # cambiar funcion de aproximacion
                if i == 1:
                    #row 2: queue position
                    #posibilidad de encontrar una posicion de fila entre 1 y cantidad de palas
                    ranValue = np.random.uniform(low= 1, high=self.N_SHOVELS+1)
                    IND[i][j] = math.floor(ranValue)
                if i==2:
                    conn = Db.Connect(self.cdata)
                    TruckInfo = conn.getTruckInfo(j)
                    loadRoutes = []
                    unloadRoutes = []
                    tLoad = 0
                    tUnload = 0
                    cycleTime = 0
                    #situacion detectata: el camion observado puede encontrarse en una pala o chancadora, por lo que  loadRoutes y unloadRoutes pueden verse afectadas
                    #para resolver esto se agregaran clausulas condicionales basicas
                    #no se considerearan los camiones que no se encuentran en algun buffer sea de carga o descarga.
                    Shovel =  conn.getShovel("Pala"+str(int(IND[0][j])))
                    TrucksInUnload = conn.getTrucksInStation(Shovel[3])
                    unloadStation = conn.getUnloadStation(Shovel[2])
                    if IND[0][j] == 0:
                            TrucksInShovel = self.SHOVEL_0
                    if IND[0][j] == 1:
                        TrucksInShovel = self.SHOVEL_1
                    #si la posicion actual es una pala, busca rutas de descarga, sino(osea se encuentra en una zona de descarga) solo calcula tiempo de espera restante para vovler al estado c
                    if TruckInfo[8].find("Pala") == 0:
                        #el camion se encuentra en algun lugar de la pala, se buscan las rutas posibles desde la pala hacia la zona de descarga establecida por la pala
                        unloadRoutes = conn.getRoutesToDestination(TruckInfo[8], Shovel[3]) # palax, destino predefinido de la pala
                        #loadRoutes = conn.getRoutesToDestination(Shovel[3], "Pala"+str(IND[0][j])) #######no trae nada esta wea arreglar    
                        #parte nueva
                        
                        #sumar tiempo restante en ser cargado, tomando los valores por defecto que tiene cada camion (pensando siempre que recien comenzaron)
                        #consultar si puede hacerse asi
                        inProcessing = False
                        flowid = 0 # almacena el id que trae el flujo de una pala correspondiente al camion sobre el que se calcula el tiempo estimado de llegada
                        ts = 0
                        path = 0
                        for tis in TrucksInShovel:
                            if tis[5] == "Processing" and tis[1] == TruckInfo[1]:
                                inProcessing = True
                                #solo suma el actual = maniobra+ (capacidad*tiempo carga) mejorar falta cuanti carga por palada
                                if len(unloadRoutes) > 1 :
                                    path = random.randint(0, len(unloadRoutes))
                                ts = TruckInfo[5]+(TruckInfo[6]*Shovel[2]) + (TruckInfo[5]*unloadRoutes[path][3])

                            elif tis[5] == "Input" and tis[1] == TruckInfo[1]:
                                flowid = tis[0]

                        if not inProcessing:
                            ProcessingTruck = []
                            for tis in TrucksInShovel:
                                if tis[0] <= flowid and tis[5] == "Input":                                    
                                    ts = ts + TruckInfo[5]+(TruckInfo[6]*Shovel[2]) + (TruckInfo[5]*unloadRoutes[path][3])
                                if tis[5] == "Processing":
                                    ProcessingTruck = tis

                            ProcessingTruckInfo = conn.getTruckCapacity(ProcessingTruck[2])
                            ts = ts + (ProcessingTruckInfo[4]*Shovel[2])+ ProcessingTruckInfo[3]
                        
                        #se suman los camiones que se encuentran en la zona de descarga (se toma en cuenta los camiones que se encuentran actualmente no los que llegaran en el tiempo ts)
                        #obtener camiones en zona de descarga asociada a la pala en la que se encuentra el camion j
                        # se suman los ts = trucks in shovel ?  time con los camiones en descarga y la ruta
                        tu = 0
                        flowid = 0
                        for tiu in TrucksInUnload:
                            if tiu[3] == "Processing":
                                tu = (TruckInfo[3]*TruckInfo[6]) + TruckInfo[5]
                            elif tiu[5] == "Input":
                                flowid = tiu[0]
                        print "Camiones en descarga %s" % TrucksInUnload #viene vacio  porque no hay datos en la tabla aun
                        for tiu in TrucksInUnload:
                            if tiu[3] == "Input" and tiu[0] <= flowid:
                                tu = tu + tiu[7] + (tiu[8] * unloadStation[2])
                                #tiempo manionbra + (tiempo descarga) + (tiempo de espera segun posicion del camion actual)
                        cycleTime = tu + ts

                    elif TruckInfo[8].find("Path") != 0:
                        #buscar posicion en input flowid en donde se encuentra el camion
                        unloadStation = conn.getUnloadStation(TruckInfo[8])
                        tu = 0
                        flowid = 0
                        inProcessing = False
                        for tiu in TrucksInUnload:
                            if tiu[5] == "Processing" and tiu[1] == TruckInfo[1]:
                                inProcessing = True
                                tu = (TruckInfo[3]*TruckInfo[6]) + TruckInfo[5]
                            elif tiu[5] == "Input" and tiu[1] == TruckInfo[1]:
                                flowid = tiu[0]

                        if not inProcessing:
                            ProcessingTruck = []
                            for tiu in TrucksInShovel:
                                if tiu[0] <= flowid and tiu[5] == "Input":                                    
                                    tu = tu + TruckInfo[5]+(TruckInfo[6]*unloadStation[2])
                                if tiu[5] == "Processing":
                                    ProcessingTruck = tiu
                            if (ProcessingTruck):
                                ProcessingTruckInfo = conn.getTruckCapacity(ProcessingTruck[2])
                                tu = tu + (ProcessingTruckInfo[4]*unloadStation[2])+ ProcessingTruckInfo[3]
#                        tu = tu + (ProcessingTruckInfo[4]*unloadStation[2])+ ProcessingTruckInfo[3]
                        cycleTime = tu
                    #resultado para el alelo actual (si no se encontro una ruta el tiempo de ciclo sera 0)
                    IND[i][j] = cycleTime
        #print(IND)
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