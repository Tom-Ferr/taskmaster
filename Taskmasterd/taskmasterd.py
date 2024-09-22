from flask import Flask, jsonify, request, render_template_string
from utils.start import start_program
from utils.stop import stop_program
from utils.update import update_confs
from utils.read import  read_confs
from utils.get_status import get_status
from utils.privilege_descalation import privilege_descalation
from utils.daemonize import daemonize
from utils.insert_logs import insert_logs
import threading
import signal
import os
import sys
import copy


if __name__ == "__main__":

    readed, _ = read_confs({})
    if not readed:
        sys.exit(1)
    daemonize()
    privilege_descalation()
    app = Flask(__name__)
    procs = {}


    confs = copy.deepcopy(readed)
    insert_logs("INFO", f"taskmasterd started with pid {os.getpid()}", confs)

    for prog in confs['programs'].keys():
        procs[prog] = {}
        if confs['programs'][prog].get('autostart', True):
            start_program(prog, confs, procs)
        
    def sigint_handler(sig, frame):
        for progs in procs.values():
            for p in progs.values(): 
                p['process'].terminate()
        insert_logs("CRIT", "the taskmasterd is shuting down", confs)
        sys.exit()

    def sighup_handler(sig, frame):
        global readed
        global confs
        ret, _ = read_confs(confs)
        if ret:
            insert_logs("WARN", "the configuration file was reread", confs)
            readed = ret
        update_confs(confs, procs, readed)

    signal.signal(signal.SIGINT, sigint_handler)
    signal.signal(signal.SIGHUP, sighup_handler)
    
    @app.route('/start', methods=['POST'])
    def start():
        json = request.get_json()
        progs = json.get('program').split() 

        for prog in progs:
            if not prog in confs["programs"].keys():
                return jsonify({"Response": "ko", "program":  prog}), 400
            start_program(prog, confs, procs)
        
        response = {"Response": "ok"}
        return jsonify(response), 200
    
    @app.route('/stop', methods=['POST'])
    def stop():
        json = request.get_json()
        progs = json.get('program').split() 

        for prog in progs:
            if not prog in confs["programs"].keys():
                return jsonify({"Response": "ko", "program":  prog}), 400
            stop_program(prog, confs, procs)

        response = {"Response": "ok"}
        return jsonify(response), 200
    
    @app.route('/restart', methods=['POST'])
    def restart():
        global confs

        json = request.get_json()
        progs = json.get('program').split() 

        for prog in progs:
            if not prog in confs["programs"].keys():
                return jsonify({"Response": "ko", "program":  prog}), 400
            autorestart = confs['programs'][prog].get('autorestart', None)
            if autorestart != None:
                confs['programs'][prog]['autorestart'] = False
                stop_program(prog, confs, procs)
                start_program(prog, confs, procs)
                confs['programs'][prog]['autorestart'] = autorestart

        response = {"Response": "ok"}
        return jsonify(response), 200
    
    @app.route('/status', methods=['POST'])
    def status():
        # json = request.get_json()
        # prog = json.get('program')

        response = {}
        for prog in confs['programs'].keys():
            status = {}
            for pid in procs[prog].keys():
                status[get_status(procs[prog][pid]['status'])] = status.get(get_status(procs[prog][pid]['status']), 0) + 1
            response[prog] = status

        # response = {procs[prog][pid]['name']: get_status(procs[prog][pid]['status']) for pid in procs.get(prog, {}).keys()}

        return jsonify(response), 200
    
    @app.route('/pid', methods=['GET'])
    def get_pid():

        pid = os.getpid()
        
        response = {"Response": pid}
        return jsonify(response), 200
    
    @app.route('/reread', methods=['GET'])
    def reread():
        global readed
        global confs

        ret, err_list = read_confs(confs)
        
        if ret:
            insert_logs("WARN", "the configuration file was reread", confs)
            readed = ret
            response = {"Response":"ok"}
        else:
            err = []
            for e in err_list:
                err.append(e.error_text)
            response = {"errors": err}
            return jsonify(response), 502

        return jsonify(response), 200
    
    @app.route('/update', methods=['GET'])
    def update():
        global readed
        global confs
        for name, progs in procs.items():
            for p in progs.values():
                p['default'] = False
            stop_program(name, confs, procs)
        procs.clear()
        confs = copy.deepcopy(readed)
        for prog in confs['programs'].keys():
            procs[prog] = {}
            start_program(prog, confs, procs)

        insert_logs("WARN", "The processes have been updated", confs)
        response = {"Response": "ok"}
        return jsonify(response), 200


    @app.route('/logs', methods=['GET'])
    def logs():
        path = confs.get("taskmaster", {}).get("logfile", None)

        if path is None:
            return "'logfile' field not found in configuration file", 404

        try:
            file_lock = threading.Lock()
            with file_lock:
                with open(path, 'r') as f:
                    file_content = f.read()
        except FileNotFoundError:
            return f"The {path} file was not found", 404
        except Exception as e:
            return f"Error reading file: {str(e)}", 500

        html_template = """
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Logs</title>
        </head>
        <body>
            <h1>Logs:</h1>
            <pre>{{ file_content }}</pre>
        </body>
        </html>
        """
        
        return render_template_string(html_template, file_content=file_content)

    app.run(host="127.0.0.1", port=4242)
