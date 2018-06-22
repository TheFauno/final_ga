import sys
import Db
import random
import numpy
from deap import base, creator, tools, algorithms

MIN = 0      # used for minimal quantity 1 for shovels and others...
N_SHOVELS = 1 # como en el modelo de prueba de simio
N_TRUCKS = 0  # 6 camiones leidos desde la BD
POP_SIZE = 10  # poblacion inicial aleatoria
CXPB = 0.3
MUTPB = 0.1
GENERATION_SIZE = 500
#ubicacion inicial se lee desde una variable global de la simulacion, se recibe desde el step c#
#sys....
home = ""

#FUNCTIONS

def evalMin(individual):
    mtct = list()
    #por cada gen del individuo (camion en posicion 0 del array o lista)
    for truck, shovel in enumerate(individual):
        tType = "" #truck type
        mTime = "" #tiempo maniobra
        #1. que tipo de camion es?  y tiempo de maniobra      
        if 0 <= truck <= truckTypes[0][5]-1:
            tType = truckTypes[0][0]
            mTime = truckTypes[0][3]
            truckEmptySpeed = truckTypes[0][1]
        if truckTypes[0][5] <= truck <= truckTypes[0][5]+truckTypes[1][5]-1:
            tType = truckTypes[1][0]
            mTime = truckTypes[1][3]
            truckEmptySpeed = truckTypes[1][1]
        if truck == truckTypes[0][5]+truckTypes[1][5]+truckTypes[2][5]-1:
            tType = truckTypes[2][0]
            mTime = truckTypes[2][3]
            truckEmptySpeed = truckTypes[1][1]

        #3. tiempo carga = ton/min x capacidad camion

        #obtener posicion en mapa gen (camion) actual -> se obtiene al comienzo por c# var home
        #obtener posibles rutas hasta el destino
        conn = Db.Connect(cdata)
        #cambiar a ingles todo al final
        destinationNode = str('Pala'+str(shovel))        
        routesToDestination =  conn.getRoutesToDestination(home, destinationNode)
        conn.disconnect()
        route = random.choice(routesToDestination)
        distance = route[3]
        estimatedTravelTime = distance * truckEmptySpeed
        #obtener tiempo espera estimado en cola (para ello consultar camiones que se encuentran en la cola y el tiempo estimado de los que se encuentran camino al mismo destino)
        conn = Db.Connect(cdata)
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
        #tiempo de ciclo estimado (tiempo de viaje) + tiempo espera estimado en cola + tiempo maniobra + tiempo carga
        estimatedcycletime = mTime + estimatedTravelTime + totalWaitingTime
        mtct.append(estimatedcycletime)
    #resultado mtct individuo actual
    mctc1 = list()
    mctc1.append(sum(mtct))
    return mctc1 #suma todos los elementos de la lista devolver como iterable

#connection configuration
cdata = {
    "host": "localhost",
    "username": "root",
    "password": "",
    "database": "simio"
}
#individual structure
#define fitness function, minimize in this case, weight negative stands for minimizing fitness
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness = creator.FitnessMin)

#trucks to create (6 in this test)
conn = Db.Connect(cdata)
truckTypes = conn.getTruckTypes()
for tt in truckTypes:
    N_TRUCKS += tt[5]

#population config
toolbox = base.Toolbox()
toolbox.register("attr_int", random.randint, MIN, N_SHOVELS) # define los tipos de un individuo
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_int, N_TRUCKS) # define individuo
toolbox.register("population", tools.initRepeat, list, toolbox.individual) #crea la poblacion

toolbox.register("evaluate", evalMin)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutUniformInt, low=1, up=N_SHOVELS, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)

conn.disconnect()

#MAIN

def main():

    pop = toolbox.population(n=10)
    hof = tools.HallOfFame(1)
    
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("sum", numpy.sum)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=10, stats=stats, halloffame=hof, verbose=False)
    
    print("best solution")
    print(hof[0])
    return pop, log, hof

if __name__ == "__main__":
    main()