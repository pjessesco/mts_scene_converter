from xml.etree.ElementTree import parse, Element, dump
from xml.etree import ElementTree
import random
import math
from datetime import datetime
import os
import numpy as np

# ================== User Option ======================

# scene_path -- bathroom1
#            |- bathroom2
#            |- bedroom
#            |- classroom
#            |- dining-room
#            |- kitchen1
#            |- kitchen2
#            |- living-room
#            |- veach
#            |- textures

scenes_path = 'C:\\Users\\cglab\\Desktop\\scenes\\'

# scene = "bathroom1"
# scene = "bathroom2"
# scene = "bedroom"
# scene = "classroom"
# scene = "dining-room"
# scene = "kitchen1"
# scene = "kitchen2"
scene = "living-room"
# scene = "veach"

# Probability that bsdf is randomly converted
rand_bsdf_prob = 0.5

# How many random scenes generated?
random_scene_num = 10

# directory that contains scene.xml
scene_path = os.path.join(scenes_path, scene)

texture_path = os.path.join(scenes_path, 'textures')
texture_list = os.listdir(texture_path)

# Angle of camera view transform in degree
angle = 30

mat_list = ['a-C', 'Ag', 'Al', 'Au', 'Be', 'Cr', 'CsI', 'Cu', 'K', 'Li', 'MgO', 'Mo', 'W', 'VN', 'TiN', 'VC', 'Te', 'Ta', 'Se']
IOR_list = ['water', 'acetone', 'ethanol', 'carbon tetrachloride', 'glycerol', 'benzene', 'silicone oil', 'bromine', 'water ice', 'fused quartz', 'pyrex',
            'acrylic glass', 'polypropylene', 'bk7', 'sodium chloride', 'amber', 'pet', 'diamond']

# ================== Set camera shift range by scene ======================

# bathroom1
if scene == "bathroom1":
    cam_shift = 0.01

# bathroom2 (duck)
elif scene == "bathroom2":
    cam_shift = 0.01

# Bedroom
elif scene == "bedroom":
    cam_shift = 0.01

# classroom
elif scene == "classroom":
    cam_shift = 0.01

# dining room
elif scene == "dining-room":
    cam_shift = 0.01

# kitchen1
elif scene == "kitchen1":
    cam_shift = 0.01

# kitchen2
elif scene == "kitchen2":
    cam_shift = 7

# living-room
elif scene == "living-room":
    cam_shift = 0.01

# veach door
elif scene == "veach":
    cam_shift = 7

# =====================================================

def fill_rand_texture(node):

    chosen_texture = random.choice(texture_list)

    texture = ElementTree.SubElement(node, 'texture')
    texture.set('name', 'diffuseReflectance')
    texture.set('type', 'bitmap')
    filename = ElementTree.SubElement(texture, 'string')
    filename.set('name', 'filename')
    filename.set('value', os.path.join(texture_path,chosen_texture))
    filtertype = ElementTree.SubElement(texture, 'string')
    filtertype.set('name', 'filterType')
    filtertype.set('value', 'trilinear')

def choose_rand_bsdf(bsdf, nested=False):
    if nested:
        bsdf_list = ['diffuse', 'dielectric', 'conductor', 'roughconductor']
    else:
        bsdf_list = ['diffuse', 'dielectric', 'conductor', 'roughconductor', 'coating']


    chosen_bsdf = random.choice(bsdf_list)

    bsdf.set('type', chosen_bsdf)

    if chosen_bsdf == 'diffuse':
        fill_rand_diffuse(bsdf)
    elif chosen_bsdf == 'dielectric':
        fill_rand_dielectric(bsdf)
    elif chosen_bsdf == 'conductor':
        fill_rand_conductor(bsdf)
    elif chosen_bsdf == 'roughconductor':
        fill_rand_rough_conductor(bsdf)
    elif chosen_bsdf == 'coating':
        fill_rand_coating(bsdf)

# albedo, or texture
def fill_rand_diffuse(bsdf):
    diff_list = ['rgb', 'texture']
    diff_mode = random.choice(diff_list)
    if diff_mode == 'rgb':
        spectrum = ElementTree.SubElement(bsdf, 'spectrum')
        spectrum.set("name", "reflectance")
        rand_r = str(round(random.uniform(0.0, 1.0), 4))
        rand_g = str(round(random.uniform(0.0, 1.0), 4))
        rand_b = str(round(random.uniform(0.0, 1.0), 4))
        spectrum.set("value", str(rand_r)+","+ str(rand_g)+","+ str(rand_b))

    elif diff_mode == 'texture':
        fill_rand_texture(bsdf)


def fill_rand_dielectric(bsdf):
    chosen_ext_ior = random.choice(IOR_list)

    intIOR = ElementTree.SubElement(bsdf, 'string')
    extIOR = ElementTree.SubElement(bsdf, 'string')

    intIOR.set("name", "intIOR")
    intIOR.set("value", "vacuum")

    extIOR.set("name", "extIOR")
    extIOR.set("value", chosen_ext_ior)


def fill_rand_conductor(bsdf):

    chosen_mat = random.choice(mat_list)

    material = ElementTree.SubElement(bsdf, 'string')
    material.set("name", "material")
    material.set("value", chosen_mat)

def fill_rand_rough_conductor(bsdf):

    rand_alpha = str(random.uniform(0.001, 0.3))

    chosen_mat = random.choice(mat_list)
    material = ElementTree.SubElement(bsdf, 'string')
    material.set("name", "material")
    material.set("value", chosen_mat)
    dist = ElementTree.SubElement(bsdf, 'string')
    dist.set("name", "distribution")
    dist.set("value", "beckmann")
    alpha = ElementTree.SubElement(bsdf, 'float')
    alpha.set("name", "alpha")
    alpha.set("value", str(rand_alpha))

def fill_rand_coating(bsdf):
    chosen_IOR = random.choice(IOR_list)
    nested_bsdf = ElementTree.SubElement(bsdf, 'bsdf')
    choose_rand_bsdf(nested_bsdf, True)
    IOR = ElementTree.SubElement(bsdf, 'string')
    IOR.set('name', 'intIOR')
    IOR.set('value', chosen_IOR)

# TODO : WIP
# def fill_mixture_bsdf(bsdf):
#
#     w1 = random.uniform(0.0, 1.0)
#     w2 = 1.0 - w1
#     weight = ElementTree.SubElement(bsdf, 'string')
#     weight.set('name', 'weights')
#     weight.set('value', str(w1)+', '+str(w2))
#
#     nested1 = ElementTree.SubElement(bsdf, 'bsdf')
#     choose_rand_bsdf(nested1, True)
#     nested2 = ElementTree.SubElement(bsdf, 'bsdf')
#     choose_rand_bsdf(nested2, True)

def convert_str_to_float(list):
    return [float(s) for s in list]

def convert_float_to_str(list):
    return [str(f) for f in list]

def dot(list1, list2):
    ret = 0
    for l1, l2 in zip(list1, list2):
        ret += l1*l2
    return ret

if __name__ == '__main__':

    random.seed(datetime.now())

    for i in range(random_scene_num):
        tree = parse(os.path.join(scene_path, 'scene.xml'))
        root = tree.getroot()
        cam_to_world = root.find("sensor").find("transform")

        # ========================= Convert Camera ============================

        # List that contains pos of camera
        cam_pos = None
        cam_view = None
        cam_target = None
        cam_up = None

        # Parse the position view vector, and up vector of a camera
        if cam_to_world.find("matrix") is not None:
            cam_mat = (cam_to_world.find("matrix").attrib["value"]).split()
            cam_pos = convert_str_to_float([cam_mat[3], cam_mat[7], cam_mat[11]])
            cam_view = convert_str_to_float([cam_mat[2], cam_mat[6], cam_mat[10]])
            cam_up = convert_str_to_float([cam_mat[1], cam_mat[5], cam_mat[9]])

        elif cam_to_world.find("lookat") is not None:
            cam_pos = np.array(convert_str_to_float(cam_to_world.find("lookat").attrib["origin"].split(",")))
            cam_view = np.array(convert_str_to_float(cam_to_world.find("lookat").attrib["target"].split(",")))
            cam_view -= cam_pos
            cam_up = convert_str_to_float(cam_to_world.find("lookat").attrib["up"].split(","))

        else:
            print("no transform exist in sensor")
            exit(-1)

        # Randomly shift camera
        cam_pos[0] += random.uniform(-cam_shift, cam_shift)
        cam_pos[1] += random.uniform(-cam_shift, cam_shift)
        cam_pos[2] += random.uniform(-cam_shift, cam_shift)

        # random sample a point on a unit spherical cap
        constant = 1.0 / (1.0 - math.cos(math.radians(angle)))
        theta = math.acos(1 - (random.uniform(0.0, 1.0) / constant))
        phi = random.uniform(0, 6.2831853)
        rand_view_vec = np.array([math.sin(theta) * math.cos(phi), math.sin(theta) * math.sin(phi), math.cos(theta)])
        rand_up_vec = np.array([rand_view_vec[0]*rand_view_vec[2],
                                rand_view_vec[1]*rand_view_vec[2],
                                -rand_view_vec[0]*rand_view_vec[0]-rand_view_vec[1]*rand_view_vec[1]])

        # Sample a random view on shifted camera position
        vx = cam_view[0]
        vy = cam_view[1]
        vz = cam_view[2]

        rot_mat = np.array([[vy,       vx*vz, vx],
                            [-vx,      vy*vz, vy],
                            [0, -vx*vx-vy*vy, vz]])

        rotated_view = np.matmul(rot_mat, rand_view_vec)
        rotated_up = np.matmul(rot_mat, rand_up_vec)

        cam_target = rotated_view + cam_pos

        cam_to_world.clear()
        cam_to_world.set('name', "toWorld")
        rand_lookat = ElementTree.SubElement(cam_to_world, 'lookat')
        rand_lookat.set("origin", str(cam_pos[0])+","+str(cam_pos[1])+","+str(cam_pos[2]))
        rand_lookat.set("target", str(cam_target[0]) + "," + str(cam_target[1]) + "," + str(cam_target[2]))
        rand_lookat.set("up", str(rotated_up[0]) + "," + str(rotated_up[1]) + "," + str(rotated_up[2]))

        # ========================= Convert BSDFs ============================

        bsdfs = root.findall("bsdf")

        for bsdf in bsdfs:

            set_bsdf_id = False

            if random.uniform(0.0, 1.0) > rand_bsdf_prob:
                continue

            ## Parse bsdf, assuming that there are no `id` either bsdf node and its nested bsdf node.

            # Parse bsdf in nested bsdf
            nested_bsdf = bsdf.find("bsdf")
            nested_bsdf_id = None
            if nested_bsdf is not None:
                if 'id' in nested_bsdf.attrib:
                    nested_bsdf_id = nested_bsdf.attrib["id"]

            # Store bsdf id
            if nested_bsdf_id is not None:
                set_bsdf_id = True
                bsdf_id = nested_bsdf_id

            # Store nested bsdf id
            if 'id' in bsdf.attrib:
                set_bsdf_id = True
                bsdf_id = bsdf.attrib["id"]

            bsdf.clear()

            # Set bsdf id to stored one
            if set_bsdf_id:
                bsdf.set('id', bsdf_id)


            choose_rand_bsdf(bsdf)

        os.path.join(scene_path, 'scene.xml')

        tree.write(scene_path + '\\rand_scene'+ str(i)+'.xml')

