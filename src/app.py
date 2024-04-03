#!/usr/bin/env python3

from zipfile import ZipFile
from json import load, dump
from os import path, mkdir, remove, listdir
from shutil import move, copy
from time import sleep
from flask import Flask, redirect, render_template, request
from logging import getLogger
from ast import literal_eval
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder="static")
log = getLogger("werkzeug")
log.disabled = True

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6699)

openapplets = []

version = "0.0-prealpha.0"
appletsvar = load(open("applets.json"))
software = load(open("software.json"))
settings = load(open("settings.json"))
rebootreasons = []

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
            return "notstarted"
    elif "nopath":
        return "nopath"
    else:
        return "notstarted"

def dictify(dictin):
    try:
        return literal_eval(dictin)
    except ValueError:
        return "notstarted"
    except SyntaxError:
        return "notstarted"
    
def getsoftwareinfo(software):
    applets = load(open(f"applets.json"))
    info = load(open(f"software/{software}/info.json"))
    info["installedfrom"] = load(open("software.json"))[software]
    if software in applets:
        info["hasapplet"] = True
    return info

@app.context_processor
def globalvars():
    return dict(openapplets=openapplets, dictify=dictify, contactdaemon=contactdaemon, rebootreasons=rebootreasons, getsoftwareinfo=getsoftwareinfo, installedsoftware=software, getvars=request.args, formvars=request.form, servermanversion=version)

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

@app.route("/applyinternetsettings/", methods=['POST'])
def applyinternetsettings():
    data = dict(request.form)
    response = contactdaemon(f"internet set {str(data).replace(' ', '')}")
    while response == "loading":
        if response == "ok":
           pass
    global rebootreasons
    rebootreasons.append("internetchange")
    return redirect("/applets/settings/internet")

@app.route("/uploadsoftware", methods=['POST'])
def uploadfile():
    if request.method == 'POST':
        f = request.files["file"]
        print(f)
        try:
            f.save("temp/softwaretoinstall.zip")
        except IsADirectoryError:
            return redirect("/renderapplet/settings/installedsoftware-notavalidfile")
        with ZipFile("temp/softwaretoinstall.zip") as z:
            try:
                info = literal_eval(z.read("info.json").decode())
                return redirect(f"/renderapplet/settings/installedsoftware-softwareinfo?name={info['name']}&version={info['version']}&summary={info['summary']}&description={info['description']}")
            except KeyError:
                return redirect("/renderapplet/settings/installedsoftware-notavalidfile")
    else:
        return redirect("/")
    
@app.route("/installsoftware")
def installsoftware():
    global softwarename
    with ZipFile("temp/softwaretoinstall.zip") as z:
        softwarename = literal_eval(z.read("info.json").decode())['name'].lower().replace(" ", "-")
        mkdir(f"software/{softwarename}")
        mkdir(f"templates/applets/{softwarename}")
        z.extractall("temp")
    remove("temp/softwaretoinstall.zip")
    for file in listdir("temp/html/"):
        move(f"temp/html/{file}", f"templates/applets/{softwarename}")
    for file in listdir("temp/"):
        move(f"temp/{file}", f"software/{softwarename}")
    software[softwarename] = "Software Installer"
    with open("software.json", "w") as f:
        dump(software, f)
    appletsvar.insert(softwarename)
    with open("applets.json", "w") as f:
        dump(appletsvar, f)
    return redirect("/renderapplet/settings/installedsoftware")
    

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
    return render_template(f"renderapplet.html", openapplets=openapplets, applettorender=applet)

@app.route("/renderapplet/<applet>/<file>", methods=['GET', 'POST'])
def renderapplet(applet, file):
    return render_template(f"applets/{applet}/{file}.html")
    
# @app.route("/applets/<applet>/<menu>/", methods=['GET', 'POST'])
# def appletmenu(applet, menu):
#     if checkifappletclosed(applet):
#         openapplets.append(applet)
#     return render_template(f"applets/{applet}/{menu}.html", openapplets=openapplets)

# @app.route("/applets/<applet>/<menu>/<menu1>/", methods=['GET', 'POST'])
# def appletmenu1(applet, menu, menu1):
#     if checkifappletclosed(applet):
#         openapplets.append(applet)
#     return render_template(f"applets/{applet}/{menu}-{menu1}.html", openapplets=openapplets)

# @app.route("/applets/<applet>/<menu>/<menu1>/<menu2>/", methods=['GET', 'POST'])
# def appletmenu2(applet, menu, menu1, menu2):
#     if checkifappletclosed(applet):
#         openapplets.append(applet)
#     return render_template(f"applets/{applet}/{menu}-{menu1}-{menu2}.html", openapplets=openapplets)

# @app.route("/applets/<applet>/<menu>/<menu1>/<menu2>/<menu3>/", methods=['GET', 'POST'])
# def appletmenu3(applet, menu, menu1, menu2, menu3):
#     if checkifappletclosed(applet):
#         openapplets.append(applet)
#     return render_template(f"applets/{applet}/{menu}-{menu1}-{menu2}-{menu3}.html", openapplets=openapplets)