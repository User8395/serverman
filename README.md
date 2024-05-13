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
If you want to try out Serverman, make sure you have Python 3 or newer and the [Serverman daemon](https://github.com/User8395/servermand) installed and follow the steps below

1. Clone the repo and `cd` into it: `git clone https://github.com/User8395/serverman; cd serverman`
2. Install `python-venv`:
	Debian/derivatives: `sudo apt install python-venv`
	Fedora: `sudo dnf install python3`
	Arch/derivatives: `sudo pacman -S python-venv`
	All others: refer to your distribution's wiki
3. Create a virtual environment: `python -m venv venv`
4. Activate the virtual environment: `source venv/bin/activate`
5. Install requirements: `pip install -r requirements.txt`
6. Enter the source directory: `cd src`
7. Run Serverman: `flask run --debug -p 6699`

When you're done, deactivate the virtual environment by running `deactivate`.

## Known issues that may take a while to fix
`requestpermissions()` is unable to return whether the user has accepted or denied the permissions

## What can Serverman do right now?
Change the host ip address, show system info, and install software.

## There's a menu to install software from a zip file, but every zip file I use is invalid?!?!
There's a zip file in the extra folder that you can use.