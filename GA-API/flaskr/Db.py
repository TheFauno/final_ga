import mysql.connector

class Connect:
    #constructor - start connection
    def __init__(self):

        cdata = {
            "host": "localhost",
            "username": "root",
            "password": "",
            "database": "flow_truck"
        }

        self._host = cdata["host"]
        self._username = cdata["username"]
        self._password = cdata["password"]
        self._database = cdata["database"]
        self._cnx = mysql.connector.connect(  
                                            user=self._username, 
                                            password=self._password,
                                            host=self._host,
                                            database=self._database
                                        )
    #close connection
    def disconnect(self):
        self._cnx.close()

    def getTruckInfo(self, id):
        #cursor
        cursor = self._cnx.cursor()
        #devuelve cuantos tipos se crearan y caracteristicas
        query = "SELECT c.id, c.nombre, tc.*, fc.NombreEstacion, fc.estado FROM camion c, tipocamion tc, flujo_camion fc WHERE c.id = %s AND c.fk_tipo = tc.Tipo AND fc.IdFlujo = (SELECT MAX(f.IdFlujo) FROM flujo_camion f WHERE f.NombreCamion = c.nombre)"
        cursor.execute(query, (id,))
        res = cursor.fetchone()
        cursor.close()
        return res
        
    def getTrucksInShovel(self, shovel):
        #cursor
        cursor = self._cnx.cursor()
        #devuelve cuantos tipos se crearan y caracteristicas
        query = "SELECT * FROM flujo_camion where NombreEstacion = %s AND Terminado = 0"
        cursor.execute(query, (shovel,))
        res = cursor.fetchall()
        cursor.close()
        return res

    def getTruckStates(self):
        #cursor
        cursor = self._cnx.cursor()
        #devuelve cuantos tipos se crearan y caracteristicas
        '''query = """SELECT fc.*, c.id, c.fk_tipo, tc.TiempoPromedioManiobra, tc.Capacidad, tc.VelocidadPromedioDescargado, tc.VelocidadPromedioCargado
        FROM flujo_camion fc, camion c, tipocamion tc 
        where fc.Terminado = 0 AND fc.NombreCamion = c.nombre AND c.fk_tipo = tc.Tipo"""'''
        query = "select tf.*, t.* from truck_flow tf, truck t where tf.FINISHED = 'No' AND tf.TRUCK_ID = t.ID"
        cursor.execute(query)
        res = cursor.fetchall()
        cursor.close()
        return res
    
    #get truck types
    def getTruckTypes(self):
        #cursor
        cursor = self._cnx.cursor()
        #devuelve cuantos tipos se crearan y caracteristicas
        query = "SELECT * FROM tipocamion"
        cursor.execute(query)
        res = cursor.fetchall()
        cursor.close()
        return res

    def getTruckNumber(self):
        #cursor
        cursor = self._cnx.cursor()
        #devuelve cuantos tipos se crearan y caracteristicas
        '''query = "select sum(Cantidad) as n_trucks from tipocamion"'''
        query = "select count(*) as n_trucks from truck"
        cursor.execute(query,)
        res = cursor.fetchone()
        cursor.close()
        return int(res[0])

    def getShovelNumber(self):
        #cursor
        cursor = self._cnx.cursor()
        #devuelve cuantos tipos se crearan y caracteristicas
        query = "select max(ID) from shovel"
        cursor.execute(query,)
        res = cursor.fetchone()
        cursor.close()
        return int(res[0])
    
    def getRoutesToDestination(self, nodoActual, nodoDestino):
        #cursor
        cursor = self._cnx.cursor()
        #devuelve destino de la pala
        #query = "SELECT * FROM rutas WHERE nodo_actual = %s AND nodo_destino = %s"
        query = "SELECT * FROM shortest_path WHERE STARTING_AT = %s AND DIRECTED_TO = %s"
        params = (nodoActual, nodoDestino)
        cursor.execute(query, params)
        res = cursor.fetchall()
        cursor.close()
        return res

    def getTrucksInStation(self, shovel):
        cursor = self._cnx.cursor()
        #query = "SELECT * FROM flujo_camion WHERE NombreEstacion = %s AND Terminado = 0"
        #query = "SELECT fc.IdFlujo, fc.NombreCamion, fc.NombreEstacion, fc.estado, fc.horasimulacion, tc.* FROM flujo_camion fc, tipocamion tc  WHERE fc.NombreEstacion = %s AND fc.Terminado = 0 and fc.TipoCamion = tc.Tipo"
        query = """SELECT tf.*, t.* 
                    FROM truck_flow tf, truck t
                    WHERE tf.STATION_ID = %s AND tf.FINISHED = 'No' AND tf.TRUCK_ID = t.ID"""
        shovel = str(shovel)
        cursor.execute(query, (shovel,))
        res = cursor.fetchall()
        cursor.close()
        return res

    def getUnloadStation(self, stationName):
        cursor = self._cnx.cursor()
        #query = "SELECT * FROM flujo_camion WHERE NombreEstacion = %s AND Terminado = 0"
        '''query = "SELECT * FROM descargas WHERE nombre = %s"'''
        query = "select * from unload where POSITIONED_AT = %s"
        stationName = str(stationName)
        cursor.execute(query, (stationName,))
        res = cursor.fetchone()
        cursor.close()
        return res

    def getAllUnloadStations(self):
        cursor = self._cnx.cursor()
        #query = "SELECT * FROM flujo_camion WHERE NombreEstacion = %s AND Terminado = 0"
        query = "select * from unload"
        cursor.execute(query)
        res = cursor.fetchall()
        cursor.close()
        return res

    def getLoadName(self, shovel):
        cursor = self._cnx.cursor()
        #query = "SELECT * FROM palas WHERE nombre = %s"
        query = "SELECT POSITIONED_AT FROM shovel WHERE ID = %s"
        cursor.execute(query, (shovel,))
        res = cursor.fetchone()
        cursor.close()
        return res

    def getShovelById(self, id):
        cursor = self._cnx.cursor()
        #query = "SELECT * FROM palas WHERE nombre = %s"
        query = "SELECT * FROM shovel WHERE ID = %s"
        cursor.execute(query, (id,))
        res = cursor.fetchone()
        cursor.close()
        return res

    def insertGA(self, truck):
        cursor = self._cnx.cursor()
        query = "INSERT INTO ag_inicial (pala) VALUES(%s)"
        cursor.execute(query, (truck,))
        self._cnx.commit()
        cursor.close()

    def truncGAInit(self):
        cursor = self._cnx.cursor()
        query = "TRUNCATE TABLE ag_inicial"
        cursor.execute(query)
        self._cnx.commit()
        cursor.close()

    def getTruckIndex(self, askingTruck):
        cursor = self._cnx.cursor()
        query = "SELECT ID FROM TRUCK WHERE NAME = %s"
        cursor.execute(query, (askingTruck,))
        res = cursor.fetchone()
        cursor.close()
        return res

    def getTrucksIndex(self):
        cursor = self._cnx.cursor()
        query = "SELECT ID FROM TRUCK"
        cursor.execute(query)
        res = cursor.fetchall()
        cursor.close()
        return res

    def getShovelName(self, shovel_index):
        cursor = self._cnx.cursor()
        #query = "SELECT POSITIONED_AT FROM TRUCK WHERE ID = %s"
        query = "SELECT POSITIONED_AT FROM SHOVEL WHERE ID = %s"
        cursor.execute(query, (shovel_index,))
        res = cursor.fetchone()
        cursor.close()
        return res

    def insertAssignment(self, truck_index, unload_index):
        cursor = self._cnx.cursor()
        query = "INSERT INTO ASSIGNMENT(TRUCK_ID, SHOVEL_ID) VALUES(%s, %s)"
        cursor.execute(query, (truck_index, unload_index))
        self._cnx.commit()
        cursor.close()

    def insertAssignments(self, assignments):
        cursor = self._cnx.cursor()
        i = 0
        for assignment in assignments:
            query = "INSERT INTO ASSIGNMENT(TRUCK_ID, SHOVEL_ID) VALUES(%s, %s)"
            cursor.execute(query, (assignment[0][0], assignment[1]))
            i = i+1
        self._cnx.commit()
        cursor.close()

    def updateAssignments(self):
        cursor = self._cnx.cursor()
        query = "UPDATE ASSIGNMENT SET STATUS = %s WHERE status = %s"
        cursor.execute(query, ('not assigned', 'assigned'))
        self._cnx.commit()
        cursor.close()

    def updateAssignment(self, truckId):
        cursor = self._cnx.cursor()
        query = "UPDATE ASSIGNMENT SET STATUS = %s WHERE TRUCK_ID = %s AND STATUS = %s"
        cursor.execute(query, ('assigned', truckId[0][0], 'not assigned'))
        self._cnx.commit()
        cursor.close()

    def hasAssignment(self, truckId):
        cursor = self._cnx.cursor()
        query = "SELECT SHOVEL_ID FROM ASSIGNMENT WHERE TRUCK_ID = %s AND STATUS = 'not assigned'"
        cursor.execute(query, (truckId[0][0],))
        res = cursor.fetchall()
        cursor.close()
        return res

    def findTruckByName(self, truckName):
        cursor = self._cnx.cursor()
        query = "SELECT ID FROM TRUCK WHERE NAME = %s"
        cursor.execute(query, (truckName,))
        res = cursor.fetchall()
        cursor.close()
        return res