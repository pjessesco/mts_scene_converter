from xml.etree.ElementTree import parse, Element, dump
from xml.etree import ElementTree
import random
import math
from datetime import datetime

# ================== User Option ======================

# scene = "living-room"
scene = "bathroom1"
# scene = "bathroom2"
# scene = "bedroom"
# scene = "classroom"
# scene = "dining-room"
# scene = "kitchen1"
# scene = "kitchen2"
# scene = "veach"

# Probability that bsdf is randomly converted
rand_bsdf_prob = 1.0

# How many random scenes generated?
random_scene_num = 10

# ========== Param of the scene (heuristic) ===========

# bathroom1
if scene == "bathroom1":
    cam_center = [-0.25, 1.512405, -0.427584]
    cam_shift = 0.01

# bathroom2 (duck)
elif scene == "bathroom2":
    cam_center = [-8.91, 5.93151, 7.54231]
    cam_shift = 0.01

# Bedroom
elif scene == "bedroom":
    cam_center = [2.05558, 1.21244, 2.29897]
    cam_shift = 0.01

# classroom
elif scene == "classroom":
    cam_center = [-0.89049, 1.57158, 2.88653]
    cam_shift = 0.01

# dining room
elif scene == "dining-room":
    cam_center = [-0.587317, 4.0623, 3.71429]
    cam_shift = 0.01

# kitchen1
elif scene == "kitchen1":
    cam_center = [0.7011, 2.00475, 2.25239]
    cam_shift = 0.01

# kitchen2
elif scene == "kitchen2":
    cam_center = [94.2855, 150.701, 296.937]
    cam_shift = 7

# living-room
elif scene == "living-room":
    cam_center = [3.40518, 1.231065, -2.31789]
    cam_shift = 0.01

# veach door
elif scene == "veach":
    cam_center = [-71.39, 100.49, 145.3]
    cam_shift = 7

# =====================================================


def get_cam_pos_from_mat(d11, d12, d13, d14,
                         d21, d22, d23, d24,
                         d31, d32, d33, d34,
                         d41, d42, d43, d44):

    return [d14, d24, d34]



def choose_rand_bsdf(bsdf):
    bsdf_list = ['diffuse', 'dielectric',  'conductor']
    chosen_bsdf = random.choice(bsdf_list)

    bsdf.set('type', chosen_bsdf)

    if chosen_bsdf == 'diffuse':
        fill_rand_diffuse(bsdf)

    elif chosen_bsdf == 'dielectric':
        fill_rand_dielectric(bsdf)
    elif chosen_bsdf == 'conductor':
        fill_rand_conductor(bsdf)


def fill_rand_diffuse(bsdf):
    spectrum = ElementTree.SubElement(bsdf, 'spectrum')
    spectrum.set("name", "reflectance")
    rand_r = str(round(random.uniform(0.0, 1.0), 4))
    rand_g = str(round(random.uniform(0.0, 1.0), 4))
    rand_b = str(round(random.uniform(0.0, 1.0), 4))
    spectrum.set("value", str(rand_r)+","+ str(rand_g)+","+ str(rand_b))


def fill_rand_dielectric(bsdf):

    IOR_list = ['water', 'water ice', 'bk7']
    chosen_ext_ior = random.choice(IOR_list)

    intIOR = ElementTree.SubElement(bsdf, 'string')
    extIOR = ElementTree.SubElement(bsdf, 'string')

    intIOR.set("name", "intIOR")
    intIOR.set("value", "vacuum")

    extIOR.set("name", "extIOR")
    extIOR.set("value", chosen_ext_ior)

def fill_rand_conductor(bsdf):

    mat_list = ['Ag', 'Al', 'Au', 'Cu', 'Li']
    chosen_mat = random.choice(mat_list)

    material = ElementTree.SubElement(bsdf, 'string')
    material.set("name", "material")
    material.set("value", chosen_mat)


if __name__ == '__main__':

    random.seed(datetime.now())

    for i in range(random_scene_num):
        tree = parse('C:\\Users\\cglab\\Desktop\\scenes\\'+ scene + '\\scene.xml')
        root = tree.getroot()
        cam_to_world = root.find("sensor").find("transform")

        # List that contains pos of camera
        cam_pos = None
        cam_target = None
        cam_up = None

        # Parse the position of a camera
        if cam_to_world.find("matrix") is not None:
            cam_mat = (cam_to_world.find("matrix").attrib["value"]).split()
            cam_pos = [cam_mat[3], cam_mat[7], cam_mat[11]]

        elif cam_to_world.find("lookat") is not None:
            cam_pos = cam_to_world.find("lookat").attrib["origin"].split(",")

        else:
            print("no transform exist in sensor")
            exit(-1)

        # original cam position of the scene
        cam_pos = [float(cam_pos[0]), float(cam_pos[1]), float(cam_pos[2])]
        # heuristic cam position of the scene
        cam_pos = cam_center


        # Randomly shift camera
        cam_pos[0] += random.uniform(-cam_shift, cam_shift)
        cam_pos[1] += random.uniform(-cam_shift, cam_shift)
        cam_pos[2] += random.uniform(-cam_shift, cam_shift)

        # Uniform sample on a sphere
        theta = 6.2831853*random.uniform(0.0, 1.0)
        phi = math.acos(1-2*random.uniform(0.0, 1.0))
        view_x = math.sin(phi)*math.cos(theta)
        view_y = math.sin(phi)*math.sin(theta)
        view_z = math.cos(phi)


        cam_target = [cam_pos[0]+view_x, cam_pos[1]+view_y, cam_pos[2]+view_z]

        cam_to_world.clear()
        cam_to_world.set('name', "toWorld")
        rand_lookat = ElementTree.SubElement(cam_to_world, 'lookat')
        rand_lookat.set("origin", str(cam_pos[0])+","+str(cam_pos[1])+","+str(cam_pos[2]))
        rand_lookat.set("target", str(cam_target[0]) + "," + str(cam_target[1]) + "," + str(cam_target[2]))
        rand_lookat.set("up", "0,0,1")


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



        tree.write('C:\\Users\\cglab\\Desktop\\scenes\\'+ scene + '\\rand_scene'+ str(i)+'.xml')

