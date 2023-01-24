import mewbot.api.registry

"""
Usage:

   python3 tools/install_modules.py
   python3 -m quick_test # Run this code
   
The output should show it loading the selected plugin, and then reporting the registered
classes from it. 
"""
if __name__ == "__main__":
    for thing in mewbot.api.registry.ComponentRegistry.load_and_register_modules():
        print(thing)
    print(mewbot.api.registry.ComponentRegistry.registered)
