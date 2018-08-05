import mysql.connector

class Connect:
    #constructor - start connection
    def __init__(self, configdata):
        self._host = configdata["host"]
        self._username = configdata["username"]
        self._password = configdata["password"]
        self._database = configdata["database"]
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
        query = "SELECT c.id, c.nombre, tc.*, fc.NombreEstacion FROM camion c, tipocamion tc, flujo_camion fc WHERE c.id = %s AND c.fk_tipo = tc.Tipo AND fc.IdFlujo = (SELECT MAX(f.IdFlujo) FROM flujo_camion f WHERE f.NombreCamion = c.nombre)"
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
        query = "SELECT * FROM flujo_camion where NombreEstacion LIKE 'Pala%' AND Terminado = 0"
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
        query = "select sum(Cantidad)+1 as n_trucks from tipocamion"
        cursor.execute(query,)
        res = cursor.fetchone()
        cursor.close()
        return int(res[0])

    def getShovelNumber(self):
        #cursor
        cursor = self._cnx.cursor()
        #devuelve cuantos tipos se crearan y caracteristicas
        query = "select max(id) as n_shovels from palas"
        cursor.execute(query,)
        res = cursor.fetchone()
        cursor.close()
        return int(res[0])
    
    def getRoutesToDestination(self, nodoActual, nodoDestino):
        #cursor
        cursor = self._cnx.cursor()
        #devuelve cuantos tipos se crearan y caracteristicas
        query = "SELECT * FROM rutas WHERE nodo_actual = %s AND nodo_destino = %s"
        params = (nodoActual, nodoDestino)
        cursor.execute(query, params)
        res = cursor.fetchall()
        cursor.close()
        return res

    def getTrucksInStation(self, shovel):
        cursor = self._cnx.cursor()
        #query = "SELECT * FROM flujo_camion WHERE NombreEstacion = %s AND Terminado = 0"
        query = "SELECT fc.IdFlujo, fc.NombreCamion, fc.NombreEstacion, fc.TipoBuffer, tc.* FROM flujo_camion fc, tipocamion tc  WHERE fc.NombreEstacion = %s AND fc.Terminado = 0 and fc.TipoCamion = tc.Tipo"
        shovel = str(shovel)
        cursor.execute(query, (shovel,))
        res = cursor.fetchall()
        cursor.close()
        return res

    def getUnloadStation(self, stationName):
        cursor = self._cnx.cursor()
        #query = "SELECT * FROM flujo_camion WHERE NombreEstacion = %s AND Terminado = 0"
        query = "SELECT * FROM descargas WHERE nombre = %s"
        stationName = str(stationName)
        cursor.execute(query, (stationName,))
        res = cursor.fetchone()
        cursor.close()
        return res

    def getShovel(self, shovel):
        cursor = self._cnx.cursor()
        query = "SELECT * FROM palas WHERE nombre = %s"
        cursor.execute(query, (shovel,))
        res = cursor.fetchone()
        cursor.close()
        return res

    def getTruckCapacity(self, type):
        cursor = self._cnx.cursor()
        query = "SELECT * FROM tipocamion WHERE Tipo = %s"
        cursor.execute(query, (type,))
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