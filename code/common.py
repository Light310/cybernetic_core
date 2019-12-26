import os
from math import pi

a = 10.5
b = 5.4
c = 12.2
d = 5.4

def angle_to_rad(angle):
    return angle * pi / 180

def rad_to_angle(rad):
    return rad * 180 / pi

sequences_dir = 'D:\\Development\\Python\\cybernetic_core\\sequences\\'

def create_dir(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)

def write_to_file(parameters, information_to_write):
    dir = sequences_dir
    for k, v in parameters.items():
        dir = os.path.join(dir, '{0}_{1}'.format(k, v)) 
        create_dir(dir)
    file = os.path.join(dir, 'sequence.txt')
    with open(file, 'w') as f:
        try:
            f.write(information_to_write)
        except TypeError:
            f.write(str(information_to_write))

def create_sequence_file(parameters):
    dir = sequences_dir
    for k, v in parameters.items():
        dir = os.path.join(dir, '{0}_{1}'.format(k, v)) 
        create_dir(dir)
    file = os.path.join(dir, 'sequence.txt')
    return file

