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

    def getTruckStates(self):
        #cursor
        cursor = self._cnx.cursor()
        #devuelve cuantos tipos se crearan y caracteristicas
        query = "SELECT * FROM flujo_camion where Terminado = 0"
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
    
    def getRoutesToDestination(self, nodoActual, nodoDestino):
        #cursor
        cursor = self._cnx.cursor()
        #devuelve cuantos tipos se crearan y caracteristicas
        query = "SELECT * FROM rutas WHERE nodo_actual = %s AND nodo_destino = %s"
        params = (str(nodoActual), str(nodoDestino))
        cursor.execute(query, (nodoActual, nodoDestino))
        res = cursor.fetchall()
        cursor.close()
        return res

    def getTrucksInShovel(self, shovel):
        cursor = self._cnx.cursor()
        query = "SELECT * FROM flujo_camion WHERE NombreEstacion = %s AND Terminado = 0"
        shovel = str(shovel)
        cursor.execute(query, (shovel,))
        res = cursor.fetchall()
        cursor.close()
        return res

    def getShovel(self, shovel):
        cursor = self._cnx.cursor()
        query = "SELECT * FROM palas WHERE nombre = %s"
        cursor.execute(query, (shovel,))
        res = cursor.fetchall()
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