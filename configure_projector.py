import argparse
import os

from hardware.projector import Projector
from hardware.camera import Camera
from hardware.surface import Surface, SurfaceFactory

intro_text = """
Welcome to the projector configuration setup!
Before starting, make sure the following is true:
    - The projector is connected
    - The camera is connected
    - You have selected the correct camera ID
    - You have selected the correct projector ID 
    
PRESS ENTER TO CONTINUE
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This will create a "
                                                 "configuration file that you can load using "
                                                 "the Projector object.")

    parser.add_argument("-s", "--save-to", type=str, required=True,
                        help="The path/filename to save the config *.json to.")
    parser.add_argument("-c", "--cam-id", type=int, required=True,
                        help="The camera ID (must be integer > 0)")
    parser.add_argument("-p", "--projector-id", type=int, required=True,
                        help="The monitor ID representing the projector. "
                             "Try numbers 0-# monitors, if you don't know.")
    args = parser.parse_args()

    p = Projector(args.projector_id)
    c = Camera(1)

    factory = SurfaceFactory(c, p)
    print(intro_text)
    input()
    while True:
        new_surface = factory.create_surface()
        p.surfaces.append(new_surface)

        ans = ""
        while "y" not in ans.lower() and "n" not in ans.lower():
            ans = input("Would you like to create another surface? (y/n)")
        if "n" in ans.lower():
            break

    p.save_configuration(args.save_to)
    print("Configuration saved!")
    c.close()
    p.close()
