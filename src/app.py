from json import load, dump
from os import popen
from flask import Flask, redirect
from flask import render_template

app = Flask(__name__, static_folder="static")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6699)

openapplets = []

appletsvar = load(open("applets.json"))
software = load(open("software.json"))

def checkifappletclosed(applet):
    if applet not in openapplets:
        return True
    else:
        return False

@app.route("/")
def login():
    return redirect("/applets")

@app.route("/quit/<applet>")
def quit(applet):
    openapplets.remove(applet)
    return redirect("/applets")

@app.route("/applets")
def applets():
    appletsdict = {}
    for i, val in enumerate(appletsvar):
        appletsdict[val] = load(open(f"software/{val}/info.json"))["description"]
    return render_template("applets.html", openapplets=openapplets, applets=appletsdict)

@app.route("/applets/<applet>")
def applet(applet):
    if checkifappletclosed(applet):
        openapplets.append(applet)
        print(openapplets)
    return render_template(f"applets/{applet}/index.html", openapplets=openapplets)
    
@app.route("/applets/<applet>/<menu>/")
def appletmenu(applet, menu):
    return render_template(f"applets/{applet}/{menu}.html", openapplets=openapplets)

@app.route("/applets/<applet>/<menu>/<menu1>")
def appletmenu1(applet, menu, menu1):
    if applet == "settings" and menu == "internet" and menu1 == "status":
        return render_template(f"applets/settings/internet-status.html", openapplets=openapplets, ip=popen("ip a").read().replace("\n", "<br>"))
    return render_template(f"applets/{applet}/{menu}-{menu1}.html", openapplets=openapplets)

@app.route("/applets/<applet>/<menu>/<menu1>/<menu2>")
def appletmenu2(applet, menu, menu1, menu2):
    return render_template(f"applets/{applet}/{menu}-{menu1}-{menu2}.html", openapplets=openapplets)

@app.route("/applets/<applet>/<menu>/<menu1>/<menu2>/<menu3>")
def appletmenu3(applet, menu, menu1, menu2, menu3,):
    return render_template(f"applets/{applet}/{menu}-{menu1}-{menu2}-{menu3}.html", openapplets=openapplets)