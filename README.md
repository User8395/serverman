# Serverman
Web-based server frontend

## What dis
Serverman is a frontend for your server. It aims to manage all aspects of a server, including, but not limited to
- Network connections
- Packages
- System updates
- Installed server software

## "Serverman"...sounds like a play on words
It is! Serverman is short for **Server man**ager.

## Does it work?
As of now, Serverman is under heavy development. There is no feature timeline right now, so no one knows what features will come next.

## I wanna try!
If you want try out Serverman, just make sure you have Python 3 or newer installed and follow the steps below

1. Clone the repo and `cd` into it: `git clone https://github.com/User8395/serverman; cd serverman`
2. Install `python-venv`:
	Debian/derivatives: `sudo apt install python-venv`
	Fedora: `venv` comes with the base Python package
	Arch/derivatives: `sudo pacman -S python-venv`
	All others: refer to your distrubution's wiki
3. Create a virtual enviroment: `python -m venv venv`
4. Activate the virtual enviroment: `source venv/bin/activate`
5. Install requirements: `pip install -r requirements.txt`
6. Enter the source directory: `cd src`
7. Run Serverman: `flask run --debug -p 6699`

When you're done, deactivate the virtual enviroment by running `deactivate`.

## What can Serverman do right now?
Currently, Serverman can get system network information by using `ip a`. View it by going to Settings > Internet > Status.

## Credits
Pallets Projects: for Flask, Jinja, and Werkzeug

Comedic README inspired by @dnschneid
