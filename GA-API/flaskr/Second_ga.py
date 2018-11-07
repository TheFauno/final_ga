import Db
import random
import math
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
    CXPB, MUTPB = 0.5, 0.2
    TOURN_SIZE = 2

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
        #calcular TA
        ta = self.getTA(conn)
        #AG
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness = creator.FitnessMin)
        #operators
        toolbox = base.Toolbox()
        toolbox.register("individual", self.InitMatrix, creator.Individual, ta) # define individuo
        toolbox.register("population", tools.initRepeat, list, toolbox.individual) #crea la poblacion
        pop = toolbox.population(n=4)
        
        toolbox.register("evaluate", self.evalMin, conn, list)

        #toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mate", self.CxFunction)
        toolbox.register("mutate", self.MutFunction)
        toolbox.register("select", self.Selection)
        #crear poblacion
        
        # Evaluate the entire population
        fitnesses = []
        for individual in pop:
            fitnesses.append(self.evalMin(conn, individual))
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit,
            ind[2] = fit
        
        hof = tools.HallOfFame(1)

        generation = 0
        GEN_LIMIT = 100

        """
        evaluate(population) LISTO
        for g in range(ngen): LISTO
            population = select(population, len(population)) LISTO
            offspring = varAnd(population, toolbox, cxpb, mutpb) X
            evaluate(offspring)
            population = offspring
        """
        
        for generation in range(GEN_LIMIT):
            # A new generation
            generation = generation + 1
            print("-- Generation %i --" % generation)

            # Select the next generation individuals
            offspring = toolbox.select(pop)
            #offspring = algorithms.varAnd(pop, toolbox, self.CXPB, self.MUTPB)
            """
            seccion varAnd
            """
            offspring = [toolbox.clone(ind) for ind in pop]
            print("descendencia")
            for i in offspring:
                print(i)
            print("fin descendencia")
            # Apply crossover and mutation on the offspring
            for i in range(1, len(offspring), 2):
                if random.random() < self.CXPB:
                    offspring[i - 1], offspring[i] = toolbox.mate(conn, offspring[i - 1],offspring[i])
                    del offspring[i - 1].fitness.values, offspring[i].fitness.values

            for i in range(len(offspring)):
                if random.random() < self.MUTPB:
                    offspring[i] = toolbox.mutate(conn, offspring[i])
                    del offspring[i].fitness.values
            """
            fin seccion varAnd
            """
            #evaluar
            # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = toolbox.map(self.evalMinWrapper(conn,invalid_ind))
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
            #1. eaSimple => pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=2500, halloffame=hof, verbose=False)
            #2.     varAnd

            # Clone the selected individuals, creo que el clone no me sirve
            #offspring = list(map(toolbox.clone, offspring))
            #cruce y mutacion
            # Apply crossover and mutation on the offspring

            #selecciona parejas
            '''for child1, child2 in zip(offspring[::2], offspring[1::2]):
                obtiene probabilidad de mutacion
                if random.random() < self.CXPB:
                    offspring = toolbox.mate(conn, child1, child2)
                    print('resultado cruce')
                    print(offspring)
                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in offspring:
                if random.random() < self.MUTPB:
                    offspring = toolbox.mutate(conn, mutant)
                    del mutant.fitness.values'''

            # Update the hall of fame with the generated individuals
            hof.update(offspring)

            # Replace the current population by the offspring
            pop[:] = offspring

        '''fitness_points = []
        fo'r ind in pop:
            fitness_points.append(ind[2])
        best_ind = []
        for fitness_point in fitness_points:
            if(fitness_point == min(fitness_points)):
                best_ind = fitness_point'''
        print(hof)
        return pop

    def InitMatrix(self, container, ta):
        shovel = []
        for i in range(1, self.N_TRUCKS):
            shovelassignment = random.randint(0, self.N_SHOVELS-1)
            shovel.append(shovelassignment)
        return container([shovel,ta, []])

    def Selection(self, pop):

        #select 2 ind from pop
        #selecciona de forma aleatorea, esto para evitar un estancamiento en un posible local
        POP_SIZE = len(pop)
        #generate 2 unique values in pop_size
        l = range(1, POP_SIZE)
        random.shuffle(l)
        index_list = []
        offspring = []

        for pair in zip(pop[::2], pop[1::2]):
            #por cada par obtener la mejor solucion
            if(pair[0][2] <  pair[1][2]):
                offspring.append(pair[0])
            else:
                offspring.append(pair[1])

        '''while len(index_list) <= (POP_SIZE) and len(l) > 1:

            index_list.append(l.pop())
        
        allowed_values = range(0, len(index_list))

        for index,individual in enumerate(pop):

            if index in allowed_values:
                offspring.append(individual)'''

        return offspring

    def CxFunction(self, conn, ind1, ind2):
        #cruce entre secciones de dos puntos
        print("padres")
        print(ind1)
        print(ind2)
        #copiar de padres
        child1 = ind1
        child3 = ind1
        child2= ind2
        child4= ind2
        #obtener rango de intecambio para childs  1,2
        point1 = random.randint(0, self.N_TRUCKS-2)
        point2 = random.randint(point1+1, self.N_TRUCKS)

        if point1 == point2:
            #cruce
            child1[0][point1], child2[0][point1] = child2[0][point1], child1[0][point1]
        else:
            #cruce
            child1[0][point1:point2], child2[0][point1:point2] = child2[0][point1:point2], child1[0][point1:point2]

        '''point1 = random.randint(0, self.N_TRUCKS-2)
        point2 = random.randint(point1+1, self.N_TRUCKS)
        if point1 == point2:
            #cruce
            child3[0][point1], child4[0][point1] = child4[0][point1], child3[0][point1]
        else:
            #cruce
            child3[0][point1:point2], child4[0][point1:point2] = child4[0][point1:point2], child3[0][point1:point2]'''

        #evaluar cada hijo child1,chidl2
        child1 = self.evalMinWrapper(conn, child1)
        child2 = self.evalMinWrapper(conn, child2)
        '''child3 = self.evalMinWrapper(conn, child3)
        child4 = self.evalMinWrapper(conn, child4)'''
        #seleccionar mejores descendencias usando elitismo de fitness (seleccionar 2)
        '''fitness_values = sorted([ind1[2], ind2[2], child1[2], child2[2], child3[2], child4[2]], reverse=True)'''
        fitness_values = sorted([ind1[2], ind2[2], child1[2], child2[2]], reverse=True)
        '''best_fitness = [fitness_values[-1], fitness_values[-2], fitness_values[-3], fitness_values[-4]]'''
        best_fitness = [fitness_values[-1], fitness_values[-2]]
        r = []
        for candidato in [ind1, ind2, child1, child2]:
            if candidato[2] in best_fitness:
                r.append(candidato)

        return r[0],r[1]

    def MutFunction(self, conn, individual):
        #generar 2 indices para seleccionar que camion va a mutar
        #error aqui
        point1 = random.randint(0, self.N_TRUCKS-2)
        point2 = random.randint(0, self.N_TRUCKS-2)
        individual[0][point1] = random.randint(0, self.N_SHOVELS-1)
        individual[0][point2] = random.randint(0, self.N_SHOVELS-1)
        return tuple(self.evalMinWrapper(conn, individual))
    
    def evalMinWrapper(self, conn, individual):
        individual[2] = self.evalMin(conn, individual)
        return individual

    def evalMin(self, conn, individual):
        
        #calcular como en TA segun 
        trucksCycleTime = 0
        listshovel = individual[0]

        #recorre cada indice de la lista del individuo

        for index,value in enumerate(listshovel,1):
            
            truck = self.findTruck(index)
            
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
                    deltatime = abs(float(self.tCurrent) -float(truckinshovel[4].replace(",", ".")))
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
                    deltatime = abs(float(self.tCurrent) -float(truckinunload[4].replace(",", ".")))
                    sumtrucksinunload = sumtrucksinunload + (truckinunload[9] * unload[2]) + truckinunload[8] - deltatime

                trucksCycleTime = loadtraveltime + sumtrucksinshovel + unloadtraveltime + sumtrucksinunload
                #se agrega el TA
            trucksCycleTime = trucksCycleTime + individual[1][index-1]
        #calcular TGA
        return trucksCycleTime

    def findTruck(self, id):
        for truck in self.TRUCK_STATES:
            if id == truck[10]:
                return truck

    def getRequestTruck(self):
        #usar despues de seleccionar la solucion
        for truck in self.TRUCK_STATES:
            if truck[8] == self.tCurrent and truck[7] == "sag":
                return truck        
    
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
            if truckstate:
                if str(truckstate[7]) == "v":
                    #0 no se puede determinar u observar
                    estimatedarrivaltime = 0

                elif str(truckstate[7]) == "d":
                    
                    #se encuentra en descarga 
                    unload = conn.getUnloadStation(truckstate[3])
                    deltatime = abs(float(self.tCurrent)-float(truckstate[8].replace(",", ".")))
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
                            deltatime = abs(float(self.tCurrent) - float(truckinunload[4].replace(",", ".")))
                            estimatedarrivaltime = (truckinunload[9] * unload[2]) + truckinunload[8] - deltatime

                    for truckinunload in trucksinunload:
                        #si el tiempo de llegada del camion que esta en el array es menor o = al tiempo de llegada del camion para calc ta sumar
                        if truckinunload[4] <= queuearrivaltime:
                            deltatime = abs(float(self.tCurrent) - float(truckinunload[4].replace(",", ".")))
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
                        deltatime = abs(float(self.tCurrent)-float(truckinunload[4].replace(",", ".")))
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
                    
                    #ya se encuentra en el ultimo estado
                    estimatedarrivaltime = 0
            
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