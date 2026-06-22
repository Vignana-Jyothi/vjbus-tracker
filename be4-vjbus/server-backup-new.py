import eventlet
eventlet.monkey_patch()
import geopy
from flask import Flask, request, jsonify,render_template, json
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, leave_room, send
import math
from geopy.distance import geodesic
from datetime import datetime
import sqlite3
import socket
import sys
import os
import threading
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()



user_count={"count":0}
PORT = 6104
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0

if is_port_in_use(PORT):
    print(f"❌ Flask is already running on port {PORT}. Exiting.")
    sys.exit(1)

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

latest_location = {}
connected_routes = {}
tracking_status = {}
route_subscriptions = {}
all_routes = []
yet_to_be = []
all_ids={}
all_uis={}
all_start_locations=json.loads(os.getenv("all_start_locations"))
all_start_timings=json.loads(os.getenv("all_start_timings"))
#database connections
def init_db():
    conn = sqlite3.connect("database.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room TEXT NOT NULL,
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    conn = sqlite3.connect("database.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            route_number TEXT, 
            log_date date, 
            log_time time
        )
    """)
    conn.commit()
    conn.close()
    
    conn = sqlite3.connect("database.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_count ( 
            Date date, 
            Users_count integer
        )
    """)
    conn.commit()
    conn.close()
    
init_db()



#functions to be used later

def auto_start():
    while True:
        now_time = datetime.now()
        current_time_str = now_time.strftime("%H:%M")
        for key in all_start_locations.keys():
            start_time = all_start_timings[key]
            if current_time_str == start_time:
                print(f"Triggering start_locations for {key} at {now_time.strftime('%H:%M:%S')}")
                if key in all_ids:
                    start_locations(all_ids[key])
        time.sleep(25)  # Check every 25 seconds

# Start the scheduling thread
thread = threading.Thread(target=auto_start, daemon=True)
thread.start()


def is_in_college(lon, lat):
    COLLEGE=(17.539873, 78.386514)
    # COLLEGE = (17.5479048, 78.394546)
    return geodesic(COLLEGE, (lat, lon)).meters <= 400

def log_data(route_id):
    try:
        conn = sqlite3.connect("database.db", check_same_thread=False)
        cursor = conn.cursor()
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")

        # Step 1: Check if the bus is already logged today
        cursor.execute("""
            SELECT 1 FROM logs WHERE route_number = ? AND log_date = ?
        """, (route_id, current_date))

        exists = cursor.fetchone()  # Fetch result (None if f)

        # Step 2: If not logged, insert the new log
        if not exists:
            cursor.execute("""
                INSERT INTO logs 
                VALUES (?, ?, ?)
            """, (route_id, current_date, current_time))
            conn.commit()
            conn.close()
            print(f"Bus {route_id} logged at {current_time}")
            log_user_count()
    except sqlite3.Error as e:
        print(f"Error logging data: {e}")


def log_user_count():
    try:
        conn = sqlite3.connect("database.db", check_same_thread=False)
        cursor = conn.cursor()
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Step 1: Check if today's count exists
        cursor.execute("""
            SELECT COALESCE(Users_count, 0) FROM user_count WHERE Date = ?
        """, (current_date,))
        
        result = cursor.fetchone()
        old_count = result[0] if result else 0 
        if old_count!=0:
            s=old_count + user_count["count"]
            cursor.execute("""
                UPDATE user_count set Users_count= ? where date=?   
            """, (s,current_date))
        else:
            cursor.execute("""
                INSERT INTO user_count (Date, Users_count) VALUES (?, ?)
            """, (current_date, old_count + user_count["count"]))

            user_count["count"] = 0  # Reset count
        # Commit changes
        conn.commit()
        conn.close()

    except sqlite3.Error as e:
        print(f"Error logging data: {e}")

def get_key_by_value(d, target_value):
    for key, value in d.items():
        if value == target_value:
            return key
    return None

def start_locations(socket_id):
    if not socket_id:
        response = {"status": "error", "message": "No socket ID provided","socket_id": request.sid }
        socketio.emit("admin_start_location_response", response, room=request.sid)
        return
    
    print(f"Admin start location request for socket: {socket_id}")

    # if socket_id not in all_uis.values():
        # response = {"status": "error", "message": f"Socket ID {socket_id} not found"}
        # socketio.emit("admin_start_location_response", response, room=request.sid)
        # return
    
    # Get the route ID for this socket
    route_id = get_key_by_value(all_ids, socket_id)    
    
    # Send Start to this specific socket
    print(f"Sending start to socket {socket_id} (route {route_id})")
    socketio.emit("admin_start", {
        "message": "Started by administrator",
        "socket_id": socket_id,
        "route_id": route_id
    }, room=socket_id)

    # Send response back to admin
    response = {
        "status": "success", 
        "message": f"Start signal sent to socket {socket_id} (route {route_id})"
    }
    socketio.emit("admin_start_location_response", response)


#Socket IO events
@socketio.on("connect")
def handle_connect():
    route_id = request.args.get("route_id", "Unkown")
    role= request.args.get("role")
    sid= request.sid
    if role in ["Student"]:
        user_count["count"] += 1    
    # Announce connection
    socketio.emit("server_message", {"message": f"A {role} connected for Route {route_id} connected!"})
    route_id=None

#Socket IO events
@socketio.on("connect")
def handle_connect():
    route_id = request.args.get("route_id", "Unkown")
    role= request.args.get("role")
    sid= request.sid
    if role in ["Driver"]:
        print(f"New connection: SID={sid}, Role={role}, Route ID={route_id}")
    print("Req: ",request.args)
    

    print("All IDs: ",all_ids)
    print("All UIs: ",all_uis)

    # Debug info - print all connections
    # print(f"Current connections: {connected_routes}")
    
    # Track user count
    user_count["count"] += 1   
    
    # Announce connection
    socketio.emit("server_message", {"message": f"Route {route_id} connected!"})
    route_id=None

@socketio.on("connected")
def handle_driver_connect(data):
    route_id = data["route_id"]
    sid = data["socket_id"]
    role = data["role"]
    #Add for other roles in future
    if role not in ["Driver"]:
        print(f"Invalid role {role} for driver connection. Expected 'Driver'.")
        return
    else:
        # if route_id not in all_uis.keys():
            print(f"Driver connected: SID={sid}, Route ID={route_id}")
            key= get_key_by_value(all_uis, sid)
            if key!=None:
                socketio.emit("server_message", {"message": f"Route {key} already connected!", "status": False})
            all_uis[route_id] = sid
            print("All UIs: ",all_uis)
    socketio.emit("server_message", {"message": f"Route {route_id} connected!"})


@socketio.on("check_location")
def handle_check_location(data):
    try:
        print("Received check_location data:  ",data)
        route_id = data.get("route_id")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        heading = data.get("heading")  # New field
        status = data.get("status")  # New field
        sid=data.get("socket_id")

        driver_location = (latitude, longitude)
        tar_loc=(all_start_locations[route_id][0], all_start_locations[route_id][1])
        distance = geodesic(driver_location, tar_loc).meters

        # print("All Routes:  ",all_routes)
        existing_route = next((r for r in yet_to_be if r["route_id"] == route_id), None)
        # print("latest locations:  ",latest_location)
        if not existing_route:
            # Add only once
            yet_to_be.append({
                "route_id": route_id,
                "latitude": latitude,
                "longitude": longitude,
                "heading": heading,
                "status": status,
                "socketId": sid
            })


        elif existing_route:
            if status != "checking":
                yet_to_be.remove(existing_route)
            else:
                existing_route["latitude"] = latitude
                existing_route["longitude"] = longitude
                existing_route["heading"] = heading
                existing_route["status"] = status
                existing_route["socketId"] = sid
        if distance <= 12500:
            yet_to_be.remove(existing_route)
            socketio.emit("start_now", {'message': 'You are in the designated area. Start broadcasting.'}, room=sid)
            print(f"✅ Driver {sid} is in the zone. Sending 'start_now' command.")

        socketio.emit("yet_to_be_bradcasted", {
            "route_id": route_id,
            "latitude": latitude,
            "longitude": longitude,
            "heading": heading,  # Send heading to clients
            "status": status  # Send status to clients
        })
    except KeyError as e:
        print(f"Error: Missing key {e} in 'check_location' data from {sid}")
    except Exception as e:
        print(f"An unexpected error occurred in handle_check_location: {e}")

@socketio.on("location_update")
def handle_location_update(data):
    print("Received location update:  ",data)
    route_id = data.get("route_id")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    heading = data.get("heading")  # New field
    status = data.get("status")  # New field
    sid=data.get("socket_id")
    
    # print("All Routes:  ",all_routes)
    existing_route = next((r for r in all_routes if r["route_id"] == route_id), None)
    # print("latest locations:  ",latest_location)
    if not existing_route and status != "stopped":
        # Add only once
        all_routes.append({
            "route_id": route_id,
            "latitude": latitude,
            "longitude": longitude,
            "heading": heading,
            "status": status,
            "socketId": sid
        })


    elif existing_route:
        if status == "stopped":
            all_routes.remove(existing_route)
        else:
            existing_route["latitude"] = latitude
            existing_route["longitude"] = longitude
            existing_route["heading"] = heading
            existing_route["status"] = status
            existing_route["socketId"] = sid
    # Emit updated data to all connected clients
    socketio.emit("location_update", {
        "route_id": route_id,
        "latitude": latitude,
        "longitude": longitude,
        "heading": heading,  # Send heading to clients
        "status": status  # Send status to clients
    })
    
    if is_in_college(longitude, latitude):
        print(f"Bus {route_id} is in college")
        log_data(route_id)
        # handle_admin_disconnect_socket({ "socket_id": all_ids[route_id] })

    return {"status": "received"}

@socketio.on("final_update")
def handle_final_update(data):
    print("Received location update in final update:  ",data)
    route_id = data.get("route_id")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    heading = data.get("heading")  # New field
    status = data.get("status")  # New field
    sid=data.get("socket_id")
    reason = data.get("reason")
    
    # print("All Routes:  ",all_routes)
    existing_route = next((r for r in all_routes if r["route_id"] == route_id), None)
    if existing_route:
        all_routes.remove(existing_route)
    # Emit updated data to all connected clients
    socketio.emit("location_update", {
        "route_id": route_id,
        "latitude": latitude,
        "longitude": longitude,
        "heading": heading,  # Send heading to clients
        "status": "stopped"  # Send status to clients
    })
    tracking_status[sid] = "stopped"
    if is_in_college(longitude, latitude):
        print(f"Bus {route_id} is in college")
        log_data(route_id)

    return {"status": "received"}


@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected",request)
    session_id = request.sid
    route_id = request.args.get("route_id", "Unkown")
    role= request.args.get("role")
    print(f"Session {session_id} disconnected. Route ID: {route_id}, Role: {role}")
    # Remove from connected_routes & tracking_status
    route_id = connected_routes.pop(session_id, None)
    tracking_status.pop(session_id, None)

    # Remove from route_subscriptions
    if route_id and route_id in route_subscriptions:
        if session_id in route_subscriptions[route_id]:
            route_subscriptions[route_id].remove(session_id)

    if route_id and all_ids.get(route_id) == session_id:
        del all_ids[route_id]
    # If this session_id was the UI for the route
    if route_id and all_uis.get(route_id) == session_id:
        del all_uis[route_id]

    # for Driver-UI
    if role=="Driver":
        user_count["count"] -= 1
    print(f"All IDs: {all_ids}")
    print(f"All UIs: {all_uis}")

    socketio.emit("server_message", {"message": f"Route {route_id or 'Unknown'} disconnected!"})


@socketio.on("admin_disconnect_socket")
def handle_admin_disconnect_socket(data):
    socket_id = data.get("socket_id")    
    if not socket_id:
        print(f"Requested for {socket_id} but not found")
        response = {"status": "error", "message": "No socket ID provided","socket_id": request.sid }
        socketio.emit("admin_disconnect_response", response, room=request.sid)
        return
    
    # Debug info
    print(f"Admin disconnect request for socket: {socket_id}")
    
    # Check if this socket exists in our connections
    # all_id
    temp=[]
    for i in all_routes:
        temp.append(i["socketId"])
    if socket_id not in temp:
        response = {"status": "error", "message": f"Socket ID {socket_id} not found"}
        socketio.emit("admin_disconnect_response", response, room=request.sid)
        return
    
    # Get the route ID for this socket
    route_id = connected_routes.get(socket_id)
    
    # Send force disconnect to this specific socket
    print(f"Sending force_disconnect to socket {socket_id} (route {route_id})")
    socketio.emit("admin_stop", {
        "message": "Disconnected by administrator",
        "socket_id": socket_id,
        "route_id": route_id
    }, room=socket_id)
    
    # Update tracking status for this socket
    if socket_id in tracking_status:
        tracking_status[socket_id] = "stopped"
    
    # Update the status in latest_location if it exists
    if route_id in latest_location:
        latest_location[route_id]["status"] = "stopped"
        if route_id in all_routes:
            all_routes.remove(route_id)
        # Broadcast the update to all clients
        socketio.emit("location_update", {
            "route_id": route_id, 
            **latest_location[route_id], 
            "status": "stopped"
        })
    
    # Send response back to admin
    response = {
        "status": "success", 
        "message": f"Disconnect signal sent to socket {socket_id} (routkoe {route_id})"
    }
    socketio.emit("admin_disconnect_response", response)

@socketio.on("admin_start_location")
def handle_admin_start_location(data):
    socket_id = data.get("socket_id")
    if not socket_id:
        response = {"status": "error", "message": "No socket ID provided","socket_id": request.sid }
        socketio.emit("admin_start_location_response", response, room=request.sid)
        return
    
    print(f"Admin start location request for socket: {socket_id}")

    # if socket_id not in all_uis.values():
        # response = {"status": "error", "message": f"Socket ID {socket_id} not found"}
        # socketio.emit("admin_start_location_response", response, room=request.sid)
        # return
    
    # Get the route ID for this socket
    route_id = get_key_by_value(all_uis, socket_id)    
    
    # Send Start to this specific socket
    print(f"Sending start to socket {socket_id} (route {route_id})")
    socketio.emit("admin_start", {
        "message": "Started by administrator",
        "socket_id": socket_id,
        "route_id": route_id
    }, room=socket_id)

    # Send response back to admin
    response = {
        "status": "success", 
        "message": f"Start signal sent to socket {socket_id} (route {route_id})"
    }
    
    socketio.emit("admin_start_location_response", response)


# ✅ JOIN ROOM + LOAD HISTORY
@socketio.on("join_room")
def handle_join(data):
    room = data["room"]
    sender = data["sender"]
    join_room(room)
    send({"sender": "System", "message": f"{sender} joined {room}"}, room=room)

    # Send chat history only to the joining client
    conn = sqlite3.connect("database.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT sender, message, timestamp FROM chat WHERE room = ? ORDER BY timestamp ASC", (room,))
    messages = [{"sender": row[0], "message": row[1], "timestamp": row[2]} for row in cursor.fetchall()]
    conn.close()
    socketio.emit("chat_history", {"room": room, "messages": messages}, room=request.sid)

# ✅ LEAVE ROOM
@socketio.on("leave_room")
def handle_leave(data):
    room = data["room"]
    sender = data["sender"]
    leave_room(room)
    send({"sender": "System", "message": f"{sender} left {room}"}, room=room)

# ✅ SEND MESSAGE
@socketio.on("send_message")
def handle_message(data):
    room = data["room"]
    sender = data["sender"]
    message = data["message"]

    conn = sqlite3.connect("database.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat (room, sender, message) VALUES (?, ?, ?)", (room, sender, message))
    conn.commit()
    conn.close()

    socketio.emit("chat_message", {
        "sender": sender,
        "message": message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }, room=room)

#New http to socket

@socketio.on("all_uis")
def get_all_uis(data=None):
    only_uis={}
    for route in all_uis.keys():
        if route not in all_ids.keys():
            only_uis[route] = all_uis[route]
    return only_uis


@socketio.on("all_connections")
def get_all_connections(data=None):
    connections = []
    for route in all_routes:
        route.update({
            "socketId": route.get("socketId"),
            "route_id": route.get("route_id"),
            "status": route.get("status"),
            "latitude": route.get("latitude"),
            "longitude": route.get("longitude")
        })
        connections.append(route)
    for route in yet_to_be:
        route.update({
            "socketId": route.get("socketId"),
            "route_id": route.get("route_id"),
            "status": route.get("status"),
            "latitude": route.get("latitude"),
            "longitude": route.get("longitude")
        })
        connections.append(route)
    # print("All Connections: ", connections)
    return connections  # This sends data via the Socket.IO callback

@socketio.on("all_locations")
def get_all_locations():
    # print("All Locations: ", all_routes)
    return all_routes

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=PORT, debug=True)