import Db
import random
import array
import math
import sys
import time
from deap import base, creator, tools, algorithms

#----------

def main(current_simulation_time):

    #
    #
    #
    #
    #
    #
    #
    #
    #

    #random.seed(64) -> nose para que es xd
    #set current simlation time
    tCurrent = float(current_simulation_time.replace(',','.'))



    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()

    conn = Db.Connect()
    SHOVEL_NUMBER = conn.getShovelNumber()-1
    #tCurrent = formData['timeNow']
    TRUCK_STATES = conn.getTruckStates()
    TRUCKS_NUMBER = conn.getTruckNumber()

    # Attribute generator 
    #                      define 'attr_bool' to be an attribute ('gene')
    #                      which corresponds to integers sampled uniformly
    #                      from the range [0,1] (i.e. 0 or 1 with equal
    #                      probability)
    #Genera valor de attr_bool de forma aleatoria esto en mi ag va desde 0 hasta el numero maximo de palas-1
    toolbox.register("no_shovel", random.randint, 0, SHOVEL_NUMBER)


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
            if id == truck[10]:
                my_truck = truck
        return my_truck

    def calcTA(truckstate):
        #calcta es llamada cada vez que se realiza la evaluacion del individuo
        #shovel assignment sera el numero generado aleatoriamente por el cromosoma del individuo
        #ts[7] == "vc" or ts[7] == "vd" no realizan cambios ya que no son observados
        estimatedarrivaltime = 0
        #si el camion se encuentra en viaje se asigna valor 0
        if truckstate:
            if str(truckstate[7]) == "v":
                #0 no se puede determinar u observar
                estimatedarrivaltime = 0

            elif str(truckstate[7]) == "d":
                    
                #se encuentra en descarga 
                unload = conn.getUnloadStation(truckstate[3])
                deltatime = abs(tCurrent - float(truckstate[8].replace(",", ".")))
                #resultado = (capacidad camion * vel. descarga pala) + tiempo maniobra de camion - (tiempo actual simulacion -> timeNow - tiempo inicio -> tiempo en el que llego a d)
                estimatedarrivaltime = (truckstate[13] * unload[2]) + truckstate[12] - deltatime

            elif str(truckstate[7]) == "cd":
                
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
                        deltatime = abs(tCurrent - float(truckinunload[4].replace(",", ".")))
                        estimatedarrivaltime = (truckinunload[9] * unload[2]) + truckinunload[8] - deltatime

                for truckinunload in trucksinunload:
                    #si el tiempo de llegada del camion que esta en el array es menor o = al tiempo de llegada del camion para calc ta sumar
                    if truckinunload[4] <= queuearrivaltime:
                        deltatime = abs(tCurrent - float(truckinunload[4].replace(",", ".")))
                        estimatedarrivaltime = estimatedarrivaltime + (truckinunload[9] * unload[2]) + truckinunload[8] - deltatime

            elif str(truckstate[7]) == "c":
                
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
                    deltatime = abs(tCurrent - float(truckinunload[4].replace(",", ".")))
                    queuetime = queuetime + (truckinunload[12] * unload[2]) + truckinunload[11] - deltatime
                #resultado = (capacidad camion * vel. descarga pala) + tiempo maniobra de camion + (distancia de viaje * vel camion cargado) + tiempo de camiones que estan en la zona de descarga) 
                # - (tiempo actual simulacion -> timeNow - tiempo inicio -> tiempo en el que llego a d)
                estimatedarrivaltime = (truckstate[12] * shovel[2]) + truckstate[11] + (meanunloadroute * truckstate[11]) + queuetime - deltatime

            elif str(truckstate[7]) == "cc":
                
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
                        
                        deltatime = abs(tCurrent - float(truckinshovel[4].replace(",", ".")))
                        estimatedarrivaltime = (truckinshovel[9] * shovel[2]) + truckinshovel[8] - deltatime

                for truckinshovel in trucksinshovel:
                    
                    if truckinshovel[4] <= queuearrivaltime:
                        deltatime = abs(tCurrent - float(truckinshovel[4].replace(",", ".")))
                        estimatedarrivaltime = estimatedarrivaltime + (truckinshovel[9] * shovel[2]) + truckinshovel[8] - deltatime

                #calcula tiempo de viaje estimado y lo adiciona al estimatedarrivaltime
                for unloadroute in unloadroutes:
                    meanunloadroute = meanunloadroute + unloadroute[3]
                
                meanunloadroute = meanunloadroute/len(unloadroutes)

                #suma tiempos de los camiones que se encuentran en destino (descarga)
                for truckinunload in trucksinunload:
                    deltatime = abs(tCurrent - float(truckinunload[4].replace(",", ".")))
                    queuetime = queuetime + (truckinunload[12] * unload[2]) + truckinunload[11] - deltatime
                estimatedarrivaltime = estimatedarrivaltime + (truckstate[12] * shovel[2]) + truckstate[11] + (meanunloadroute * truckstate[11]) + queuetime - deltatime

            elif str(truckstate[7]) == "sag":
                
                #ya se encuentra en el ultimo estado
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
            if truck[7] !=  "v":
                shovelname = "Pala"+str(value)
                shovel = conn.getShovel(shovelname)

                #datos obligatorios

                loadroutes = conn.getRoutesToDestination(truck[3], shovelname)
                trucksinshovel = conn.getTrucksInStation(shovelname)
                unloadroutes = conn.getRoutesToDestination(shovel[1], shovel[3])
                unload = conn.getUnloadStation(shovel[3])
                trucksinunload = conn.getTrucksInStation(shovel[3])                

                # distancia prom ruta viaje a carga

                loadmeandistance = 0
                for loadroute in loadroutes:
                    loadmeandistance = loadmeandistance + loadroute[3]
                loadmeandistance = loadmeandistance / len(loadroutes)
                loadtraveltime = loadmeandistance * truck[12]

                #suma camiones en carga
                sumtrucksinshovel = 0
                for truckinshovel in trucksinshovel:
                    deltatime = abs(float(tCurrent) -float(truckinshovel[4].replace(",", ".")))
                    sumtrucksinshovel = sumtrucksinshovel + (truckinshovel[9] * shovel[2]) + truckinshovel[8] - deltatime

                #distancia prom ruta viaje a descarga
                unloadmeandistance = 0
                for unloadroute in unloadroutes:
                    unloadmeandistance = unloadmeandistance + unloadroute[3]
                unloadmeandistance = unloadmeandistance / len(unloadroutes)
                unloadtraveltime = unloadmeandistance * truck[12]

                #suma camiones en descarga
                sumtrucksinunload = 0
                for truckinunload in trucksinunload:
                    deltatime = abs(tCurrent - float(truckinunload[4].replace(",", ".")))
                    sumtrucksinunload = sumtrucksinunload + (truckinunload[9] * unload[2]) + truckinunload[8] - deltatime

                trucksCycleTime = loadtraveltime + sumtrucksinshovel + unloadtraveltime + sumtrucksinunload
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
    toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)

    # operator for selecting individuals for breeding the next
    # generation: each individual of the current generation
    # is replaced by the 'fittest' (best) of three individuals
    # drawn randomly from the current generation.
    toolbox.register("select", tools.selTournament, tournsize=3)

    # create an initial population of 300 individuals (where
    # each individual is a list of integers)
    pop = toolbox.population(n=300)

    # CXPB  is the probability with which two individuals
    #       are crossed
    #
    # MUTPB is the probability for mutating an individual
    CXPB, MUTPB = 0.5, 0.2
    
    print("Start of evolution")
    
    # Evaluate the entire population
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit
    
    print("  Evaluated %i individuals" % len(pop))

    # Extracting all the fitnesses of 
    fits = [ind.fitness.values[0] for ind in pop]

    # Variable keeping track of the number of generations
    g = 0
    
    # Begin the evolution
    #tiempo maximo de ejecucion 1 minuto
    time_current = int(time.time()/60)
    while (int(time.time()/60) - time_current) < 1 and g < 500:
        # A new generation
        time_current = int(time.time()/60)
        g = g + 1
        print("-- Generation %i --" % g)
        
        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
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
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        
        print("  Evaluated %i individuals" % len(invalid_ind))
        
        # The population is entirely replaced by the offspring
        pop[:] = offspring
        
        # Gather all the fitnesses in one list and print the stats
        fits = [ind.fitness.values[0] for ind in pop]
        
        length = len(pop)
        mean = sum(fits) / length
        sum2 = sum(x*x for x in fits)
        std = abs(sum2 / length - mean**2)**0.5
        
        print("  Min %s" % min(fits))
        print("  Max %s" % max(fits))
        print("  Avg %s" % mean)
        print("  Std %s" % std)
    
    print("-- End of (successful) evolution --")
    best_ind = tools.selBest(pop, 1)[0]
    print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))
    estimated_arrival_time = []
    for index, val in enumerate(best_ind, start = 1):
        ta = calcTA(findTruck(index))
        estimated_arrival_time.append(ta)
    print("mejor individuo, tiempo estimado, fitness")
    return  best_ind, estimated_arrival_time, best_ind.fitness.values

'''if __name__ == "__main__":
    main()'''