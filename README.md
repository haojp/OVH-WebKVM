# OVH WebKVM

OVH WebKVM is a little python script that enables your server's emergency
console using OVH API, launches locales [NoVNC](http://kanaka.github.io/noVNC/)
and [websockify](https://github.com/kanaka/websockify) instances,
then connects itself automatically to your server's console.

No need to use OVH manager or the awful Java iKVM Viewer applet!

Support for ATEN proprietary video encoding in NoVNC is done by
[@kelleyk](https://github.com/kelleyk), many thanks to
[him](https://github.com/kelleyk/noVNC/tree/bmc-support)!

## Requirements

 - Python 3.2+
 - Any modern web browser

This script must works on OS X and any recent Linux distribution shipping
Python 3.2+.

## Setup

Create a new virtualenv:
```
pyvenv ~/.pyvenv/OVH-WebKVM
```

Activate the new venv:
```
source ~/.pyvenv/OVH-WebKVM/bin/activate
```

Clone the repository:
```
git clone --recursive https://github.com/Inikup/OVH-WebKVM.git
cd OVH-WebKVM
```

Install dependencies:
```
pip install -r requirements.txt
```

Register your application on the OVH API using
[this form](https://eu.api.ovh.com/createApp/), with the following permissions:
```
GET  /dedicated/server
GET  /dedicated/server/*/features/ipmi*
POST /dedicated/server/*/features/ipmi*
GET  /dedicated/server/*/task/*
```

Then rename the `ovh.conf.default` file to `ovh.conf`, and edit it with the
application key, application secret, and consumer key provided by OVH.

## Usage

Activate the venv if needed:
```
source ~/.pyvenv/OVH-WebKVM/bin/activate
```

You can now launch the script:
```
./kvm.py [your server name]
```

Example:
```
./kvm.py nsXXXXXX.ip-XXX-XXX-XXX.eu
```

Press Ctrl+C to exit.
Then, type `deactivate` to exit venv.

# Tips

For a better video quality, set "Video quality" to "high" and "Subsampling mode"
to "4:4:4" in noVNC settings.

