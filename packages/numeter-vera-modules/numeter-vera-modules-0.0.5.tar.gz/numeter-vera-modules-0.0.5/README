numeter-vera-modules
====================

Vera module for Numeter poller.

Installation
--------------

You need to have the requests python module :

    pip install resquests

After than just clone the repo and launch the setup.py :

    git clone https://github.com/Seraf/numeter-vera-module/
    cd numeter-vera-module
    python setup.py install

Configuration
---------------

Edit the poller configuration file :

    vim /etc/numeter/numeter_poller.cfg

Add your new module in numeter poller module list **veraModule** :

    modules = numeter.poller.muninModule:MuninModule|veraModule:VeraModule

Add the configuration section for this module :

    [VeraModule]
    address: 192.168.1.XX:3480
    devices: [{'id':5, 'variables':['CurrentTemperature','CurrentSetpoint']}]
    
The module can graph everything : It's a python list containing dictionnary.
Add a device ID and variables (in states[]) you want to graph. It will automatically retrieve the name of the device and the value of each variable to display it in a graph.
