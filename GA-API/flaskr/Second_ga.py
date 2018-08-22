import Db
import random
import math
import numpy as np
import sys
from deap import base, creator, tools, algorithms

class Second_ga():
    #inicializar parametros
    tCurrent = ''
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
        self.tCurrent = formData['timeNow']
        conn = Db.Connect(self.cdata)
        self.TRUCK_STATES = conn.getTruckStates()
        self.TRUCK_TYPES = conn.getTruckTypes()
        self.N_TRUCKS = conn.getTruckNumber()
        self.N_SHOVELS = conn.getShovelNumber()
        conn.disconnect()
        
        #assign trucks to shovels arrays
        for t in self.TRUCK_STATES:
            if "Pala" in t[3]:
                i = t[3].split('Pala')
                if (i[1] == '0'):
                    self.SHOVEL_0.append(t)
                if (i[1] == '1'):
                    self.SHOVEL_1.append(t)

    def createGA(self):
        conn = Db.Connect(self.cdata)
        #ta = [0] * self.N_TRUCKS
        #res = self.calc_tga(self.SHOVEL_0, self.SHOVEL_1, self.tCurrent)
        #print("res = %s" % res)
        #calcular TA
        ta = self.getTA(conn)
        #AG
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness = creator.FitnessMin)
        #operators
        toolbox = base.Toolbox()
        toolbox.register("individual", self.InitMatrix, creator.Individual, ta) # define individuo
        toolbox.register("population", tools.initRepeat, list, toolbox.individual) #crea la poblacion
        pop = toolbox.population(n=5)
        print(pop)
        sys.exit()
        toolbox.register("evaluate", self.evalMin)

        #toolbox.register("mate", self.cxTwoPoint, candidates)
        #toolbox.register("mutate", self.mutUniformInt, low=1, up=self.N_SHOVELS, indpb=0.05)
        #toolbox.register("select", self..selTournament, tournsize=3)
        #crear poblacion
        
        # Evaluate the entire population
        fitnesses = list(map(toolbox.evaluate, pop))
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit
        conn.disconnect()
        hof = tools.HallOfFame(1)
        #pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=2500, halloffame=hof, verbose=False)
        #print pop
        return 'hola mundo'

    def InitMatrix(self, container, ta):
        shovel = []
        for i in range(1, self.N_TRUCKS):
            shovelassignment = random.randint(0, self.N_SHOVELS-1)
            shovel.append(shovelassignment)
        return container([shovel,ta])

    def evalMin(self, individual):
        conn = Db.Connect(self.cdata)
        #print(individual)
        conn.disconnect()
        #calcular TGA
        return (1.0,)
    
    def getTA(self, conn):
        ta = []
        for i in range(1, self.N_TRUCKS):
            truckstate = self.searchTruckState(i)
            ta.append(self.CalcTa(conn, truckstate))
        return ta

    def CalcTa(self, conn, truckstate):
        #calcta es llamada cada vez que se realiza la evaluacion del individuo
        #shovel assignment sera el numero generado aleatoriamente por el cromosoma del individuo
            #ts[7] == "vc" or ts[7] == "vd" no realizan cambios ya que no son observados
            estimatedarrivaltime = 0
            #si el camion se encuentra en viaje se asigna valor 0
            #print((truckstate[1], truckstate[7]))
            if truckstate:
                if str(truckstate[7]) == "v":
                    print("esta en v")
                    #0 no se puede determinar u observar
                    estimatedarrivaltime = 0

                elif str(truckstate[7]) == "d":
                    print("esta en d")
                    #se encuentra en descarga 
                    unload = conn.getUnloadStation(truckstate[3])
                    deltatime = abs(float(self.tCurrent)-float(truckstate[8].replace(",", ".")))
                    #resultado = (capacidad camion * vel. descarga pala) + tiempo maniobra de camion - (tiempo actual simulacion -> timeNow - tiempo inicio -> tiempo en el que llego a d)
                    estimatedarrivaltime = (truckstate[13] * unload[2]) + truckstate[12] - deltatime

                elif str(truckstate[7]) == "cd":
                    print("esta en cd")
                    unload = conn.getUnloadStation(truckstate[3])
                    trucksinunload = conn.getTrucksInStation(truckstate[3])
                    queuearrivaltime = 0

                    #busca posicion de camion actual en cola y calcula tiempo de descarga de camion que se encuentre descargando
                    for truckinunload in trucksinunload:

                        if truckinunload[3] == "cd":
                            #buscar posicion camion en cola
                            if truckstate[1] == truckinunload[1]:
                                #obtener indice
                                queuearrivaltime = truckinunload[4]

                        elif truckinunload[3] == "d":
                            #usar formula de camion cargando que se encuentra en la estacion de descarga
                            deltatime = abs(float(self.tCurrent) - float(truckinunload[4].replace(",", ".")))
                            estimatedarrivaltime = (truckinunload[9] * unload[2]) + truckinunload[8] - deltatime

                    for truckinunload in trucksinunload:
                        #si el tiempo de llegada del camion que esta en el array es menor o = al tiempo de llegada del camion para calc ta sumar
                        if truckinunload[4] <= queuearrivaltime:
                            deltatime = abs(float(self.tCurrent) - float(truckinunload[4].replace(",", ".")))
                            estimatedarrivaltime = estimatedarrivaltime + (truckinunload[9] * unload[2]) + truckinunload[8] - deltatime

                elif str(truckstate[7]) == "c":
                    print("esta en c")
                    #camion se encuentra cargando: capacidad camion * vel descarga + tiempo maniobra + tiempo actual - tiempo inicial
                    shovel = conn.getShovel(truckstate[3])
                    unloadroutes = conn.getRoutesToDestination(truckstate[3], shovel[3])
                    unload = conn.getUnloadStation(shovel[3])
                    trucksinunload = conn.getTrucksInStation(shovel[3])
                    meanunloadroute = 0
                    queuetime = 0

                    #calcula distancia promedio de rutas hacia descarga
                    for unloadroute in unloadroutes:
                        meanunloadroute = meanunloadroute + unloadroute[3]
                    
                    meanunloadroute = meanunloadroute/len(unloadroutes)

                    #calcula tiempo de espera en descarga
                    for truckinunload in trucksinunload:
                        deltatime = abs(float(self.tCurrent)-float(truckinunload[4].replace(",", ".")))
                        queuetime = queuetime + (truckinunload[12] * unload[2]) + truckinunload[11] - deltatime
                    #resultado = (capacidad camion * vel. descarga pala) + tiempo maniobra de camion + (distancia de viaje * vel camion cargado) + tiempo de camiones que estan en la zona de descarga) 
                    # - (tiempo actual simulacion -> timeNow - tiempo inicio -> tiempo en el que llego a d)
                    estimatedarrivaltime = (truckstate[12] * shovel[2]) + truckstate[11] + (meanunloadroute * truckstate[11]) + queuetime - deltatime

                elif str(truckstate[7]) == "cc":
                    print("esta en cc")
                    #camion se encuentra esperando carga
                    shovel = conn.getShovel(truckstate[3])
                    trucksinshovel = conn.getTrucksInStation(truckstate[3])
                    unloadroutes = conn.getRoutesToDestination(truckstate[3], shovel[3])
                    trucksinunload = conn.getTrucksInStation(shovel[3])

                    meanunloadroute = 0
                    queuearrivaltime = 0
                    queuetime = 0
                    estimatedarrivaltime = 0
                    #calcula tiempos aprox para que el camion salga de la pala
                    for truckinshovel in trucksinshovel:
                        if truckinshovel[3] == "cc":

                            if truckstate[1] == truckinshovel[1]:
                                queuearrivaltime = truckinshovel[4]

                        elif truckinshovel[3] == "c":
                            
                            deltatime = abs(float(self.tCurrent) - float(truckinshovel[4].replace(",", ".")))
                            estimatedarrivaltime = (truckinshovel[9] * shovel[2]) + truckinshovel[8] - deltatime

                    for truckinshovel in trucksinshovel:
                        
                        if truckinshovel[4] <= queuearrivaltime:
                            deltatime = abs(float(self.tCurrent) - float(truckinshovel[4].replace(",", ".")))
                            estimatedarrivaltime = estimatedarrivaltime + (truckinshovel[9] * shovel[2]) + truckinshovel[8] - deltatime

                    #calcula tiempo de viaje estimado y lo adiciona al estimatedarrivaltime
                    for unloadroute in unloadroutes:
                        meanunloadroute = meanunloadroute + unloadroute[3]
                    
                    meanunloadroute = meanunloadroute/len(unloadroutes)

                    #suma tiempos de los camiones que se encuentran en destino (descarga)
                    for truckinunload in trucksinunload:
                        deltatime = abs(float(self.tCurrent) -float(truckinunload[4].replace(",", ".")))
                        queuetime = queuetime + (truckinunload[12] * unload[2]) + truckinunload[11] - deltatime
                    estimatedarrivaltime = estimatedarrivaltime + (truckstate[12] * shovel[2]) + truckstate[11] + (meanunloadroute * truckstate[11]) + queuetime - deltatime

                elif str(truckstate[7]) == "sag":
                    print("esta en sag")
                    #ya se encuentra en el ultimo estado
                    estimatedarrivaltime = 0
                    '''estimatedarrivaltime = 0
                    shovelname = "Pala"+str(shovelassignment)
                    shovel = conn.getShovel(shovelname)
                    #datos obligatorios
                    loadroutes = conn.getRoutesToDestination(truckstate[3], shovelname)
                    trucksinshovel = conn.getTrucksInStation(shovelname)
                    unloadroutes = conn.getRoutesToDestination(shovel[1], shovel[3])
                    unload = conn.getUnloadStation(shovel[3])
                    trucksinunload = conn.getTrucksInStation(shovel[3])                

                    # distancia prom ruta viaje a carga
                    loadmeandistance = 0
                    for loadroute in loadroutes:
                        loadmeandistance = loadmeandistance+ loadroute[3]
                    loadmeandistance = loadmeandistance / len(loadroutes)
                    loadtraveltime = loadmeandistance * truckstate[12]

                    #suma camiones en carga
                    sumtrucksinshovel = 0
                    for truckinshovel in trucksinshovel:
                        deltatime = abs(float(self.tCurrent) -float(truckinshovel[4].replace(",", ".")))
                        sumtrucksinshovel = sumtrucksinshovel + (truckinshovel[9] * shovel[2]) + truckinshovel[8] - deltatime

                    #distancia prom ruta viaje a descarga
                    unloadmeandistance = 0
                    for unloadroute in unloadroutes:
                        unloadmeandistance = unloadmeandistance + unloadroute[3]
                    unloadmeandistance = unloadmeandistance / len(unloadroutes)
                    unloadtraveltime = unloadmeandistance * truckstate[12]

                    #suma camiones en descarga
                    sumtrucksinunload = 0
                    for truckinunload in trucksinunload:
                        deltatime = abs(float(self.tCurrent) -float(truckinunload[4].replace(",", ".")))
                        sumtrucksinunload = sumtrucksinunload + (truckinunload[9] * unload[2]) + truckinunload[8] - deltatime

                    estimatedarrivaltime = loadtraveltime + sumtrucksinshovel + unloadtraveltime + sumtrucksinunload'''
            
            return estimatedarrivaltime

    def calc_tga(self, atl_s0, atl_s1, tCurrent):
        pass
        
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

    def searchTruckState(self, truckid):
        mytruckstate = []
        for truckstate in self.TRUCK_STATES:
            if truckstate[10] == truckid:
                mytruckstate = truckstate
        return mytruckstate