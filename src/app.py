#!/usr/bin/env python3

from zipfile import ZipFile, BadZipFile
from json import load, dump
from os import path, mkdir, remove, listdir, rmdir, popen
from shutil import move, copy, rmtree
from time import sleep
from flask import Flask, redirect, render_template, request, send_from_directory
from logging import getLogger
from ast import literal_eval
from pathlib import Path
from requests import get

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
permissions = load(open("permissions.json"))
rebootreasons = []

def save(thing):
    match thing:
        case "settings":
            with open("settings.json", "w") as f:
                dump(settings, f)
        case "applets":
            with open("applets.json", "w") as f:
                dump(appletsvar, f)
        case "software":
            with open("software.json", "w") as f:
                dump(software, f)
        case "permissions":
            with open("permissions.json", "w") as f:
                dump(permissions, f)

def run(command: str):
    return str(popen(command).read())

def checkifappletclosed(applet):
    if applet not in openapplets:
        return True
    else:
        return False

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
    return dict(rebootreasons=rebootreasons, getsoftwareinfo=getsoftwareinfo, installedsoftware=software, getvars=request.args, formvars=request.form, servermanversion=version)

@app.route("/")
def login():
    return redirect("/applets/")

@app.route("/applyinternetsettings/", methods=['POST'])
def applyinternetsettings():
    newips = dict(request.form)
    for ip in newips:
        ip = ip.replace(".", " ").split()
        thingtoset = ip[1]
        interface = ip[0]
        ip = newips[".".join(ip)]
        if thingtoset == "ip":
            run(f"ip addr replace {ip}/24 dev {interface}")
        elif thingtoset == "gateway":
            oldgateway = run(f'ip route show 0.0.0.0/0 dev {interface} | cut -d " " -f3').replace('\n', '')
            run(f"ip route delete default via {oldgateway}")
            run(f"ip route add default via {ip} dev {interface}")
    return redirect("/renderapplet/settings/internet")

@app.route("/uploadsoftware", methods=['POST'])
def uploadsoftware():
    if request.method == 'POST':
        rmtree("temp")
        mkdir("temp")
        f = request.files["file"]
        try:
            f.save("temp/softwaretoinstall.zip")
        except IsADirectoryError:
            return redirect("/renderapplet/settings/installedsoftware-notavalidfile")
        try:
            with ZipFile("temp/softwaretoinstall.zip") as z:
                try:
                    info = literal_eval(z.read("info.json").decode())
                    return redirect(f"/renderapplet/settings/installedsoftware-softwareinfo?name={info['name']}&version={info['version']}&summary={info['summary']}&description={info['description']}")
                except KeyError:
                    return redirect("/renderapplet/settings/installedsoftware-notavalidfile")
        except BadZipFile:
            remove("temp/softwaretoinstall.zip")
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
    software[softwarename] = "Settings"
    save("software")
    appletsvar.append(softwarename)
    save("applets")
    permissions[softwarename] = []
    save("permissions")
    return redirect("/renderapplet/settings/installedsoftware")  

@app.route("/uninstallsoftware/<softwarename>")
def uninstallsoftware(softwarename):
    try:
        openapplets.remove(software)
    except:
        pass
    rmtree(f"software/{softwarename}", ignore_errors=True)  
    rmtree(f"templates/applets/{softwarename}", ignore_errors=True)
    appletsvar.remove(softwarename)
    save("applets")
    del software[softwarename]
    save("software")
    return redirect("/renderapplet/settings/installedsoftware")

@app.route("/quit/<applet>/")
def quit(applet):
    try:
        openapplets.remove(applet)
        return redirect("/applets")
    except:
        return redirect("/applets")

@app.route("/uploadfile/<applet>", methods=["POST"])
def uploadfile():
    return

@app.route("/createfile/<applet>/", methods=["POST"])
def createfile(applet):
    try:
        Path(f"software/{applet}/{request.form.get("filename")}").touch()
        return "success"
    except:
        return "unknown error"
    
@app.route("/removefile/<applet>/", methods=["POST"])
def removefile(applet):
    try:
        remove(f"software/{applet}/{request.form.get("filename")}")
        return "success"
    except:
        return "unknown error"
    
@app.route("/readfile/<applet>/", methods=["POST"])
def readfile(applet):
    try:
        return open(f"software/{applet}/{request.form.get("filename")}", "r").read()
    except FileNotFoundError:
        return "file not found"
    except:
        return "unknown error"
    
@app.route("/writefile/<applet>/", methods=["POST"])
def writefile(applet):
    try:
        open(f"software/{applet}/{request.form.get("filename")}", "a+").write(request.form.get("contents"))
        return "success"
    except:
        return "unknown error"

@app.route("/makedir/<applet>/", methods=["POST"])
def makedir(applet):
    try:
        mkdir(f"software/{applet}/{request.form.get("dirname")}")
        return "success"
    except:
        return "unknown error"

@app.route("/removedir/<applet>/", methods=["POST"])
def removedir(applet):
    try:
        rmdir(f"software/{applet}/{request.form.get("dirname")}")
        return "success"
    except:
        return "unknown error"

@app.route("/downloadfile/<applet>/", methods=["POST"])
def downloadfile(applet):
    try:
        r = get(request.form.get("url"), allow_redirects=True)
        with open(f"software/{applet}/{request.form.get("output")}", "wb") as f:
            f.write(r.content)
        return "done"
    except:
        return "unknown error"

@app.route("/runcommand/<applet>/", methods=["POST"])
def runcommand(applet):
    try:
        if "commands" in permissions[applet]:
            return run(request.form.get("command"))
        else:
            return "permission denied"
    except:
        return "unknown error"


@app.route("/applets/")
def applets():
    appletsdict = {}
    for i, val in enumerate(appletsvar):
        appletsdict[val] = load(open(f"software/{val}/info.json"))["summary"]
    return render_template("applets.html", openapplets=openapplets, applets=appletsdict)

@app.route("/applets/<applet>/")
def applet(applet):
    if checkifappletclosed(applet):
        openapplets.append(applet)
    return render_template(f"renderapplet.html", openapplets=openapplets, applettorender=applet, appletperms=permissions[applet])

@app.route("/renderapplet/<applet>/<file>", methods=['GET', 'POST'])
def renderapplet(applet, file):
    if checkifappletclosed(applet):
        openapplets.append(applet)
    return render_template(f"applets/{applet}/{file}.html") 

@app.route("/renderapplet/settings/internet")
def internet():
    ifs = run("ls /sys/class/net/").split()
    ips = {}
    for interface in ifs:
        ip = run(f"ip -f inet addr show {interface} | sed -En -e 's/.*inet ([0-9.]+).*/\\1/p'").replace("\n", "")
        gateway = run(f"ip route show 0.0.0.0/0 dev {interface} | cut -d " " -f3").replace("\n", "")
        if ip != "" and interface != "lo":
            ips[f"{interface}"] = {"ip": ip, "gateway": gateway}
    return render_template("applets/settings/internet.html", ips=ips)

@app.route("/renderapplet/settings/about")
def about():
    hostinfo = literal_eval(run("hostnamectl --json=short").replace('null', "None"))
    info = dict()
    info["servermand"] = version
    info["os"] = hostinfo["OperatingSystemPrettyName"]
    info["kernel"] = hostinfo['KernelName'] + " " + hostinfo['KernelRelease'] + " " + hostinfo['KernelVersion']
    info["hardware"] = hostinfo["HardwareVendor"] + " " + hostinfo["HardwareModel"]
    info["firmware"] = hostinfo["FirmwareVendor"] + " " + hostinfo["FirmwareVersion"]
    return render_template("applets/settings/about.html", info=info)

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