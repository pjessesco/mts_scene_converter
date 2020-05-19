from xml.etree.ElementTree import parse, Element, dump
from xml.etree import ElementTree
import random
import math
from datetime import datetime

# ========== Param of the scene (heuristic) ===========

# bathroom1
bathroom_center = [-0.25, 1.512405, -0.427584]
bathroom_shift = 0.01

# bathroom2 (duck)
bathroom2_center = [-8.91, 5.93151, 7.54231]
bathroom2_shift = 0.01

# Bedroom
bedroom_center = [2.05558, 1.21244, 2.29897]
bedroom_shift = 0.01

# classroom
classroom_center = [-0.89049, 1.57158, 2.88653]
classroom_shift = 0.01

# dining room
dining_room_center = [-0.587317, 4.0623, 3.71429]
dining_room_shift = 0.01

# kitchen1
kitchen_center = [0.7011, 2.00475, 2.25239]
kitchen_shift = 0.01


# kitchen2
kitchen2_center = [94.2855, 150.701, 296.937]
kitchen2_shift = 7

# living-room
grey_white_room_center = [3.40518, 1.231065, -2.31789]
grey_white_room_shift = 0.01

# veach door
veach_door_center = [-71.39, 100.49, 145.3]
veach_door_shift = 7


# ================== User Option ======================

# Probability that bsdf is randomly chosen
rand_bsdf_prob = 0.5

cam_center = bedroom_center
cam_shift = bedroom_shift

random_scene_num = 10


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

    # folder name
    # scene = "living-room"
    # scene = "bathroom1"
    # scene = "bathroom2"
    # scene = "bedroom"
    # scene = "classroom"
    # scene = "dining-room"
    # scene = "kitchen1"
    # scene = "kitchen2"
    scene = "veach"


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

            if random.uniform(0.0, 1.0) > rand_bsdf_prob:
                continue
            print("bsdf change")

            set_bsdf_id = False


            # Clear bsdf xml node except its id
            if 'id' in bsdf.attrib:
                set_bsdf_id = True
                bsdf_id = bsdf.attrib["id"]

            bsdf.clear()

            if set_bsdf_id:
                bsdf.set('id', bsdf_id)


            choose_rand_bsdf(bsdf)



        tree.write('C:\\Users\\cglab\\Desktop\\scenes\\'+ scene + '\\rand_scene'+ str(i)+'.xml')

