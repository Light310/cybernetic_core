import math
from math import pi, sin, cos
import numpy as np

from common import a, b, c, d, angle_to_rad, rad_to_angle

target_alpha = 0
target_beta = 0
target_gamma = 0

def get_leg_angles(delta_x, delta_z, prev_angles, mode="moving"):
    #print('Looking for angles for ({0}, {1})'.format(delta_x, delta_z))
    possible_angles = find_angles(delta_x, delta_z)

    # recalculating to check for some error
    """
    for item in possible_angles:
        alpha = item[0]
        beta = item[1]
        gamma = item[2]
        Bx = a * cos(alpha)
        By = a * sin(alpha)
        Cx = Bx + b * cos(alpha + beta)
        Cy = By + b * sin(alpha + beta)
        Dx = Cx + c * cos(alpha + beta + gamma)
        Dy = Cy + c * sin(alpha + beta + gamma)
        if abs(Dx - delta_x) > 0.01 or abs(Dy - delta_z) > 0.01:
            raise Exception('Recalculating error')
    """

    return get_best_angles(possible_angles, prev_angles, mode)

def get_best_angles(all_angles, prev_angles, mode):
    min_distance = 1000
    best_angles = None
    min_distance_num = 0
    
    for item in all_angles:
        if not check_angles(item, mode)[0]:
            continue        
        cur_distance = get_angles_distance(item, prev_angles)
        
        if cur_distance <= min_distance:
            min_distance = cur_distance
            best_angles = item[:]

    if min_distance > 0.1:
        min_distance_num += 1        
        if min_distance_num > 1:
            
            print('best_angles : {0}'.format([rad_to_angle(x) for x in best_angles]))
            raise Exception('Min distance found : {0}'.format(min_distance))

    if best_angles is None:
        #print('No suitable angles found. Halt')
        #for angle in all_angles:
        #    print(check_angles(angle, mode)[1])
        raise Exception('No angles\n')
        # sys.exit(1)
    return best_angles

def check_angles(angles, mode):
    """
    mode = 'stable' means all 4 legs are standing, and more movement available
    mode = 'moving' default, at least 1 leg is up
    """
    alpha = rad_to_angle(angles[0])
    beta = rad_to_angle(angles[1])
    gamma = rad_to_angle(angles[2])
    angles_converted = str([round(x, 2) for x in [alpha, beta, gamma]])
    if alpha < -70 or alpha > 80:
        return False, angles_converted + ' alpha={0}'.format(alpha)
    if beta < -120 or beta > 80:
        return False,  angles_converted + '. beta={0}'.format(beta)
    if gamma < -90 or gamma > 15: # 15 is cuz of construction of last joint
        return False, angles_converted + '. gamma={0}'.format(gamma)
    if alpha + beta < -110 or alpha + beta > 80:
        return False, angles_converted + '. alpha + beta = {0}'.format(alpha + beta)
    if mode == 'stable130':
        if alpha + beta + gamma < -130 or alpha + beta + gamma > -50:
            return False, angles_converted + '. stable130 mode. alpha + beta + gamma = {0}'.format(alpha + beta + gamma)
    elif mode == 'stable120':
        if alpha + beta + gamma < -120 or alpha + beta + gamma > -60:
            return False, angles_converted + '. stable120 mode. alpha + beta + gamma = {0}'.format(alpha + beta + gamma)
    elif mode == 'stable110':
        if alpha + beta + gamma < -110 or alpha + beta + gamma > -70:
            return False, angles_converted + '. stable110 mode. alpha + beta + gamma = {0}'.format(alpha + beta + gamma)
    else:
        if alpha + beta + gamma < -100 or alpha + beta + gamma > -80:
            return False, angles_converted + '. stable100 mode. alpha + beta + gamma = {0}'.format(alpha + beta + gamma)
    
    return True, 'All ok'


def find_angles(Dx, Dy):
    results = []
    full_dist = math.sqrt(Dx ** 2 + Dy ** 2)
    if full_dist > a + b + c:
        #print('No decisions. Full distance : {0}'.format(full_dist))
        raise Exception('No decisions. Full distance : {0}'.format(full_dist))
        #sys.exit(1)

    #for k in np.arange(-35.0, 35.0, 0.1):
    for k in np.arange(-45.0, 45.0, 0.5):

        ksi = angle_to_rad(k)

        Cx = Dx + c * math.cos(math.pi / 2 + ksi)
        Cy = Dy + c * math.sin(math.pi / 2 + ksi)
        dist = math.sqrt(Cx ** 2 + Cy ** 2)

        if dist > a + b or dist < abs(a - b):
            pass
        else:
            # print('Ksi : {0}'.format(k))
            alpha1 = math.acos((a ** 2 + dist ** 2 - b ** 2) / (2 * a * dist))
            beta1 = math.acos((a ** 2 + b ** 2 - dist ** 2) / (2 * a * b))
            beta = -1 * (pi - beta1)

            alpha2 = math.atan2(Cy, Cx)
            alpha = alpha1 + alpha2

            Bx = a * cos(alpha)
            By = a * sin(alpha)

            BD = math.sqrt((Dx - Bx) ** 2 + (Dy - By) ** 2)
            angle_C = math.acos((b ** 2 + c ** 2 - BD ** 2) / (2 * b * c))

            for coef in [-1, 1]:
                gamma = coef * (pi - angle_C)

                Cx = Bx + b * cos(alpha + beta)
                Cy = By + b * sin(alpha + beta)
                new_Dx = Cx + c * cos(alpha + beta + gamma)
                new_Dy = Cy + c * sin(alpha + beta + gamma)
                if abs(new_Dx - Dx) > 0.01 or abs(new_Dy - Dy) > 0.01:
                    continue

                results.append([alpha, beta, gamma])

    return results

def get_angles_distance(angles1, angles2):
    # weight of gamma is 1.5 !!!
    return math.sqrt((angles1[0] - angles2[0]) ** 2 +
                     (angles1[1] - angles2[1]) ** 2 +
                     1.5 * (angles1[2] - angles2[2]) ** 2)


def angles_str(angles):
    result = ''
    for item in angles:
        result += '{0} '.format(round(180 * item / pi, 2))
    return result
