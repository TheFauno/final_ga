import Db
import random
import numpy
from deap import base, creator, tools, algorithms

class First_ga():

    #valores globales
    MIN = 0      # used for minimal quantity from 0 in simulator for shovels and others...
    N_SHOVELS = 1 # como en el modelo de prueba de simio
    N_TRUCKS = 0  # 6 camiones leidos desde la BD
    POP_SIZE = 10  # poblacion inicial aleatoria
    CXPB = 0.3
    MUTPB = 0.1
    GENERATION_SIZE = 500
    timeNow = '' #tiempo del simulador
    #ubicacion inicial se lee desde una variable global de la simulacion, se recibe desde el step c#
    #sys....
    home = ''
    truckTypes = {}
    #connection configuration
    cdata = {
        "host": "localhost",
        "username": "root",
        "password": "",
        "database": "simio"
    }

    def __init__(self, formData):
        self.timeNow = formData['timeNow']

    def createGA(self):
        #individual structure
        #define fitness function, minimize in this case, weight negative stands for minimizing fitness
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness = creator.FitnessMin)
        #trucks to create (6 in this test)
        conn = Db.Connect(self.cdata)
        self.truckTypes = conn.getTruckTypes()
        for tt in self.truckTypes:
            self.N_TRUCKS += tt[5]

        #population config
        toolbox = base.Toolbox()
        toolbox.register("attr_int", random.randint, self.MIN, self.N_SHOVELS) # define los tipos de un individuo
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_int, self.N_TRUCKS) # define individuo
        toolbox.register("population", tools.initRepeat, list, toolbox.individual) #crea la poblacion

        toolbox.register("evaluate", self.evalMin)
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", tools.mutUniformInt, low=1, up=self.N_SHOVELS, indpb=0.05)
        toolbox.register("select", tools.selTournament, tournsize=3)

        conn.disconnect()

        pop = toolbox.population(n=100)

        hof = tools.HallOfFame(1)
        
        '''stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", numpy.mean)
        stats.register("sum", numpy.sum)
        stats.register("std", numpy.std)
        stats.register("min", numpy.min)
        stats.register("max", numpy.max)'''

        #pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=10, stats=stats, halloffame=hof, verbose=False)
        pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=2500, halloffame=hof, verbose=False)
        
        #print("best solution")
        #print(hof[0])
        bestSolution = hof[0]
        
        conn = Db.Connect(self.cdata)
        conn.truncGAInit()
        #en esta linea insertar el tiempo estimado de llegada 
        #obtenido de hof[0].fitness.values
        print(self.timeNow)
        for row in bestSolution:
            conn.insertGA(row)            
        conn.disconnect()
        #clear toolbox for next ussage of deap
        self.clear(toolbox) 
        return bestSolution
        #return pop, log, hof

    #funcion de evaluacion

    def evalMin(self, individual):
        mtct = list()
        #por cada gen del individuo (camion en posicion 0 del array o lista)
        for truck, shovel in enumerate(individual):
            tType = "" #truck type
            mTime = "" #tiempo maniobra
            #1. que tipo de camion es?  y tiempo de maniobra      
            if 0 <= truck <= self.truckTypes[0][5]-1:
                tType = self.truckTypes[0][0]
                mTime = self.truckTypes[0][3]
                truckEmptySpeed = self.truckTypes[0][1]
            if self.truckTypes[0][5] <= truck <= self.truckTypes[0][5]+self.truckTypes[1][5]-1:
                tType = self.truckTypes[1][0]
                mTime = self.truckTypes[1][3]
                truckEmptySpeed = self.truckTypes[1][1]
            if truck == self.truckTypes[0][5]+self.truckTypes[1][5]+self.truckTypes[2][5]-1:
                tType = self.truckTypes[2][0]
                mTime = self.truckTypes[2][3]
                truckEmptySpeed = self.truckTypes[1][1]

            #3. tiempo carga = ton/min x capacidad camion

            #obtener posicion en mapa gen (camion) actual -> se obtiene al comienzo por c# var home
            #obtener posibles rutas hasta el destino
            conn = Db.Connect(self.cdata)
            #cambiar a ingles todo al final
            destinationNode = str('Pala'+str(shovel))      
            routesToDestination =  conn.getRoutesToDestination(self.home, destinationNode)
            conn.disconnect()
            route = random.choice(routesToDestination)
            distance = route[3]
            estimatedTravelTime = distance * truckEmptySpeed
            #obtener tiempo espera estimado en cola (para ello consultar camiones que se encuentran en la cola y el tiempo estimado de los que se encuentran camino al mismo destino)
            conn = Db.Connect(self.cdata)
            #buscar cuantos y que tipos de camion se encuentran en cola
            TrucksInShovel =  conn.getTrucksInShovel(destinationNode)
            #buscar si hay un camion que esta siendo cargado
            inputTrucksWaitTime = 0
            processingTruckLoadTime = 0
            totalWaitingTime = 0
            shovelData = conn.getShovel(destinationNode)
            
            #calcular tiempo aproximado espera antes de que el camion comience a ser cargado por la pala
            if len(TrucksInShovel) > 0:
                for truck in TrucksInShovel:
                    truckCapacity = conn.getTruckCapacity(truck[2])
                    if truck[5] == 'Processing':
                        #tiempo carga = tiempo carga pala x espacio disponible camion
                        processingTruckLoadTime = (shovelData[2] * truckCapacity)
                    elif truck[5] == 'Input':
                        #sumar tiempo carga sgte camion 
                        inputTrucksWaitTime = inputTrucksWaitTime + shovelData[0][2] * truckCapacity[4] + mTime
                #tiempo carga camion processing + tiempo carga camion input
                totalWaitingTime = processingTruckLoadTime + inputTrucksWaitTime 
            conn.disconnect()
            #obtener tiempo carga
            #lista de mtct en i0 guardar:
            #tiempo de ciclo estimado (tiempo de viaje) + tiempo espera estimado en cola + tiempo maniobra + tiempo carga + hora en simulador
            estimatedcycletime = mTime + estimatedTravelTime + totalWaitingTime #verificar unidades
            mtct.append(estimatedcycletime)
        #resultado mtct individuo actual
        mctc1 = list()
        mctc1.append(sum(mtct))
        return mctc1 #suma todos los elementos de la lista devolver como iterable

    def clear(self, toolbox):
        #this function purpose is unregister elements in toolbox
        toolbox.unregister("attr_int")
        toolbox.unregister("individual")
        toolbox.unregister("population")
        toolbox.unregister("evaluate")
        toolbox.unregister("mate")
        toolbox.unregister("mutate")
        toolbox.unregister("select")