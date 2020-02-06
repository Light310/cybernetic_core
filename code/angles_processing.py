import math
from math import pi, sin, cos
import numpy as np

from common import a, b, c, d, angle_to_rad, rad_to_angle

target_alpha = 0
target_beta = 0
target_gamma = 0

def get_leg_angles(delta_x, delta_z, prev_angles, mode):
    #print(f'Looking for angles for ({delta_x}, {delta_z}, {prev_angles}, {mode})')
    if sum(prev_angles) != 0:
        prev_ksi = rad_to_angle(sum(prev_angles)) + 90
    else:
        prev_ksi = None

    possible_angles = find_angles(delta_x, delta_z, prev_ksi)

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
    min_distance = 100000000
    best_angles = None
    min_distance_num = 0
    
    for item in all_angles:
        if not check_angles(item, mode)[0]:
            continue        
        cur_distance = get_angles_distance(item, prev_angles)
        #print(angles_str(item), cur_distance)
        #print(cur_distance)
        
        if cur_distance <= min_distance:
            min_distance = cur_distance
            best_angles = item[:]

    if min_distance > 0.1:
        min_distance_num += 1        
        if min_distance_num > 1:            
            print('best_angles : {0}'.format([rad_to_angle(x) for x in best_angles]))
            raise Exception('Min distance found : {0}'.format(min_distance))

    #print(f'Diff: {angles_diff(prev_angles, best_angles)}. Prev angles: {angles_str(prev_angles)}, best_angles: {angles_str(best_angles)}')
    #print(min_distance)
    if best_angles is None:
        #print('No suitable angles found. Halt')
        #for angle in all_angles:
        #    print(check_angles(angle, mode)[1])
        raise Exception('No angles\n')
        # sys.exit(1)
    return best_angles

def check_angles(angles, mode):
    # mode means range plus and minus from vertical. Mode 10 means 80 - 100 degrees
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
    
    if mode is None:
        mode = 10

    if alpha + beta + gamma < -90 - mode or alpha + beta + gamma > -90 + mode:
            return False, f'{angles_converted}. mode {mode}. alpha + beta + gamma = {alpha + beta + gamma}'
    """
    if mode == 'stable130':
        if alpha + beta + gamma < -130 or alpha + beta + gamma > -50:
            return False, angles_converted + '. stable130 mode. alpha + beta + gamma = {0}'.format(alpha + beta + gamma)
    elif mode == 'stable120':
        if alpha + beta + gamma < -120 or alpha + beta + gamma > -60:
            return False, angles_converted + '. stable120 mode. alpha + beta + gamma = {0}'.format(alpha + beta + gamma)
    elif mode == 'stable115':
        if alpha + beta + gamma < -115 or alpha + beta + gamma > -65:
            return False, angles_converted + '. stable115 mode. alpha + beta + gamma = {0}'.format(alpha + beta + gamma)
    else:
        if alpha + beta + gamma < -110 or alpha + beta + gamma > -70:
            return False, angles_converted + '. stable110 mode. alpha + beta + gamma = {0}'.format(alpha + beta + gamma)
    """
    
    return True, 'All ok'


def find_angles(Dx, Dy, prev_ksi=None):
    #print(f'Dx, Dy : ({Dx}, {Dy})')
    results = []
    full_dist = math.sqrt(Dx ** 2 + Dy ** 2)
    if full_dist > a + b + c:
        #print('No decisions. Full distance : {0}'.format(full_dist))
        raise Exception('No decisions. Full distance : {0}'.format(full_dist))
        #sys.exit(1)

    #for k in np.arange(-35.0, 35.0, 0.1):
    from_angle = -40.0
    to_angle = 40.0
    if prev_ksi:
        from_angle = max(from_angle, prev_ksi - 2.0)
        to_angle = min(to_angle, prev_ksi + 2.0)
        #print(f'Trying angles : {from_angle}, {to_angle}')

    for k in np.arange(from_angle, to_angle, 0.01):

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
                if abs(rad_to_angle(alpha+beta+gamma) - k + 90) > 0.1:
                    print(f'wtf {rad_to_angle(alpha+beta+gamma)}. {k}. {abs(rad_to_angle(alpha+beta+gamma) - k + 90)}')

    return results

def get_angles_distance(angles1, angles2):
    # angles sent in radians
    # adding difference of last join from perpendicular as a critical value
    # do I need SQRT? WTF?
    return (angles1[0] - angles2[0]) ** 2 + \
           (angles1[1] - angles2[1]) ** 2 + \
           (angles1[2] - angles2[2]) ** 2 + \
           3 * abs(rad_to_angle(angles1[0] + angles1[1] + angles1[2] + 90) ** 2)


def angles_str(angles):
    result = ''
    for item in angles:
        result += '{0} '.format(round(rad_to_angle(item), 2))
    return result

def angles_diff(angles1, angles2):
    summ_diff = 0
    result = []
    for angle1, angle2 in zip(angles1, angles2):
        item = round(rad_to_angle(angle1 - angle2), 2)
        result.append(item)
        summ_diff += abs(item)
    
    return result, round(summ_diff, 2)

#get_leg_angles(8.034745999833035, -9.999599999999894, [0.3535205598896317, -0.9122890020654717, -1.5007200751774685], 'stable120')
"""
Looking for angles for (8.034745999833035, -9.999599999999894, [0.3535205598896317, -0.9122890020654717, -1.5007200751774685], stable120)
Diff: ([-0.85, 5.37, -2.52], 8.74). Prev angles: 20.26 -52.27 -85.98 , best_angles: 21.1 -57.64 -83.47
76102627.80376154

Looking for angles for (8.035311685257767, -9.999600000000001, [0.42280362424280127, -1.1885066630999062, -1.3286920635360902], stable120)
Diff: ([3.12, -10.47, 7.34], 20.93). Prev angles: 24.22 -68.1 -76.13 , best_angles: 21.1 -57.63 -83.47
76102627.84563096
"""