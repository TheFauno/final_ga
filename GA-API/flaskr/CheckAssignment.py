import Db

def checkAssignment(simulation_name_truck):

    #truck
    askingTruck = simulation_name_truck.split(".")[0]
    conn = Db.Connect()
    truckId = conn.findTruckByName(askingTruck)
    assignment = conn.hasAssignment(truckId)
    if assignment:
        conn.updateAssignment(truckId)
        assignment = conn.getLoadName(assignment[0][0])[0]
    conn.disconnect()
    return assignment