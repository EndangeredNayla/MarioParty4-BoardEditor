# ============================================
# MP4 Board Editor
# Current Author: Nayla Hanegan (naylahanegan@gmail.com)
# Original Author: Mr. Brocoli
# Date: 5/6/2024
# License: MIT
# ============================================

from tkinter import filedialog
from ursina import *

import struct
import random
import subprocess
import shutil
import math
import tempfile
import sys
import os

# Determine if the script is frozen
frozen = getattr(sys, 'frozen', False)

# If the script is frozen, use the appropriate file path
if frozen:
    # Get the path to the bundled files
    bundle_dir = sys._MEIPASS
    # Modify your file paths accordingly
    bindump_path = os.path.join(bundle_dir, "dependencies", "bindump.exe")
    binpack_path = os.path.join(bundle_dir, "dependencies", "binpack.exe")
    assets_dir = os.path.join(bundle_dir, "assets")
else:
    # Use the regular file paths
    bindump_path = "dependencies/bindump.exe"
    binpack_path = "dependencies/binpack.exe"
    assets_dir = "assets"

fname = filedialog.askopenfilename(title="Select a world file", defaultextension=".bin", filetypes = [("RAW Board File", "*.bin"), ("Extracted Board File", "*.dat")])
dot_index = fname.find('.')
fileName = os.path.basename(fname)
if dot_index != -1:
    fileExt = fileName[dot_index + 1:]
if "bin" in fileName:
    os.makedirs(".tmp", exist_ok=True)
    os.chdir(".tmp")
    shutil.copy(fname, fileName)
    os.chdir("..")
    #if os.path.exists("tmp/" + fileName[:-4] + "_file0.dat"):
    #    pass
    if os.name != 'nt': #elif
        subprocess.run(["wine", bindump_path, ".tmp" + "/" + fileName])
    else:
        subprocess.run([bindump_path, ".tmp" + "/" + fileName])
        

def random_space():
    x = random.randint(0, 1000)
    if x <= 300:
        return 1
    if x <= 450:
        return 2
    if x <= 500:
        return 3
    if x <= 600:
        return 4
    if x <= 700:
        return 5
    if x <= 800:
        return 6
    if x <= 900:
        return 7
    if x <= 950:
        return 8
    return 9

spaces = []
SCALES_US = 0.0002
global file

def read_uint():
    global file
    return struct.unpack('>I', file.read(4))[0]

def read_short():
    global file
    return struct.unpack('>H', file.read(2))[0]

def read_float():
    global file
    return struct.unpack('>f', file.read(4))[0]

def read_vec3f():
    return [read_float(), read_float(), read_float()]

def write_uint(x):
    global file
    file.write(struct.pack('>I', x))

def write_short(x):
    global file
    file.write(struct.pack('>H', x))

def write_float(x):
    global file
    file.write(struct.pack('>f', x))

def write_vec3f(x):
    write_float(x[0])
    write_float(x[1])
    write_float(x[2])

class Space:
    space_types = ["Empty", "Blue", "Red", "Bowser", "Mushroom", "Battle", "Happening", "Chance", "Star", "Warp", "Fire", "Unknown"]
    
    def __init__(self):
        self.position = [0.0, 0.0, 0.0]
        self.special = 0
        self.scale = [1.0, 1.0, 1.0]
        self.rotation = [0.0, 0.0, 0.0]
        self.space_type = 0
        self.next_space_ids = []
        self.dragger = None
        self.lines = []

    def read(self):
        self.position = read_vec3f()
        self.rotation = read_vec3f()
        self.scale = read_vec3f()
        self.special = read_uint()
        self.space_type = read_short()
        next_space_num = read_short()
        self.next_space_ids = [read_short() for _ in range(next_space_num)]

    def write(self):
        write_vec3f(self.position)
        write_vec3f(self.rotation)
        write_vec3f(self.scale)
        write_uint(self.special)
        write_short(self.space_type)
        write_short(len(self.next_space_ids))
        for space_id in self.next_space_ids:
            write_short(space_id)

    def pos_2d(self):
        return (self.position[0] * SCALES_US, -self.position[2] * SCALES_US)

    def copy_attributes(self, original):
        self.position = original.position.copy()
        self.rotation = original.rotation.copy()
        self.scale = original.scale.copy()
        self.special = original.special
        self.space_type = original.space_type
        self.next_space_ids = []

    def ui_setup(self):
        if not self.dragger:
            self.dragger = Draggable()
        self.dragger.model = 'quad'
        self.dragger.scale = SCALES_US * 100
        self.dragger.color = color.white
        self.dragger.position = self.pos_2d()
        self.dragger.setP(self.dragger, 0)
        tex = textures[self.space_type]  # Use textures based on space type
        if tex is not None:
            self.dragger.setTexture(tex, 1)
        else:
            print("Error: Texture is None")
        while len(self.lines) != len(self.next_space_ids):
            self.lines.append(Entity(parent=camera.ui, model='line', origin_x=-.5))
        self.dragger.bruhsus = self

    def drag_update(self):
        x = self
        x.dragger.setTexture(textures[x.space_type], 1)
        for y, z in zip(x.lines, x.next_space_ids):
            z = spaces[z].dragger
            y.position = x.dragger.position
            y.look_at_2d(z)
            y.rotation_z -= 90
            y.scale_x = distance_2d(y, z)
        x.position[0] = x.dragger.position[0] / SCALES_US
        x.position[2] = -x.dragger.position[1] / SCALES_US

    def __str__(self):
        x = f"Position: {self.position}\n"
        x += f"Special: {hex(self.special)}\n"
        x += f"Rotation: {self.rotation}\n"
        x += f"SpaceType: {self.space_types[self.space_type]}\n"
        x += f"NextSpaceIDs: {self.next_space_ids}\n"
        return x
global file
if "_file0" not in fileName:
    with open(".tmp" + "/" + fileName[:-4] + "_file0.dat", 'rb') as f:
        file = f
        length = read_uint()
        for i in range(length):
            x = Space()
            x.read()
            spaces.append(x)
else:
    with open(".tmp" + "/" + fileName[:-4] + ".dat", 'rb') as f:
        file = f
        length = read_uint()
        for i in range(length):
            x = Space()
            x.read()
            spaces.append(x)
app = Ursina()
window.fps_counter.enabled = False
window.collider_counter.enabled = False
window.cog_button.enabled = False
window.entity_counter.enabled = False
t = Text(scale=1, origin=(0,0), background=False)
print(os.getcwd())
textures = [
    loader.loadTexture(assets_dir + "/Empty.png"),
    loader.loadTexture(assets_dir + "/Blue.png"),
    loader.loadTexture(assets_dir + "/Red.png"),
    loader.loadTexture(assets_dir + "/Bowser.png"),
    loader.loadTexture(assets_dir + "/Mushroom.png"),
    loader.loadTexture(assets_dir + "/Battle.png"),
    loader.loadTexture(assets_dir + "/Happening.png"),
    loader.loadTexture(assets_dir + "/Chance.png"),
    loader.loadTexture(assets_dir + "/Star.png"),
    loader.loadTexture(assets_dir + "/Warp.png"),
    loader.loadTexture(assets_dir + "/Fire.png"),
    loader.loadTexture(assets_dir + "/Unknown.png")
]
print("Textures loaded successfully:", textures)


for x in spaces:
    x.ui_setup()

def update():
    if mouse.hovered_entity is not None:
        if str(mouse.hovered_entity) == "draggable":
            t.text = str(mouse.hovered_entity.bruhsus)
    for x in spaces:
        x.drag_update()

def input(key):
    if key == 'q':
        if mouse.hovered_entity is not None:
            if str(mouse.hovered_entity) == "draggable":
                mouse.hovered_entity.bruhsus.space_type += 1
                if mouse.hovered_entity.bruhsus.space_type >= 10:
                    mouse.hovered_entity.bruhsus.space_type = 0
    if key == "w":
        if mouse.hovered_entity is not None:
            if str(mouse.hovered_entity) == "draggable":
                old_space = mouse.hovered_entity.bruhsus
                new_space = Space()
                new_space.copy_attributes(old_space)
                spaces.append(new_space)
                old_space.next_space_ids.append(len(spaces) - 1)
                new_space.ui_setup()
                old_space.ui_setup()
                new_space.dragger.setY(new_space.dragger.getY() + SCALES_US * 300)
    if key == "e":
        if mouse.hovered_entity is not None:
            if str(mouse.hovered_entity) == "draggable":
                old_space = mouse.hovered_entity.bruhsus
                old_space.next_space_ids = []
    if key == "s":
        global file
        with open(".tmp" + "/" + fileName[:-4] + "_file0.dat", "wb") as w:
            file = w
            write_uint(len(spaces))
            for x in spaces:
                x.write()
            os.makedirs(".tmp/out", exist_ok=True)
            if os.name != 'nt':
                subprocess.run(["wine", bindump_path, ".tmp" + "/" + fileName[:-4] + ".txt", ".tmp/out" + fileName])
            else:
                subprocess.run([bindump_path, ".tmp" + "/" + fileName[:-4] + ".txt", ".tmp/out" + fileName])
            file_path = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("RAW Board File", "*.bin")])
            shutil.copy(".tmp/out" + fileName, file_path)
    if key == "r":
        if mouse.hovered_entity is not None:
            if str(mouse.hovered_entity) == "draggable":
                old_space = mouse.hovered_entity.bruhsus
                old_space.next_space_ids
                dist = 10000
                closest_space = -1
                for i, x in enumerate(spaces):
                    if x == old_space or i in old_space.next_space_ids:
                        continue
                    dist_temp = math.dist(old_space.position, x.position)
                    if dist_temp < dist:
                        dist = dist_temp
                        closest_space = i
                if closest_space == -1:
                    return
                old_space.next_space_ids.append(closest_space)
                old_space.ui_setup()

app.run()