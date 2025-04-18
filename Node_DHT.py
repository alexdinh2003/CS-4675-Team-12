import socket
import threading
import time
import hashlib
import random
import sys
from copy import deepcopy
import json
import os
#from handleData import *
from flask import Flask, request
from flask_cors import CORS, cross_origin
from flask import send_from_directory


flask_app = Flask(__name__)
cors = CORS(flask_app)

DATA_FOLDER = "NodeData"
os.makedirs(DATA_FOLDER, exist_ok=True)


@flask_app.route('/api/upload-image', methods=['POST'])
@cross_origin()
def upload_image():
    listing_hash = request.form.get("listing_hash")
    file = request.files.get("file")
    if not listing_hash or not file:
        return {"error":"listing_hash and file required"},400

    node.upload_image_http(listing_hash, file)
    return {"result":"Image uploaded"},200

@flask_app.route('/api/get-listing-by-hash', methods=['GET'])
@cross_origin()
def get_listing_by_hash():
    h = request.args.get("hash")
    if not h:
        return {"error":"hash required"},400

    raw = node.process_requests(f"get_listing_by_hash|{h}")
    try:
        return json.loads(raw), 200
    except:
        return {"error": raw}, 404

@flask_app.route('/api/get-image/<filename>', methods=['GET'])
@cross_origin()
def get_image(filename):
    path = node.get_image_path(filename)
    if not path:
        return {"error":"Not found"},404
    return send_from_directory(DATA_FOLDER, filename)

@flask_app.route('/api/add-listing', methods=['POST'])
@cross_origin()
def add_listing():
    data = request.get_json()
    if not data:
        return {"error":"Invalid JSON"},400

    raw = node.process_requests(f"add_listing|{json.dumps(data)}")
    return {"result": raw},200

@flask_app.route('/api/get-listings', methods=['GET'])
@cross_origin()
def get_listings():
    city = request.args.get("city")
    zipc = request.args.get("zipcode")
    # XOR: exactly one must be provided
    if bool(city) == bool(zipc):
        return {"error":"Provide exactly one of city or zipcode"},400

    if city:
        city = city.lower()
        raw = node.process_requests(f"get_listings_by_city|{city}")
    else:
        raw = node.process_requests(f"get_listings_by_zip|{zipc}")

    # raw is JSON list of listing IDs; if you want _hashes_ instead:
    ids = json.loads(raw)
    hashes = [ str(node.hash(f"listing:{i}")) for i in ids ]
    return {"hashes": hashes},200

@flask_app.route('/api/book-listing', methods=['POST'])
def book_listing():
    data = request.get_json()
    if not data:
        return {"error": "Invalid JSON data"}, 400

    message = f"book_listing|{json.dumps(data)}"
    result = node.process_requests(message)
    return {"result": result}, 200

@flask_app.route('/api/write-review', methods=['POST'])
def write_review():
    data = request.get_json()
    if not data or 'listing_id' not in data or 'review' not in data:
        return {"error": "Invalid JSON data"}, 400

    listing_id = data['listing_id']
    review = data['review']
    message = f"write_review|{listing_id}|{review}"
    result = node.process_requests(message)
    return {"result": result}, 200

@flask_app.route('/api/get-reviews', methods=['GET'])
def get_reviews():
    listing_id = request.args.get("listing_id")
    if not listing_id:
        return {"error": "Listing ID is required"}, 400

    message = f"get_reviews|{listing_id}"
    result = node.process_requests(message)
    return {"result": result}, 200


# # MUST BE DONE VIA FEATURE_FLAG
# @flask_app.route('/get-url', methods=['GET'])
# def get_url():
#     #This becomes the URL of the peer node that the frontend determines the new peer will connect to
#     return json({"url": "http://localhost:5000"})




m = 7
# The class DataStore is used to store the key value pairs at each node

class DataStore:
    def __init__(self):
        self.data = {}
    def insert(self, key, value):
        self.data[key] = value
    def delete(self, key):
        del self.data[key]
    def search(self, search_key):
        # print('Search key', search_key)

        if search_key in self.data:
            return self.data[search_key]
        else:
            # print('Not found')
            print(self.data)
            return None
#Class represents the actual Node, it stores ip and port of a node
class NodeInfo:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
    def __str__(self):
        return self.ip + "|" + str(self.port)
# The class Node is used to manage the each node that, it contains all the information about the node like ip, port,
# the node's successor, finger table, predecessor etc.
class Node:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = int(port)
        self.nodeinfo = NodeInfo(ip, port)
        self.id = self.hash(str(self.nodeinfo))
        self.predecessor = None
        self.successor = None
        self.finger_table = FingerTable(self.id)
        self.data_store = DataStore()
        self.data_folder = DATA_FOLDER

    def hash(self, message: str) -> int:
        '''
        Generates an integer hash using sha256
        '''
        digest = hashlib.sha256(message.encode()).hexdigest()
        digest = int(digest, 16) % pow(2,m)
        return digest

    def upload_image_http(self, listing_hash: str, file_storage):
        path = os.path.join(self.data_folder, file_storage.filename)
        file_storage.save(path)

        # attach filename to the JSON stored under hash:<listing_hash>
        key = f"hash:{listing_hash}"
        raw = self.data_store.data.get(key)
        if raw:
            lj = json.loads(raw)
            imgs = lj.setdefault("images", [])
            if file_storage.filename not in imgs:
                imgs.append(file_storage.filename)
                # write back both hash: and listing:id entries
                self.data_store.data[key] = json.dumps(lj)
                self.data_store.data[f"listing:{lj['id']}"] = json.dumps(lj)
        return True

    def get_image_path(self, filename: str) -> str | None:
        path = os.path.join(self.data_folder, filename)
        return path if os.path.exists(path) else None


    def process_requests(self, message: str) -> str:
        operation = message.split("|")[0]
        args = message.split("|")[1:]
        result = "Done"

        if operation == "add_listing":
            print("Adding listing with args: ", args)

            listing_json = json.loads(args[0])
            listing_id = listing_json["id"]
            key = f"listing:{listing_id}"

            key_hash = self.hash(key)
            print("insertion for ", listing_id, " with hash ", key_hash)
            succ = self.find_successor(key_hash)
            ip, port = self.get_ip_port(succ)

            if ip == self.ip and port == self.port:
                self.data_store.insert(key, json.dumps(listing_json))
                city = listing_json.get("location", "unknown").lower()

                # Zipcode Index
                zipcode = str(int(float(listing_json.get("zipcode", 0))))
                zip_key = f"zipcode:{zipcode}"
                zip_key_hash = self.hash(zip_key)
                zip_succ = self.find_successor(zip_key_hash)
                ip_zip_idx, port_zip_idx = self.get_ip_port(zip_succ)

                if ip_zip_idx == self.ip and port_zip_idx == self.port:
                    zip_list = json.loads(self.data_store.data.get(zip_key, "[]"))
                    if listing_id not in zip_list:
                        zip_list.append(listing_id)
                        self.data_store.data[zip_key] = json.dumps(zip_list)
                else:
                    send_message(ip_zip_idx, port_zip_idx, f"update_zipcode_index|{zipcode}|{listing_id}")

                # City index
                city_key = f"city:{city}"
                city_key_hash = self.hash(city_key)
                city_succ = self.find_successor(city_key_hash)
                ip_city, ip_port = self.get_ip_port(city_succ)

                if ip_city == self.ip and ip_port == self.port:
                    city_list = json.loads(self.data_store.data.get(city_key, "[]"))
                    if listing_id not in city_list:
                        city_list.append(listing_id)
                        self.data_store.data[city_key] = json.dumps(city_list)
                else:
                    send_message(ip_city, ip_port, f"update_city_index|{city}|{listing_id}")

                result = f"Listing {listing_id} added."
            else:
                result = send_message(ip, port, message)

        elif operation == "update_city_index":
            city = args[0].lower()
            listing_id = args[1]
            city_key = f"city:{city}"
            city_list = json.loads(self.data_store.data.get(city_key, "[]"))
            if listing_id not in city_list:
                city_list.append(listing_id)
                self.data_store.data[city_key] = json.dumps(city_list)
            result = f"City index updated for {city}"

        elif operation == "update_zipcode_index":
            zipcode = args[0]
            listing_id = args[1]
            zip_key = f"zipcode:{zipcode}"
            zip_list = json.loads(self.data_store.data.get(zip_key, "[]"))
            if listing_id not in zip_list:
                zip_list.append(listing_id)
                self.data_store.data[zip_key] = json.dumps(zip_list)
            result = f"Zipcode index updated for {zipcode}"

        elif operation == "get_listings_by_city":
            city = args[0].lower()
            city_key = f"city:{city}"
            key_hash = self.hash(city_key)
            succ = self.find_successor(key_hash)
            ip, port = self.get_ip_port(succ)

            if ip == self.ip and port == self.port:
                result = self.data_store.data.get(city_key, "[]")
            else:
                result = send_message(ip, port, message)

        elif operation == "get_listings_by_zip":
            zipcode = args[0]
            key = f"zipcode:{zipcode}"
            key_hash = self.hash(key)

            succ = self.find_successor(key_hash)
            ip, port = self.get_ip_port(succ)

            if ip == self.ip and port == self.port:
                result = self.data_store.data.get(key, "[]")
            else:
                result = send_message(ip, port, message)

        elif operation == "get_listing_by_id":
            id = args[0]
            key = f"listing:{id}"
            keyHash = self.hash(key)

            print("query for ", key, " with hash ", keyHash)
            # Find the appropriate node in the ring
            succ = self.find_successor(int(keyHash))
            ip, port = self.get_ip_port(succ)

            if ip == self.ip and port == self.port:
                raw = self.data_store.data.get(key)
            else:
                raw = send_message(ip, port, f"search_server|{key}")
            print("QUERY - ", id, " about to send: ", raw)

            if not raw or raw == "NOT FOUND":
                return "Listing not found"

            lj = json.loads(raw)
            return lj

        elif operation == "book_listing":
            booking_json = json.loads(args[0])
            booking_id = booking_json["id"]
            key = f"booking:{booking_id}"
            key_hash = self.hash(key)
            succ = self.find_successor(key_hash)
            ip, port = self.get_ip_port(succ)

            if ip == self.ip and port == self.port:
                self.data_store.insert(key, json.dumps(booking_json))
                result = f"Booking {booking_id} added."
            else:
                result = send_message(ip, port, message)

        elif operation == "write_review":
            listing_id = args[0]
            review = args[1]
            key = f"review:{listing_id}"
            key_hash = self.hash(key)
            succ = self.find_successor(key_hash)
            ip, port = self.get_ip_port(succ)

            if ip == self.ip and port == self.port:
                review_list = json.loads(self.data_store.data.get(key, "[]"))
                review_list.append(review)
                self.data_store.data[key] = json.dumps(review_list)
                result = "Review added."
            else:
                result = send_message(ip, port, message)

        elif operation == "get_reviews":
            listing_id = args[0]
            key = f"review:{listing_id}"
            key_hash = self.hash(key)
            succ = self.find_successor(key_hash)
            ip, port = self.get_ip_port(succ)

            if ip == self.ip and port == self.port:
                result = self.data_store.data.get(key, "[]")
            else:
                result = send_message(ip, port, message)

        # Remaining default Chord operations...
        elif operation == 'insert_server':
            data = args[0].split(":")
            key = data[0]
            value = data[1]
            self.data_store.insert(key, value)
            result = 'Inserted'

        elif operation == "delete_server":
            self.data_store.delete(args[0])
            result = 'Deleted'

        elif operation == "search_server":
            data = args[0]
            value = self.data_store.search(data)
            result = value if value else "NOT FOUND"

        elif operation == "send_keys":
            id_of_joining_node = int(args[0])
            result = self.send_keys(id_of_joining_node)

        elif operation == "insert":
            data = args[0].split(":")
            key = data[0]
            value = data[1]
            result = self.insert_key(key, value)

        elif operation == "delete":
            result = self.delete_key(args[0])

        elif operation == "search":
            result = self.search_key(args[0])

        elif operation == "join_request":
            result = self.join_request_from_other_node(int(args[0]))

        elif operation == "find_predecessor":
            result = self.find_predecessor(int(args[0]))

        elif operation == "find_successor":
            result = self.find_successor(int(args[0]))

        elif operation == "get_successor":
            result = self.get_successor()

        elif operation == "get_predecessor":
            result = self.get_predecessor()

        elif operation == "get_id":
            result = self.get_id()

        elif operation == "notify":
            self.notify(int(args[0]), args[1], args[2])
            result = "Notified"
        else:
            result = "Unknown op"


        return str(result)

    def serve_requests(self, conn, addr):
        '''
        The serve_requests fucntion is used to listen to incomint requests on the open port and then reply to them it
        takes as arguments the connection and the address of the connected device.
        '''
        with conn:
            raw = conn.recv(1024)
            if not raw:
                return
            msg = raw.decode('utf-8').strip()
            parts = msg.split("|")
            op = parts[0]

            if op == "upload_image":
                # parts = ["upload_image", listing_hash, filename, filesize]
                _, listing_hash, filename, fs = parts
                file_size = int(fs)
                self._handle_upload_image(conn, listing_hash, filename, file_size)
                return

            if op == "get_image":
                # parts = ["get_image", filename]
                _, filename = parts
                self._handle_get_image(conn, filename)
                return

            # otherwise, delegate to your existing process_requests()
            response = self.process_requests(msg)
            # if you returned bytes, send raw, else utf‑8 encode
            if isinstance(response, bytes):
                conn.sendall(response)
            else:
                conn.sendall(response)


    def _handle_upload_image(self, conn, listing_hash, filename, file_size):
        # read exactly file_size bytes
        received = b''
        while len(received) < file_size:
            chunk = conn.recv(min(4096, file_size - len(received)))
            if not chunk:
                break
            received += chunk

        # save to disk
        path = os.path.join(self.data_folder, filename)
        with open(path, 'wb') as f:
            f.write(received)
        conn.sendall(b"Image uploaded")

    def _handle_get_image(self, conn, filename):
        path = os.path.join(self.data_folder, filename)
        if not os.path.exists(path):
            conn.sendall(b"NOT FOUND")
            return
        with open(path, 'rb') as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                conn.sendall(chunk)


    def start(self):
        '''
        The start function creates 3 threads for each node:
        On the 1st thread the stabilize function is being called repeatedly in a definite interval of time
        On the 2nd thread the fix_fingers function is being called repeatedly in a definite interval of time
        and on the 3rd thread the serve_requests function is running which is continously listening for any new
        incoming requests
        '''
        thread_for_stabalize = threading.Thread(target = self.stabilize)
        thread_for_stabalize.start()
        thread_for_fix_finger = threading.Thread(target=  self.fix_fingers)
        thread_for_fix_finger.start()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.nodeinfo.ip, self.nodeinfo.port))
            s.listen()
            while True:
                conn, addr = s.accept()
                t = threading.Thread(target=self.serve_requests, args=(conn,addr))
                t.start()

    def insert_key(self,key,value):
        '''
        The function to handle the incoming key_value pair insertion request from the client this function searches for the
        correct node on which the key_value pair needs to be stored and then sends a message to that node to store the
        key_val pair in its data_store
        '''
        id_of_key = self.hash(str(key))
        succ = self.find_successor(id_of_key)
        # print("Succ found for inserting key" , id_of_key , succ)
        ip,port = self.get_ip_port(succ)
        send_message(ip,port,"insert_server|" + str(key) + ":" + str(value) )
        return "Inserted at node id " + str(Node(ip,port).id) + " key was " + str(key) + " key hash was " + str(id_of_key)

    def delete_key(self,key):
        '''
        The function to handle the incoming key_value pair deletion request from the client this function searches for the
        correct node on which the key_value pair is stored and then sends a message to that node to delete the key_val
        pair in its data_store.
        '''
        id_of_key = self.hash(str(key))
        succ = self.find_successor(id_of_key)
        # print("Succ found for deleting key" , id_of_key , succ)
        ip,port = self.get_ip_port(succ)
        send_message(ip,port,"delete_server|" + str(key) )
        return "deleted at node id " + str(Node(ip,port).id) + " key was " + str(key) + " key hash was " + str(id_of_key)


    def search_key(self,key):
        '''
        The function to handle the incoming key_value pair search request from the client this function searches for the
        correct node on which the key_value pair is stored and then sends a message to that node to return the value
        corresponding to that key.
        '''
        id_of_key = self.hash(str(key))
        succ = self.find_successor(id_of_key)
        # print("Succ found for searching key" , id_of_key , succ)
        ip,port = self.get_ip_port(succ)
        data = send_message(ip,port,"search_server|" + str(key) )
        return data


    def join_request_from_other_node(self, node_id):
        """ will return successor for the node who is requesting to join """
        return self.find_successor(node_id)

    def join(self,node_ip, node_port):
        '''
        Function responsible to join any new nodes to the chord ring it finds out the successor and the predecessor of the
        new incoming node in the ring and then it sends a send_keys request to its successor to recieve all the keys
        smaller than its id from its successor.
        '''
        data = 'join_request|' + str(self.id)
        succ = send_message(node_ip,node_port,data)
        ip,port = self.get_ip_port(succ)
        self.successor = Node(ip,port)
        self.finger_table.table[0][1] = self.successor
        self.predecessor = None

        if self.successor.id != self.id:
            data = send_message(self.successor.ip , self.successor.port, "send_keys|"+str(self.id))
            # print("data recieved" , data)
            for key_value in data.split(':'):
                if len(key_value) > 1:
                    # print(key_value.split('|'))
                    self.data_store.data[key_value.split('|')[0]] = key_value.split('|')[1]

    def find_predecessor(self, search_id: str) -> str:
        '''
        The find_predecessor function provides the predecessor of any value in the ring given its id.
        '''
        if search_id == self.id:
            return str(self.nodeinfo)
        # print("finding pred for id ", search_id)


        assert self.successor is not None and isinstance(self.successor, Node), f"Successor does not exist for node {self}"



        if self.get_forward_distance(self.successor.id) > self.get_forward_distance(search_id): # Base Case: Are we the predecessor ?
            return self.nodeinfo.__str__()
        else:
            new_node_hop = self.closest_preceding_node(search_id)
            # print("new node hop finding hops in find predecessor" , new_node_hop.nodeinfo.__str__() )
            if new_node_hop is None:
                return "None"
            ip, port = self.get_ip_port(new_node_hop.nodeinfo.__str__())
            if ip == self.ip and port == self.port:
                return self.nodeinfo.__str__()
            data = send_message(ip , port, "find_predecessor|"+str(search_id))
            return data

    def find_successor(self, search_id):
        '''
        The find_successor function provides the successor of any value in the ring given its id.
        '''
        if(search_id == self.id):
            return str(self.nodeinfo)
        # print("finding succ for id ", search_id)
        predecessor = self.find_predecessor(search_id)
        # print("predcessor found is ", predecessor)
        if(predecessor == "None"):
            return "None"
        ip,port = self.get_ip_port(predecessor)
        # print(ip ,port , "in find successor, data of predecesor")
        data = send_message(ip , port, "get_successor") # Note that this returns the direct successor
        return data

    def closest_preceding_node(self, search_id:str) -> "Node":
        closest_node = None
        min_distance = pow(2,m)+1
        for i in list(reversed(range(m))):
            # print("checking hops" ,i ,self.finger_table.table[i][1])
            if  self.finger_table.table[i][1] is not None and self.get_forward_distance_2nodes(self.finger_table.table[i][1].id,search_id) < min_distance  :
                closest_node = self.finger_table.table[i][1]
                min_distance = self.get_forward_distance_2nodes(self.finger_table.table[i][1].id,search_id)
                # print("Min distance",min_distance)

        return closest_node

    def send_keys(self, id_of_joining_node):
        '''
        The send_keys function is used to send all the keys less than equal to the id_of_joining_node to the new node that
        has joined the chord ring.
        '''
        # print(id_of_joining_node , "Asking for keys")
        data = ""
        keys_to_be_removed = []
        for keys in self.data_store.data:
            key_id = self.hash(str(keys))
            if self.get_forward_distance_2nodes(key_id , id_of_joining_node) < self.get_forward_distance_2nodes(key_id,self.id):
                data += str(keys) + "|" + str(self.data_store.data[keys]) + ":"
                keys_to_be_removed.append(keys)
        for keys in keys_to_be_removed:
            self.data_store.data.pop(keys)
        return data


    def stabilize(self):
        '''
        The stabilize function is called in repetitively in regular intervals as it is responsible to make sure that each
        node is pointing to its correct successor and predecessor nodes. By the help of the stabilize function each node
        is able to gather information of new nodes joining the ring.
        '''
        while True:
            if self.successor is None:
                time.sleep(10)
                continue
            data = "get_predecessor"

            if self.successor.ip == self.ip  and self.successor.port == self.port:
                time.sleep(10)
            result = send_message(self.successor.ip , self.successor.port , data)
            if result == "None" or len(result) == 0:
                send_message(self.successor.ip , self.successor.port, "notify|"+ str(self.id) + "|" + self.nodeinfo.__str__())
                continue

            # print("found predecessor of my sucessor", result, self.successor.id)
            ip , port = self.get_ip_port(result)
            result = int(send_message(ip,port,"get_id"))
            if self.get_backward_distance(result) > self.get_backward_distance(self.successor.id):
                # print("changing my succ in stablaize", result)
                self.successor = Node(ip,port)
                self.finger_table.table[0][1] = self.successor
            send_message(self.successor.ip , self.successor.port, "notify|"+ str(self.id) + "|" + self.nodeinfo.__str__())
            print("===============================================")
            print("STABILIZING")
            print("===============================================")
            print("ID: ", self.id)
            if self.successor is not None:
                print("Successor ID: " , self.successor.id)
            if self.predecessor is not None:
                print("predecessor ID: " , self.predecessor.id)
            print("===============================================")
            print("=============== FINGER TABLE ==================")
            self.finger_table.print()
            print("===============================================")
            print("DATA STORE")
            print("===============================================")
            print(str(self.data_store.data))
            print("===============================================")
            print("+++++++++++++++ END +++++++++++++++++++++++++++\n\n\n")
            time.sleep(10)

    def notify(self, node_id , node_ip , node_port):
        '''
        Recevies notification from stabilized function when there is change in successor
        '''
        if self.predecessor is not None:
            if self.get_backward_distance(node_id) < self.get_backward_distance(self.predecessor.id):
                # print("someone notified me")
                # print("changing my pred", node_id)
                self.predecessor = Node(node_ip,int(node_port))
                return
        if self.predecessor is None or self.predecessor == "None" or ( node_id > self.predecessor.id and node_id < self.id ) or ( self.id == self.predecessor.id and node_id != self.id) :
            # print("someone notified me")
            # print("changing my pred", node_id)
            self.predecessor = Node(node_ip,int(node_port))
            if self.id == self.successor.id:
                # print("changing my succ", node_id)
                self.successor = Node(node_ip,int(node_port))
                self.finger_table.table[0][1] = self.successor

    def fix_fingers(self):
        '''
        The fix_fingers function is used to correct the finger table at regular interval of time this function waits for
        10 seconds and then picks one random index of the table and corrects it so that if any new node has joined the
        ring it can properly mark that node in its finger table.
        '''
        while True:

            random_index = random.randint(1,m-1)
            finger = self.finger_table.table[random_index][0]
            # print("in fix fingers , fixing index", random_index)
            data = self.find_successor(finger)
            if data == "None":
                time.sleep(10)
                continue
            ip,port = self.get_ip_port(data)
            self.finger_table.table[random_index][1] = Node(ip,port)
            time.sleep(10)
    def get_successor(self):
        '''
        This function is used to return the successor of the node
        '''
        if self.successor is None:
            return "None"
        return self.successor.nodeinfo.__str__()
    def get_predecessor(self):
        '''
        This function is used to return the predecessor of the node

        '''
        if self.predecessor is None:
            return "None"
        return self.predecessor.nodeinfo.__str__()
    def get_id(self):
        '''
        This function is used to return the id of the node

        '''
        return str(self.id)
    def get_ip_port(self, string_format):
        '''
        This function is used to return the ip and port number of a given node

        '''
        return string_format.strip().split('|')[0] , int(string_format.strip().split('|')[1])

    def get_backward_distance(self, node1):

        disjance = 0
        if(self.id > node1):
            disjance =   self.id - node1
        elif self.id == node1:
            disjance = 0
        else:
            disjance=  pow(2,m) - abs(self.id - node1)
        # print("BACK ward distance of ",self.id,node1 , disjance)
        return disjance

    def get_backward_distance_2nodes(self, node2, node1):
        distance = 0
        if(node2 > node1):
            distance =   node2 - node1
        elif node2 == node1:
            distance = 0
        else:
            distance=  pow(2,m) - abs(node2 - node1)
        # print("BACK word distance of ",node2,node1 , distance)
        return distance

    def get_forward_distance(self,nodeid, nodeid2 = None):
        return pow(2,m) - self.get_backward_distance(nodeid)


    def get_forward_distance_2nodes(self,node2,node1):
        return pow(2,m) - self.get_backward_distance_2nodes(node2,node1)
# The class FingerTable is responsible for managing the finger table of each node.
class FingerTable:
    '''
    The __init__ fucntion is used to initialize the table with values when
    a new node joins the ring
    '''
    def __init__(self, my_id):
        self.table = []
        for i in range(m):
            x = pow(2, i)
            entry = (my_id + x) % pow(2,m)
            node = None
            self.table.append([entry, node])

    def print(self):
        '''
        The print function is used to print the finger table of a node.
        '''
        for index, entry in enumerate(self.table):
            if entry[1] is None:
                print('Entry: ', index, " Interval start: ", entry[0]," Successor: ", "None")
            else:
                print('Entry: ', index, " Interval start: ", entry[0]," Successor: ", entry[1].id)


def send_message(ip, port, message):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    #
    # delay
    #
    # connect to server on local computer
    s.connect((ip,port))
    s.send(message.encode('utf-8'))
    data = s.recv(1024)
    s.close()
    return data.decode("utf-8")

def start_flask_app():
    flask_app.run(host="0.0.0.0", port=5000, debug=False)



ip = "127.0.0.1"
#flask_thread = threading.Thread(target=start_flask_app)
#flask_thread.daemon = True  # Daemon thread will exit when the main program exits
#flask_thread.start()
# This if statement is used to check if the node joining is the first node of the ring or not

if len(sys.argv) == 3:
    print("JOINING RING")
    node = Node(ip, int(sys.argv[1]))

    node.join(ip,int(sys.argv[2]))
    node.start()

if len(sys.argv) == 2:
    assert(len(sys.argv) >= 1)
    print(f"CREATING RING in {ip}:{sys.argv[1]}")
    node = Node(ip, int(sys.argv[1]))

    node.predecessor = Node(ip,node.port)
    node.successor = Node(ip,node.port)
    node.finger_table.table[0][1] = node
    node.start()
