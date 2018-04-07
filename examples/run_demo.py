from examples import demos
from hardware.camera import Camera
from hardware.projector import Projector

"""
This is a quick example on how to run a demo from the demos module
"""

# Open a camera
cam = Camera(0)

# Calibrate the projector
projector = Projector(2)
projector.load_configuration("../projector-config.json")



# Run the demo of your choice
# demos.draw_edged(cam, projector)
# demos.draw_pointer(cam, projector)
# demos.draw_edged_snapshot(cam, projector)
demos.draw_inverted(cam, projector)

