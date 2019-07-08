#!/usr/bin/python

import Db
import random
import array
import math
import sys
import time
from deap import base, creator, tools, algorithms

def main(current_simulation_time, simulation_name_truck):
    tiempo_total_ag = time.time()
    tiempo_inicio_ag = time.time()
    #truck
    askingTruck = simulation_name_truck.split(".")[0]
    #set current simlation time
    tCurrent = float(current_simulation_time.replace(',','.'))
     
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()

    conn = Db.Connect()
    SHOVEL_NUMBER = conn.getShovelNumber()
    TRUCK_STATES = conn.getTruckStates()
    TRUCKS_NUMBER = conn.getTruckNumber()
    unloadStations = conn.getAllUnloadStations()

    # Attribute generator 
    #                      define 'attr_bool' to be an attribute ('gene')
    #                      which corresponds to integers sampled uniformly
    #                      from the range [0,1] (i.e. 0 or 1 with equal
    #                      probability)
    #Genera valor de attr_bool de forma aleatoria esto en mi ag va desde 0 hasta el numero maximo de palas-1
    toolbox.register("no_shovel", random.randint, 1, SHOVEL_NUMBER)


    # Structure initializers
    #                         define 'individual' to be an individual
    #                         consisting of 100 'attr_bool' elements ('genes')
    # en mi ga el individuo consiste de valores enteros hasta el numero de camiones utilizados o registrados en la bd
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.no_shovel, TRUCKS_NUMBER)

    # define the population to be a list of individuals
    #igual en mi AG
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    #FUNCIONES DE UTILIDAD
    #
    #
    #
    def findTruck(id):
        my_truck = ''
        for truck in TRUCK_STATES:
            if id == truck[1]:
                my_truck = truck
        return my_truck

    def calcTA(truckstate):
        #calcta es llamada cada vez que se realiza la evaluacion del individuo
        #shovel assignment sera el numero generado aleatoriamente por el cromosoma del individuo
        #ts[4] == "vc" or ts[4] == "vd" no realizan cambios ya que no son observados
        estimatedarrivaltime = 0
        #si el camion se encuentra en viaje se asigna valor 0
        if truckstate:
            if str(truckstate[6]) == "v":
                #0 no se puede determinar u observar
                estimatedarrivaltime = 0

            elif str(truckstate[6]) == "d":
                    
                #se encuentra en descarga 
                #unload = conn.getUnloadStation(truckstate[3])
                deltatime = abs(tCurrent - float(truckstate[7].replace(",", ".")))
                #resultado = (tiempo en descargar completo) + tiempo maniobra de camion - (tiempo actual simulacion -> timeNow - tiempo inicio -> tiempo en el que llego a d)
                estimatedarrivaltime = (truckstate[12] + truckstate[14])/60000 - deltatime

            elif str(truckstate[6]) == "cd":
                
                unload = conn.getUnloadStation(truckstate[2])
                trucksinunload = conn.getTrucksInStation(truckstate[2])
                queuearrivaltime = 0

                #busca posicion de camion actual en cola y calcula tiempo de descarga de camion que se encuentre descargando
                for truckinunload in trucksinunload:

                    if truckinunload[6] == "cd":
                        #buscar posicion camion en cola
                        if truckstate[1] == truckinunload[1]:
                            #obtener indice
                            queuearrivaltime = float(truckinunload[7].replace(',','.'))

                    elif truckinunload[6] == "d":
                        #usar formula de camion cargando que se encuentra en la estacion de descarga
                        deltatime = abs(tCurrent - float(truckinunload[7].replace(",", ".")))
                        estimatedarrivaltime = (truckinunload[12] + truckinunload[14])/60000 - deltatime

                for truckinunload in trucksinunload:
                    #si el tiempo de llegada del camion que esta en el array es menor o = al tiempo de llegada del camion para calc ta sumar
                    if float(truckinunload[7].replace(',','.')) <= queuearrivaltime:
                        deltatime = abs(tCurrent - float(truckinunload[7].replace(",", ".")))
                        estimatedarrivaltime = estimatedarrivaltime + (truckinunload[12] + truckinunload[14])/6000 - deltatime

            elif str(truckstate[6]) == "c":
                
                #camion se encuentra cargando: capacidad camion * vel descarga + tiempo maniobra + tiempo actual - tiempo inicial
                #nueva forma: camion.capacidad * pala.palasMinuto + camion.spottingtime + tiempoactual - tiempo inicial + tiempo estimado en cola si lo tiene
                shovel = conn.getShovel(truckstate[2])
                unloadroute = conn.getRoutesToDestination(shovel[2], shovel[8]) 
                unload = conn.getUnloadStation(shovel[8])
                trucksinunload = conn.getTrucksInStation(unload[3])
                #shortest path not mean
                meanunloadroute = unloadroute[4]
                queuetime = 0

                #calcula tiempo de espera en descarga
                for truckinunload in trucksinunload:
                    deltatime = abs(tCurrent - float(truckinunload[7].replace(",", ".")))
                    queuetime = queuetime + (truckinunload[12] * unload[14]/60000) + truckinunload[11] - deltatime
                #resultado = (capacidad camion * vel. descarga pala) + tiempo maniobra de camion + (distancia de viaje * vel camion cargado) + tiempo de camiones que estan en la zona de descarga) 
                # - (tiempo actual simulacion -> timeNow - tiempo inicio -> tiempo en el que llego a d)
                #estimatedarrivaltime = (truckstate[12] * shovel[2]) + truckstate[11] + (meanunloadroute * truckstate[11]) + queuetime - deltatime
                # paladas necesarias para llenar camion = capacidad camion / cantidad por palada
                # nro paladas * LOAD_RATE * (tiempo de carga por una palada en milisegundos / 6000)
                # tiempo en recorrer camino = (meanunloadroute * truckstate[17]) (se asume ambos estan en km - distancia (km), velocidad cargado (km/h))
                estimatedarrivaltime = (truckstate[13] / shovel[3]) * ((shovel[4] * shovel[5])/60000) + (meanunloadroute * truckstate[17])/60000 + queuetime - deltatime

            elif str(truckstate[6]) == "cc":
                
                #camion se encuentra esperando carga
                shovel = conn.getShovel(truckstate[2])
                trucksinshovel = conn.getTrucksInStation(shovel[2])
                unloadroute = conn.getRoutesToDestination(shovel[2], shovel[8])
                unload = conn.getUnloadStation(shovel[8])
                trucksinunload = conn.getTrucksInStation(unload[3])

                meanunloadroute = 0
                queuearrivaltime = 0
                queuetime = 0
                estimatedarrivaltime = 0
                #calcula tiempos aprox para que el camion salga de la pala
                for truckinshovel in trucksinshovel:
                    if truckinshovel[6] == "cc":

                        if truckstate[1] == truckinshovel[1]:
                            queuearrivaltime = truckinshovel[7]

                    elif truckinshovel[6] == "c":
                        
                        deltatime = abs(tCurrent - float(truckinshovel[7].replace(",", ".")))
                        #estimatedarrivaltime = (truckinshovel[9] * shovel[2]) + truckinshovel[8] - deltatime
                        estimatedarrivaltime = (truckinshovel[13] / shovel[3]) * (shovel[4]/60000) - deltatime

                for truckinshovel in trucksinshovel:
                    
                    if float(truckinshovel[7].replace(',','.')) <= queuearrivaltime:
                        deltatime = abs(tCurrent - float(truckinshovel[7].replace(",", ".")))
                        estimatedarrivaltime = estimatedarrivaltime + (truckinshovel[12] + truckinshovel[14] )/60000  - deltatime

                #calcula tiempo de viaje estimado y lo adiciona al estimatedarrivaltime                
                meanunloadroute = unloadroute

                #suma tiempos de los camiones que se encuentran en destino (descarga)
                for truckinunload in trucksinunload:
                    deltatime = abs(tCurrent - float(truckinunload[7].replace(",", ".")))
                    #(truckinunload[12] + truckinunload[14])/6000 - deltatime
                    queuetime = queuetime + (truckinunload[12] + truckinunload[14])/60000 - deltatime
                # en cola descarga o en carga (truckstate[12] * shovel[2])
                #estimatedarrivaltime = estimatedarrivaltime + (truckstate[12] * shovel[2]) + truckstate[11] + (meanunloadroute * truckstate[11]) + queuetime - deltatime
                estimatedarrivaltime = estimatedarrivaltime + (truckstate[13] / shovel[3]) * ((shovel[4] * shovel[5])/60000) + ((meanunloadroute * truckstate[17])/60000) + queuetime - deltatime

            elif str(truckstate[7]) == "sag":
                # sag: solicita algoritmo genetico
                # ya se encuentra en el ultimo estado
                estimatedarrivaltime = 0
            
            return estimatedarrivaltime
    
    # the goal ('fitness') function to be maximized
    #en mi ag necesito qud se minimize
    def evalOneMin(individual):
        #calcular como en TA segun
        trucksCycleTime = 0
        listshovel = individual
        #recorre cada indice de la lista del individuo
        
        for index,value in enumerate(listshovel,1):
            truck = findTruck(index)
            if type(truck) is list:
                if truck[6] !=  "v" or '':
                    shovel = conn.getShovelById(value)
                    shovelname = str(shovel[2])

                    #datos obligatorios
                    # shovel[2], shovel[8]
                    #unload = conn.getUnloadStation(shovel[8])
                    for sublist in unloadStations:
                        if sublist[3] == shovel[8]:
                            unload = sublist
                            break
                    loadroutes = conn.getRoutesToDestination(unload[3], shovelname)
                    trucksinshovel = conn.getTrucksInStation(shovelname)
                    #unloadroutes = conn.getRoutesToDestination(shovel[2], shovel[8])
                    #trucksinunload = conn.getTrucksInStation(shovel[8])

                    # distancia mas corta ruta viaje a carga
                    loadtraveltime = loadroutes[4] * truck[12]

                    #suma camiones en carga
                    sumtrucksinshovel = 0
                    for truckinshovel in trucksinshovel:
                        deltatime = abs(float(tCurrent) -float(truckinshovel[7].replace(",", ".")))
                        #sumtrucksinshovel = sumtrucksinshovel + (truckinshovel[9] * shovel[2]) + truckinshovel[8] - deltatime
                        sumtrucksinshovel = sumtrucksinshovel + (truckinshovel[13] / shovel[3]) * ((shovel[4] * shovel[5])/60000) + truckinshovel[17]/60000 - deltatime

                    #distancia prom ruta viaje a descarga
                    #unloadtraveltime = unloadroutes[4] * truck[16]

                    #suma camiones en descarga
                    #sumtrucksinunload = 0
                    '''for truckinunload in trucksinunload:
                        deltatime = abs(tCurrent - float(truckinunload[7].replace(",", ".")))'''
                        #sumtrucksinunload = sumtrucksinunload + (truckinunload[9] * unload[2]) + truckinunload[8] - deltatime
                        #sumtrucksinunload = sumtrucksinunload + (truckinunload[15]/60000) + (truckinunload[17]/60000) - deltatime
                    
                    #trucksCycleTime = loadtraveltime + sumtrucksinshovel + unloadtraveltime + sumtrucksinunload
                    trucksCycleTime = loadtraveltime + sumtrucksinshovel
                    #se agrega el TA
                    trucksCycleTime = trucksCycleTime + individual[index-1]

        #calcular TGA
        return trucksCycleTime,
        #return sum(individual),

    #----------
    # Operator registration
    #----------
    # register the goal / fitness function
    toolbox.register("evaluate", evalOneMin)

    # register the crossover operator
    toolbox.register("mate", tools.cxTwoPoint)

    # register a mutation operator with a probability to
    # flip each attribute/gene of 0.05
    toolbox.register("mutate", tools.mutUniformInt, low = 1, up = SHOVEL_NUMBER, indpb=50)

    # operator for selecting individuals for breeding the next
    # generation: each individual of the current generation
    # is replaced by the 'fittest' (best) of three individuals
    # drawn randomly from the current generation.
    toolbox.register("select", tools.selTournament, tournsize=3)
    #print("Termino fase 1: ", time.time()-tiempo_inicio_ag)
    tiempo_inicio_ag = time.time()
    # create an initial population of 300 individuals (where
    # each individual is a list of integers)
    pop = toolbox.population(n=5)
    #print("Termino fase 2: ", time.time()-tiempo_inicio_ag)
    tiempo_inicio_ag = time.time()
    # CXPB  is the probability with which two individuals
    #       are crossed
    #
    # MUTPB is the probability for mutating an individual
    CXPB, MUTPB = 0.5, 0.08

    #convergence list
    results = []

    genetic_algorithm_initial_time = time.time()
    # Evaluate the entire population
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    #print("Termino evaluacion inicial: ", time.time()-genetic_algorithm_initial_time)
    genetic_algorithm_initial_time = time.time()    
    #print("evaluacion primera poblacion")
    # Extracting all the fitnesses of 
    # Variable keeping track of the number of generations
    g = 0    
    # Begin the evolution
    #tiempo maximo de ejecucion 1 minuto
    time_current = time.time() + 7
    converge = 0
    #while converge < 3 or (int(time.time()/60) - time_current) < 1:
    #while converge < 3 or (int(time.time()) - time_current) < 1:
    while time.time() <= time_current:
        variable_tiempo=time.time()
        variable_tiempo_final=time.time()
        # A new generation
        #time_current = int(time.time()/60)
        g = g + 1
        #print("-- Generation %i --" % g)
        #print("cantidad de individuos: ", len(pop))
        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        #print("Individuos seleccionados: ", len(offspring))        
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))  
        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):

            # cross two individuals with probability CXPB
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                # fitness values of the children
                # must be recalculated later
                del child1.fitness.values
                del child2.fitness.values                

        for mutant in offspring:            
            # mutate an individual with probability MUTPB
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values
        # Evaluate the individuals with an invalid fitness        
        #print("  Evaluated %i individuals" % len(invalid_ind))
        fitnesses = list(map(toolbox.evaluate, offspring))

        for ind, fit in zip(offspring, fitnesses):
            ind.fitness.values = fit
        
        total = 0

        for fitness in fitnesses:
            total = total + fitness[0]
        results.append(total)
        #fin prueba
        # The population is entirely replaced by the offspring
        pop[:] = offspring
        # Gather all the fitnesses in one list and print the stats        
        #converge = convergence(results, converge)
        #print("converge: ", converge)
    print("generations: %i" % g)
    print("-- End of (successful) evolution --")
    tiempo_inicio_ag = time.time()
    #print("individuos candidatos")
    #print(pop)
    best_ind = tools.selBest(pop, 1)[0]
    #print("mejor individuo seleccionado")
    #print(best_ind)
    #print("fitness mejor individuo sleeccionado")
    #print(best_ind.fitness)
    #print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))
    # find truck index 
    tiempo_inicio_ag = time.time()
    truck_index = conn.getTruckIndex(askingTruck)[0]
    trucks_index = conn.getTrucksIndex()

    assignments = [(trucks_index[i], best_ind[i]) for i in range(0, len(trucks_index))]

    # find unload index (resulting data), name
    shovel_index = best_ind[truck_index-1]
    shovel_name = conn.getLoadName(shovel_index)[0]
    # insert asssignment
    #conn.insertAssignment(truck_index, unload_index)
    conn.updateAssignments()
    conn.insertAssignments(assignments)

    # return results to SIMIO
    #print("mejor individuo, tiempo estimado, fitness")
    conn.disconnect()
    estimated_arrival_time= 0
    return  best_ind, estimated_arrival_time, best_ind.fitness.values, shovel_name

def convergence(results, converge):
    print(results)
    converge = 0
    if len(results)>2:
        if results[-1] == results[-2] == results[-3]:
            converge = 3
    return converge