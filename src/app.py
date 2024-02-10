from json import load, dump
from os import path
from time import sleep
from flask import Flask, redirect, render_template, request
from ast import literal_eval

app = Flask(__name__, static_folder="static")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6699)

openapplets = []

appletsvar = load(open("applets.json"))
software = load(open("software.json"))
settings = load(open("settings.json"))

def savesettings():
    with open("settings.json", "w") as f:
        dump(settings, f)

def checkifappletclosed(applet):
    if applet not in openapplets:
        return True
    else:
        return False


def checkifservermandstarted():
    if settings["daemon"] == "":
        try:
            with open(f"{settings['daemon']}servermand.pid") as f:
                if path.isdir(f"/proc/{f.read()}"): 
                    return True
                else:
                    return False
        except FileNotFoundError:
            return False
    else:
        return "nopath"
    
def contactdaemon(command):
    if command == "daemonpath":
        return settings["daemon"]
    if checkifservermandstarted():
        try:
            with open(f"{settings['daemon']}servermand.input", "w") as f:
                f.write(command)
            with open(f"{settings['daemon']}servermand.output", "r") as f:
                sleep(1)
                return f.read()
        except FileNotFoundError:
            print("dERROR")
            return "notstarted"
    elif "nopath":
        return "nopath"
    else:
        return "notstarted"

@app.context_processor
def globalvars():
    return dict(openapplets=openapplets, literal_eval=literal_eval, contactdaemon=contactdaemon)

@app.route("/")
def login():
    return redirect("/applets/")

@app.route("/setdaemonpath/", methods=['POST'])
def setdaemonpath():
    data = dict(request.form)
    daemonpath = ""
    try:
        if data["path"][-1] != "/":
            daemonpath = data["path"] + "/"
        else:
            daemonpath = data["path"]
    except IndexError:
        pass
    if path.exists(daemonpath + "servermand.py") == False:
        return redirect("/applets/settings/daemon/invalidpath/")
    settings["daemon"] = daemonpath
    savesettings()
    return redirect("/applets/settings/daemon")

@app.route("/quit/<applet>/")
def quit(applet):
    try:
        openapplets.remove(applet)
        return redirect("/applets")
    except ValueError:
        return redirect("/applets")

@app.route("/applets/")
def applets():
    appletsdict = {}
    for i, val in enumerate(appletsvar):
        appletsdict[val] = load(open(f"software/{val}/info.json"))["description"]
    return render_template("applets.html", openapplets=openapplets, applets=appletsdict)

@app.route("/applets/<applet>/")
def applet(applet):
    if checkifappletclosed(applet):
        openapplets.append(applet)
    return render_template(f"applets/{applet}/index.html", openapplets=openapplets)
    
@app.route("/applets/<applet>/<menu>/")
def appletmenu(applet, menu):
    return render_template(f"applets/{applet}/{menu}.html", openapplets=openapplets)

@app.route("/applets/<applet>/<menu>/<menu1>/")
def appletmenu1(applet, menu, menu1):
    return render_template(f"applets/{applet}/{menu}-{menu1}.html", openapplets=openapplets)

@app.route("/applets/<applet>/<menu>/<menu1>/<menu2>/")
def appletmenu2(applet, menu, menu1, menu2):
    return render_template(f"applets/{applet}/{menu}-{menu1}-{menu2}.html", openapplets=openapplets)

@app.route("/applets/<applet>/<menu>/<menu1>/<menu2>/<menu3>/")
def appletmenu3(applet, menu, menu1, menu2, menu3):
    return render_template(f"applets/{applet}/{menu}-{menu1}-{menu2}-{menu3}.html", openapplets=openapplets)