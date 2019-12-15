import math
import sys
from math import pi, sin, cos
import random

import copy

from animation import animate
from angles_processing import get_leg_angles, target_alpha, target_beta, target_gamma
from common import a, b, c, d, angle_to_rad, rad_to_angle



#a = 10.5
#b = 5.4
#c = 12.2
#d = 5.4
# ground_z = -2 # - deactivated mode
ground_z = -4 # - deactivated mode tower
# ground_z = -10 # - activated mode
# ground_z = -20 # - activated mode tower
k = 14
turn_angle = pi / 96

z_up = 5

margin = 3  # 1 cm from intersection point

# phi_angle = 15
phi_angle = 0
phi = angle_to_rad(phi_angle)

#target_gamma = 0
#target_beta = -30
#target_alpha = -60

body_weight = 500
leg_CD_weight = 100
leg_BC_weight = 50
leg_AB_weight = 150
leg_OA_weight = 50

def get_angle_by_coords(x1, y1):
    l = math.sqrt(x1 ** 2 + y1 ** 2)
    initial_angle = math.asin(abs(y1) / l)
    if x1 >= 0 and y1 >= 0:
        return initial_angle
    if x1 >= 0 and y1 < 0:
        return 2*pi - initial_angle
    if x1 < 0 and y1 >= 0:
        return pi - initial_angle
    if x1 < 0 and y1 < 0:
        return initial_angle + pi


def turn_on_angle(x1, y1, angle):

    if angle >= pi/2:
        raise Exception('Too big angle : {0}'.format(angle))
    l = math.sqrt(x1 ** 2 + y1 ** 2)
    initial_angle = get_angle_by_coords(x1, y1)
    result_angle = angle + initial_angle
    """
    print('In : ({0},{1}, {2}). Out : ({3},{4}, {5})'
          .format(x1,
                  y1,
                  angle,
                  round(cos(result_angle) * l, 2),
                  round(sin(result_angle) * l, 2),
                  result_angle))
    """
    return round(cos(result_angle) * l, 2), round(sin(result_angle) * l, 2)


class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return '({0},{1},{2})'.format(round(self.x, 3), round(self.y, 3), round(self.z, 3))


class Line:
    def __init__(self, Point1, Point2):
        self.Point1 = Point1
        self.Point2 = Point2

    def convert_to_arr(self):
        return [[self.Point1.x, self.Point2.x],
                [self.Point1.y, self.Point2.y],
                [self.Point1.z, self.Point2.z]]



class LinearFunc:
    def __init__(self, point1=None, point2=None, k=None, b=None):
        if point1 is None:
            if k == 0:
                k = 0.00001
            self.k = k
            self.b = b
        else:
            delta_x = (point2.x - point1.x)
            if delta_x == 0:
                delta_x = 0.00001
            self.k = (point2.y - point1.y) / delta_x
            self.b = (point2.x * point1.y - point1.x * point2.y) / delta_x
            self.angle = math.atan2(point2.y - point1.y, point2.x - point1.x)

    def get_y(self, x):
        return self.k * x + self.b

    def get_x(self, y):
        return (y - self.b) / self.k

    def __str__(self):
        return 'y = ({0}) * x + ({1})'.format(round(self.k, 4), round(self.b, 4))


def calculate_intersection(func1, func2):
    x = (func1.b - func2.b) / (func2.k - func1.k)
    y = func1.k * x + func1.b
    return x, y

# function, that moves on a line from a given point to a target point for a margin distance
def move_on_a_line(intersection_point, target_point, margin):
    function = LinearFunc(intersection_point, target_point)
    new_point_x = round(intersection_point.x + math.cos(function.angle) * margin, 2)
    new_point_y = round(intersection_point.y + math.sin(function.angle) * margin, 2)
    return [new_point_x, new_point_y]



def target_body_position(target_leg_positions, unsupporting_leg_number):
    """
    take 4 legs basement points and the unsupporting leg
    return target position of body
    :param target_leg_positions: array: [[leg1_x, leg1_y], [leg2_x, leg2_y], [leg3_x, leg3_y], [leg4_x, leg4_y]]
    :param unsupporting_leg_number: 1 or 2 or 3 or 4
    :return: [body_x, body_y]
    """
    leg1_point = Point(target_leg_positions[0][0], target_leg_positions[0][1], 0)
    leg2_point = Point(target_leg_positions[1][0], target_leg_positions[1][1], 0)
    leg3_point = Point(target_leg_positions[2][0], target_leg_positions[2][1], 0)
    leg4_point = Point(target_leg_positions[3][0], target_leg_positions[3][1], 0)

    # find intersection point
    func1 = LinearFunc(leg1_point, leg3_point)
    func2 = LinearFunc(leg2_point, leg4_point)
    intersection = Point(*calculate_intersection(func1, func2), 0)

    # find a point on targeted line, at a margin distance from intersection point
    if unsupporting_leg_number == 1:
        target_leg = leg3_point
    elif unsupporting_leg_number == 2:
        target_leg = leg4_point
    elif unsupporting_leg_number == 3:
        target_leg = leg1_point
    elif unsupporting_leg_number == 4:
        target_leg = leg2_point
    else:
        raise ValueError('Bad leg number : {0}. Should be 1, 2, 3 or 4'.format(unsupporting_leg_number))

    body_target_point = move_on_a_line(intersection, target_leg, margin)

    return body_target_point


class MovementHistory:
    def __init__(self):
        self.body_lines_history = [[], [], [], []]
        self.line_mass_weight_history = [[]]
        self.basement_lines_history = [[], [], [], [], [], [], [], []]
        self.leg_lines_history = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
        self.unsupporting_leg_lines_history = [[]]
        self._lines_history = []
        self.angles_history = []

    # o1 - o4 = leg1.O - leg4.O
    def add_body_lines(self, o1, o2, o3, o4):
        self.body_lines_history[0].append(Line(o1, o2).convert_to_arr())
        self.body_lines_history[1].append(Line(o2, o3).convert_to_arr())
        self.body_lines_history[2].append(Line(o3, o4).convert_to_arr())
        self.body_lines_history[3].append(Line(o4, o1).convert_to_arr())

    def add_mw_lines(self, wm1, wm2):
        self.line_mass_weight_history[0].append(Line(wm1, wm2).convert_to_arr())

    def add_unsup_leg_line(self, d):
        unsupporting_point_1 = d
        unsupporting_point_2 = Point(d.x, d.y, d.z + 10)
        self.unsupporting_leg_lines_history[0].append(Line(unsupporting_point_1, unsupporting_point_2).convert_to_arr())

    # d1 - d4 = leg1.D - leg4.D
    def add_basement_lines(self, d1, d2, d3, d4, ground_z):
        LF_13 = LinearFunc(point1=d1, point2=d3)
        LF_24 = LinearFunc(point1=d2, point2=d4)
        intersection = calculate_intersection(LF_13, LF_24)
        legs_center = Point(intersection[0], intersection[1], ground_z)

        LM_12 = Point(d1.x, d1.y, ground_z)
        LM_23 = Point(d2.x, d2.y, ground_z)
        LM_34 = Point(d3.x, d3.y, ground_z)
        LM_14 = Point(d4.x, d4.y, ground_z)

        leg1_D_projection = Point(d1.x, d1.y, ground_z)
        leg2_D_projection = Point(d2.x, d2.y, ground_z)
        leg3_D_projection = Point(d3.x, d3.y, ground_z)
        leg4_D_projection = Point(d4.x, d4.y, ground_z)

        self.basement_lines_history[0].append(Line(leg1_D_projection, leg2_D_projection).convert_to_arr())
        self.basement_lines_history[1].append(Line(leg2_D_projection, leg3_D_projection).convert_to_arr())
        self.basement_lines_history[2].append(Line(leg3_D_projection, leg4_D_projection).convert_to_arr())
        self.basement_lines_history[3].append(Line(leg1_D_projection, leg4_D_projection).convert_to_arr())

        self.basement_lines_history[4].append(Line(LM_12, legs_center).convert_to_arr())
        self.basement_lines_history[5].append(Line(LM_23, legs_center).convert_to_arr())
        self.basement_lines_history[6].append(Line(LM_34, legs_center).convert_to_arr())
        self.basement_lines_history[7].append(Line(LM_14, legs_center).convert_to_arr())

    def add_leg_lines(self, leg1, leg2, leg3, leg4):
        i = 0
        for leg in [leg1, leg2, leg3, leg4]:
            self.leg_lines_history[4 * i].append(Line(leg.O, leg.A).convert_to_arr())
            self.leg_lines_history[4 * i + 1].append(Line(leg.A, leg.B).convert_to_arr())
            self.leg_lines_history[4 * i + 2].append(Line(leg.B, leg.C).convert_to_arr())
            self.leg_lines_history[4 * i + 3].append(Line(leg.C, leg.D).convert_to_arr())
            i += 1

    @property
    def lines_history(self):
        self._lines_history.extend(self.body_lines_history[:])
        self._lines_history.extend(self.leg_lines_history)
        self._lines_history.extend(self.line_mass_weight_history)
        self._lines_history.extend(self.basement_lines_history)
        self._lines_history.extend(self.unsupporting_leg_lines_history)
        return self._lines_history

    def add_angles_snapshot(self, leg1, leg2, leg3, leg4):
        # angles are : gamma1, beta1, alpha1, tetta1, gamma2, beta2, alpha2, tetta2 ...
        # for leg1 tetta = 45 means 0 for servo
        # leg2 tetta = -45, leg3 tetta = -135, leg4 tetta = 135

        position = []
        for leg in [leg1, leg4, leg3, leg2]:
            position.append(round(rad_to_angle(leg.gamma), 2))
            position.append(round(rad_to_angle(leg.beta), 2))
            position.append(-1 * round(rad_to_angle(leg.alpha), 2))
            tetta = rad_to_angle(leg.tetta)
            if leg == leg1:
                tetta -= 45
            if leg == leg2:
                tetta += 45
            if leg == leg3:
                tetta += 135
            if leg == leg4:
                tetta -= 135
            tetta = round(tetta, 2)
            position.append(tetta)
        self.angles_history.append(position)


#################################################################


class Leg:
    def __init__(self, number, name, O, D, alpha, beta, gamma):
        self.number = number
        self.name = name
        self.O = O
        self.A = None
        self.B = None
        self.C = None
        self.D = D
        self.tetta = None
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.calculate_angles()

    def __str__(self):
        return '{0}. O: {1} -> A: {2} -> B: {3} -> C: {4} -> D: {5}. Angles : {6}' \
            .format(self.name,
                    self.O,
                    self.A,
                    self.B,
                    self.C,
                    self.D,
                    angles_str([self.tetta,
                                self.alpha,
                                self.beta,
                                self.gamma]))

    @staticmethod
    def move_point(point, delta_x, delta_y, delta_z):
        point.x += delta_x
        point.y += delta_y
        point.z += delta_z

    def move_mount_point(self, delta_x, delta_y, delta_z):
        #)
        #print('Got command to move point O for ({0},{1},{2})'.format(delta_x, delta_y, delta_z))
        self.move_point(self.O, delta_x, delta_y, delta_z)
        self.calculate_angles()

    def move_end_point(self, delta_x, delta_y, delta_z):
        #print(self)
        #print('Got command to move point D for ({0},{1},{2})'.format(delta_x, delta_y, delta_z))
        self.move_point(self.D, delta_x, delta_y, delta_z)
        self.calculate_angles()

    # means one leg is raised and moves with the body
    # end_delta = 0 means that leg is not moving, else it is also moving somehow
    def move_both_points(self, delta_x, delta_y, delta_z, end_delta_x, end_delta_y, end_delta_z):
        self.move_point(self.O, delta_x, delta_y, delta_z)
        self.move_point(self.D,
                        delta_x + end_delta_x,
                        delta_y + end_delta_y,
                        delta_z + end_delta_z)
        self.calculate_angles()

    def calculate_angles(self):
        try:
            #print('Before angles : {0}'.format(self))
            pass
        except:
            pass
        O = self.O
        D = self.D

        tetta = math.atan2(D.y - O.y, D.x - O.x)
        A = Point(O.x + d * cos(tetta), O.y + d * sin(tetta), O.z)
        l = math.sqrt((D.x - A.x) ** 2 + (D.y - A.y) ** 2)
        delta_z = D.z - O.z
        #best_angles = get_leg_angles(l, delta_z)
        #alpha, beta, gamma = best_angles[0], best_angles[1], best_angles[2]
        alpha, beta, gamma = get_leg_angles(l, delta_z)

        Bx = a * cos(alpha)
        By = a * sin(alpha)
        Cx = Bx + b * cos(alpha + beta)
        Cy = By + b * sin(alpha + beta)
        Dx = Cx + c * cos(alpha + beta + gamma)
        Dy = Cy + c * sin(alpha + beta + gamma)
        if abs(Dx - l) > 0.01 or abs(Dy - delta_z) > 0.01:
            print('WTF')

        B_xz = [a * cos(alpha), a * sin(alpha)]
        C_xz = [B_xz[0] + b * cos(alpha + beta), B_xz[1] + b * sin(alpha + beta)]
        D_xz = [C_xz[0] + c * cos(alpha + beta + gamma), C_xz[1] + c * sin(alpha + beta + gamma)]

        # print('XZ-projection. B : {0}. C : {1}. D : {2}.'.format(B_xz, C_xz, D_xz))
        D_prev = D
        self.A = A
        self.B = Point(A.x + B_xz[0] * cos(tetta), A.y + B_xz[0] * sin(tetta), A.z + B_xz[1])
        self.C = Point(A.x + C_xz[0] * cos(tetta), A.y + C_xz[0] * sin(tetta), A.z + C_xz[1])
        self.D = Point(A.x + D_xz[0] * cos(tetta), A.y + D_xz[0] * sin(tetta), A.z + D_xz[1])
        if abs(D_prev.x - self.D.x) > 0.01 or abs(D_prev.y - self.D.y) > 0.01 or abs(D_prev.z - self.D.z) > 0.01:
            #print('wtf')
            raise Exception('D_prev far from D. Angles : {0}'.format(angles_str([tetta, alpha, beta, gamma])))
        # print('XYZ-projection. B : {0}. C : {1}. D : {2}.'.format(self.B, self.C, self.D))

        self.tetta, self.alpha, self.beta, self.gamma = tetta, alpha, beta, gamma
        #print('After angles : {0}'.format(self))

"""
def get_leg_angles(delta_x, delta_z):
    print('Looking for angles for ({0}, {1})'.format(delta_x, delta_z))
    possible_angles = find_angles(delta_x, delta_z)

    # recalculating to check for some error
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
            print('WTF')

    return get_best_angles(possible_angles)
"""

def angles_str(angles):
    result = ''
    for item in angles:
        result += '{0} '.format(round(180 * item / pi, 2))
    return result

"""
def check_angles(angles):
    alpha = rad_to_angle(angles[0])
    beta = rad_to_angle(angles[1])
    gamma = rad_to_angle(angles[2])
    angles_converted = str([round(x, 2) for x in [alpha, beta, gamma]])
    if alpha < -80 or alpha > 80:
        return False, angles_converted + ' alpha={0}'.format(alpha)
    if beta < -80 or beta > 80:
        return False,  angles_converted + '. beta={0}'.format(beta)
    if gamma < -80 or gamma > 80:
        return False, angles_converted + '. gamma={0}'.format(gamma)
    if alpha + beta < -90 or alpha + beta > 80:
        return False, angles_converted + '. alpha + beta = {0}'.format(alpha + beta)
    if alpha + beta + gamma < -135 or alpha + beta + gamma > -45:
        return False, angles_converted + '. alpha + beta = {0}'.format(alpha + beta + gamma)
    
    return True, 'All ok'
"""
"""
def get_best_angles(all_angles):
    min_distance = 1000
    best_angles = None
    print_angles = False
    for item in all_angles:
        if not check_angles(item)[0]:
            continue        
        cur_distance = get_angles_distance(item, [target_alpha, target_beta, target_gamma])
        # print('Angles : {0}. Distance : {1}'.format(angles_str(item), cur_distance))
        if cur_distance <= min_distance:
            min_distance = cur_distance
            best_angles = item[:]
    # print(angles_str(best_angles), min_distance)
    if best_angles is None:
        #print('No suitable angles found. Halt')
        for angle in all_angles:
            print(check_angles(angle)[1])
        raise Exception('No angles\n')
        # sys.exit(1)
    return best_angles
"""
"""
def find_angles(Dx, Dy):
    results = []
    full_dist = math.sqrt(Dx ** 2 + Dy ** 2)
    if full_dist > a + b + c:
        #print('No decisions. Full distance : {0}'.format(full_dist))
        raise Exception('No decisions. Full distance : {0}'.format(full_dist))
        #sys.exit(1)

    #for k in np.arange(-35.0, 35.0, 0.1):
    for k in np.arange(-45.0, 45.0, 0.5):
        if stable_mode and k != 0:
            continue

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
"""
"""
def get_angles_distance(angles1, angles2):
    # weight of gamma is 1.5 !!!
    return math.sqrt((angles1[0] - angles2[0]) ** 2 +
                     (angles1[1] - angles2[1]) ** 2 +
                     1.5 * (angles1[2] - angles2[2]) ** 2)
"""
###########################################################################


class MovementSequence:
    def __init__(self, Leg1, Leg2, Leg3, Leg4, step=0.5):
        self.step = step
        self.ground_z = ground_z
        self.mass_center_distance = 0
        self.mass_center_distance_gen2 = None
        self.mass_center = None
        self.unsupporting_leg = None
        self.target_unsupporting_leg = None
        self.mh = MovementHistory()

        self.Leg1 = Leg1
        self.Leg2 = Leg2
        self.Leg3 = Leg3
        self.Leg4 = Leg4
        self.Legs = [self.Leg1, self.Leg2, self.Leg3, self.Leg4]
        self.post_movement_actions()

    def __str__(self):
        result = '-------------------------------------- MS -------------------------------------\n'
        result += '\n'.join('{0}'.format(x) for x in self.Legs)
        return result

    def save_angles(self):
        self.mh.add_angles_snapshot(self.Leg1, self.Leg2, self.Leg3, self.Leg4)

    def post_movement_actions(self):
        # self.calculate_unsupporting_leg()
        self.save_angles()
        self.log_movement_history()

    def log_movement_history(self):
        self.mh.add_leg_lines(self.Leg1, self.Leg2, self.Leg3, self.Leg4)
        self.mh.add_body_lines(self.Leg1.O, self.Leg2.O, self.Leg3.O, self.Leg4.O)
        self.mass_center = self.calculate_mass_center()
        wm1 = Point(self.mass_center[0], self.mass_center[1], self.Leg1.O.z)
        wm2 = Point(self.mass_center[0], self.mass_center[1], self.ground_z)
        self.mh.add_mw_lines(wm1, wm2)
        self.mh.add_basement_lines(self.Leg1.D, self.Leg2.D, self.Leg3.D, self.Leg4.D, self.ground_z)
        try:
            self.mh.add_unsup_leg_line(self.unsupporting_leg.D)
        except:
            self.mh.add_unsup_leg_line(self.Leg1.D)

        # LM - legs middle point, LM_12 - middle of legs 1 and 2
        # ALL projected to self.ground_z
   
    def body_movement(self, delta_x, delta_y, delta_z, leg_up=None, leg_up_delta=[0, 0, 0]):
        if delta_x == delta_y == delta_z == 0:
            #print('No movement required')
            return
        max_delta = max(abs(delta_x), abs(delta_y), abs(delta_z),
                        abs(leg_up_delta[0]), abs(leg_up_delta[1]), abs(leg_up_delta[2]))

        num_steps = int(max_delta / self.step) + 1
        _delta_x = round(delta_x / num_steps, 4)
        _delta_y = round(delta_y / num_steps, 4)
        _delta_z = round(delta_z / num_steps, 4)
        _end_delta_x = round(leg_up_delta[0] / num_steps, 4)
        _end_delta_y = round(leg_up_delta[1] / num_steps, 4)
        _end_delta_z = round(leg_up_delta[2] / num_steps, 4)

        for m in range(num_steps):
            #print('----------------------------- next step ------------------------------')
            ms1 = copy.deepcopy(self)
            if leg_up == self.Leg1:
                self.Leg1.move_both_points(_delta_x, _delta_y, _delta_z,
                                           _end_delta_x, _end_delta_y, _end_delta_z)
            else:
                self.Leg1.move_mount_point(_delta_x, _delta_y, _delta_z)

            if leg_up == self.Leg2:
                self.Leg2.move_both_points(_delta_x, _delta_y, _delta_z,
                                           _end_delta_x, _end_delta_y, _end_delta_z)
            else:
                self.Leg2.move_mount_point(_delta_x, _delta_y, _delta_z)

            if leg_up == self.Leg3:
                self.Leg3.move_both_points(_delta_x, _delta_y, _delta_z,
                                           _end_delta_x, _end_delta_y, _end_delta_z)
            else:
                self.Leg3.move_mount_point(_delta_x, _delta_y, _delta_z)

            if leg_up == self.Leg4:
                self.Leg4.move_both_points(_delta_x, _delta_y, _delta_z,
                                           _end_delta_x, _end_delta_y, _end_delta_z)
            else:
                self.Leg4.move_mount_point(_delta_x, _delta_y, _delta_z)

            for leg1 in [self.Leg1, self.Leg2, self.Leg3, self.Leg4]:
                for leg2 in [ms1.Leg1, ms1.Leg2, ms1.Leg3, ms1.Leg4]:
                    if leg1.number == leg2.number:
                        deltas = [0, 0, 0]
                        if leg_up == leg1:
                            deltas = [_end_delta_x, _end_delta_y, _end_delta_z]
                        if abs(leg1.D.x - leg2.D.x + deltas[0]) > 0.1 \
                           or abs(leg1.D.y - leg2.D.y + deltas[1]) > 0.1 \
                           or abs(leg1.D.z - leg2.D.z + deltas[2]) > 0.1:
                            print(leg1)
                            print(leg2)
                            raise Exception('Leg should not move! ({0}, {1}, {2})'
                                            .format(leg1.D.x - leg2.D.x + deltas[0],
                                                    leg1.D.y - leg2.D.y + deltas[1],
                                                    leg1.D.z - leg2.D.z + deltas[2]))

            self.post_movement_actions()

    def body_to_center(self):
        # move body to center
        avg_o_x, avg_o_y, avg_d_x, avg_d_y = 0, 0, 0, 0
        for leg in self.Legs:
            avg_o_x += leg.O.x
            avg_o_y += leg.O.y
            avg_d_x += leg.D.x
            avg_d_y += leg.D.y

        avg_o_x /= 4
        avg_o_y /= 4
        avg_d_x /= 4
        avg_d_y /= 4

        self.body_movement(avg_d_x - avg_o_x, avg_d_y - avg_o_y, 0)

    def turn_body(self, angle):
        num_steps = int(abs(angle / turn_angle))
        step_angle = round(angle / num_steps, 4)

        for m in range(num_steps):
            for leg in self.Legs:
                x_new, y_new = turn_on_angle(leg.O.x, leg.O.y, step_angle)
                delta_x = x_new - leg.O.x
                delta_y = y_new - leg.O.y
                leg.move_mount_point(delta_x, delta_y, 0)
            self.post_movement_actions()

    @property
    def lines_history(self):
        return self.mh.lines_history

    # LM - legs middle point, LM12 - middle point between legs 1 and 2, and so on
    def calculate_basement_points(self):
        LF_13 = LinearFunc(point1=self.Leg1.D, point2=self.Leg3.D)
        LF_24 = LinearFunc(point1=self.Leg2.D, point2=self.Leg4.D)

        intersection = calculate_intersection(LF_13, LF_24)
        LM = Point(intersection[0], intersection[1], self.ground_z)
        return LM

    def calculate_mass_center(self):
        weight_points = []
        for leg in [self.Leg1, self.Leg2, self.Leg3, self.Leg4]:
            weight_points.append([(leg.O.x + leg.A.x) / 2, (leg.O.y + leg.A.y) / 2, leg_OA_weight])
            weight_points.append([(leg.A.x + leg.B.x) / 2, (leg.A.y + leg.B.y) / 2, leg_AB_weight])
            weight_points.append([(leg.B.x + leg.C.x) / 2, (leg.B.y + leg.C.y) / 2, leg_BC_weight])
            weight_points.append([(leg.C.x + leg.D.x) / 2, (leg.C.y + leg.D.y) / 2, leg_CD_weight])
        weight_points.append([(self.Leg1.O.x + self.Leg2.O.x + self.Leg3.O.x + self.Leg4.O.x) / 4,
                              (self.Leg1.O.y + self.Leg2.O.y + self.Leg3.O.y + self.Leg4.O.y) / 4,
                              body_weight])

        weight_sum = 0
        mass_center_x = 0
        mass_center_y = 0
        for item in weight_points:
            mass_center_x += item[0] * item[2]
            mass_center_y += item[1] * item[2]
            weight_sum += item[2]

        return [round(mass_center_x / weight_sum, 2), round(mass_center_y / weight_sum, 2)]

    def leg_movement(self, leg_num, leg_delta):
        if leg_num == 1:
            leg = self.Leg1
        elif leg_num == 2:
            leg = self.Leg2
        elif leg_num == 3:
            leg = self.Leg3
        elif leg_num == 4:
            leg = self.Leg4

        max_delta = max(abs(x) for x in leg_delta)
        num_steps = int(max_delta / self.step)
        leg_delta = [round(x / num_steps, 4) for x in leg_delta]
        for m in range(num_steps):
            for my_leg in [self.Leg1, self.Leg2, self.Leg3, self.Leg4]:
                if my_leg == leg:
                    #self._leg_move(my_leg, leg_delta)
                    my_leg.move_end_point(leg_delta[0], leg_delta[1], leg_delta[2])
                #else:
                    #self._leg_move(my_leg, None)
                #    my_leg.move_end_point(0, 0, 0)
            self.post_movement_actions()

    @staticmethod
    def _leg_move(Leg, delta=None):
        if delta is None:
            Leg.move_end_point(0, 0, 0)
        else:
            Leg.move_end_point(delta[0], delta[1], delta[2])
    
    def print_to_sequence_file(self):
        with open(sequence_file, 'w') as f:
            f.write('\n'.join(str(x) for x in self.mh.angles_history))
    

    def run_animation(self, delay=100):
        animate(self.lines_history, delay)


def ms_to_array(ms):
    ms_array = []
    for leg in [ms.Leg1, ms.Leg2, ms.Leg3, ms.Leg4]:
        ms_array.append([round(leg.O.x, 2),
                         round(leg.O.y, 2),
                         round(leg.O.z, 2),
                         round(leg.D.x, 2),
                         round(leg.D.y, 2),
                         round(leg.D.z, 2),
                         round(leg.alpha, 5),
                         round(leg.beta, 5),
                         round(leg.gamma, 5),
                         round(leg.tetta, 5)])
    return ms_array


def create_new_ms(step=0.5, ms_array=None):
    if ms_array is None:
        O1 = Point(4.5, 4.5, 0)
        D1 = Point(k, k, ground_z)
        Leg1 = Leg(1, "Leg1", O1, D1, angle_to_rad(target_alpha), angle_to_rad(target_beta), angle_to_rad(target_gamma))

        O2 = Point(4.5, -4.5, 0)
        D2 = Point(k, -k, ground_z)
        Leg2 = Leg(2, "Leg2", O2, D2, angle_to_rad(target_alpha), angle_to_rad(target_beta), angle_to_rad(target_gamma))

        O3 = Point(-4.5, -4.5, 0)
        D3 = Point(-k, -k, ground_z)
        Leg3 = Leg(3, "Leg3", O3, D3, angle_to_rad(target_alpha), angle_to_rad(target_beta), angle_to_rad(target_gamma))

        O4 = Point(-4.5, 4.5, 0)
        D4 = Point(-k, k, ground_z)
        Leg4 = Leg(4, "Leg4", O4, D4, angle_to_rad(target_alpha), angle_to_rad(target_beta), angle_to_rad(target_gamma))
    else:
        for i in range(4):
            leg = ms_array[i]
            O = Point(leg[0], leg[1], leg[2])
            D = Point(leg[3], leg[4], leg[5])
            if i == 0:
                Leg1 = Leg(1, "Leg1", O, D, leg[6], leg[7], leg[8])
            if i == 1:
                Leg2 = Leg(2, "Leg2", O, D, leg[6], leg[7], leg[8])
            if i == 2:
                Leg3 = Leg(3, "Leg3", O, D, leg[6], leg[7], leg[8])
            if i == 3:
                Leg4 = Leg(4, "Leg4", O, D, leg[6], leg[7], leg[8])

    return MovementSequence(Leg1, Leg2, Leg3, Leg4, step=step)


def body_compensation_for_leg_delta(ms, leg_num, leg_delta):

    legs_coords_array = [[ms.Leg1.D.x + leg_delta[0][0], ms.Leg1.D.y  + leg_delta[0][1]],
                   [ms.Leg2.D.x + leg_delta[1][0], ms.Leg2.D.y + leg_delta[1][1]],
                   [ms.Leg3.D.x + leg_delta[2][0], ms.Leg3.D.y + leg_delta[2][1]],
                   [ms.Leg4.D.x + leg_delta[3][0], ms.Leg4.D.y + leg_delta[3][1]]]

    target = target_body_position(legs_coords_array, leg_num)

    current_body = [(ms.Leg1.O.x + ms.Leg2.O.x + ms.Leg3.O.x + ms.Leg4.O.x)/4,
                    (ms.Leg1.O.y + ms.Leg2.O.y + ms.Leg3.O.y + ms.Leg4.O.y)/4]

    ms.body_movement(target[0] - current_body[0], target[1] - current_body[1], 0)


def compensated_leg_movement(ms, leg_num, leg_delta):
    full_leg_delta = [[0, 0], [0, 0], [0, 0], [0, 0]]
    if leg_num == 1:
        leg = ms.Leg1
        full_leg_delta[0] = [leg_delta[0], leg_delta[1]]
    elif leg_num == 2:
        leg = ms.Leg2
        full_leg_delta[1] = [leg_delta[0], leg_delta[1]]
    elif leg_num == 3:
        leg = ms.Leg3
        full_leg_delta[2] = [leg_delta[0], leg_delta[1]]
    elif leg_num == 4:
        leg = ms.Leg4
        full_leg_delta[3] = [leg_delta[0], leg_delta[1]]

    # moving body to compensate future movement
    body_compensation_for_leg_delta(ms, leg_num, full_leg_delta)

    max_delta = max(abs(x) for x in leg_delta)
    num_steps = int(max_delta / ms.step)
    leg_delta = [round(x / num_steps, 4) for x in leg_delta]
    for m in range(num_steps):
        leg.move_end_point(leg_delta[0], leg_delta[1], leg_delta[2])
        ms.post_movement_actions()


def move_legs_z(ms, legs_delta_z, leg_seq):
    max_delta = max(abs(x) for x in legs_delta_z)
    num_steps = int(max_delta / ms.step)
    leg_delta_step = [round(x / num_steps, 4) for x in legs_delta_z]

    for m in range(num_steps):
        for i in range(len(leg_seq)):
            leg_seq[i].move_end_point(0, 0, leg_delta_step[i])
        ms.post_movement_actions()


def leg_move_with_compensation(ms, leg_num, delta_x, delta_y):
    #compensated_leg_movement(ms, leg_num, [0, 0, z_up])
    #compensated_leg_movement(ms, leg_num, [delta_x, delta_y, 0])
    compensated_leg_movement(ms, leg_num, [delta_x, delta_y, z_up])
    compensated_leg_movement(ms, leg_num, [0, 0, -z_up])


def turn_body(ms, angle_deg):
    angle = angle_to_rad(angle_deg)
    # move leg one by one
    for leg in [ms.Leg1, ms.Leg3, ms.Leg2, ms.Leg4]:
        x_new, y_new = turn_on_angle(leg.D.x, leg.D.y, angle)
        delta_x = x_new - leg.D.x
        delta_y = y_new - leg.D.y
        leg_move_with_compensation(ms, leg.number, delta_x, delta_y)

    ms.body_to_center()

    ms.turn_body(angle)


def move_body_straight(ms, delta_x, delta_y, leg_seq=[1, 2, 3, 4], body_to_center=False):
    for leg in leg_seq:
        leg_move_with_compensation(ms, leg, delta_x, delta_y)
    if body_to_center:
        ms.body_to_center()


ms = create_new_ms(step=0.2)

sequence_file = 'D:\\Development\\Python\\cybernetic_core\\sequences\\deactivation_tow.txt'

#move_body_straight(ms, -4, 0, leg_seq=[4, 3, 2, 1], body_to_center=True)
#move_body_straight(ms, 4, 0, body_to_center=True)
#move_legs_z(ms, [4, 4, -6, -6], leg_seq=[ms.Leg1, ms.Leg2, ms.Leg3, ms.Leg4])
#move_legs_z(ms, [-4, -4, 6, 6], leg_seq=[ms.Leg1, ms.Leg2, ms.Leg3, ms.Leg4])
#move_legs_z(ms, [10, 10, -10, -10], leg_seq=[ms.Leg1, ms.Leg2, ms.Leg3, ms.Leg4])
#move_legs_z(ms, [-4, -4, 6, 6], leg_seq=[ms.Leg1, ms.Leg2, ms.Leg3, ms.Leg4])
#ms.print_to_sequence_file()
# теоретически, при очень длинных движениях оно может упасть, если слишком большой перекос в ногах
# можно пофиксить, если пересчитывать компенсацию корпусом на каждой итерации движения ноги

# -9, 14

try:
    
    ms.body_movement(0, 0, 14)
    ms.body_movement(0, 0, -14)
    # ms.body_movement(0, 0, 5)
    #turn_body(ms, 15)
    pass
except:
    print('Fail')

ms.run_animation(delay=5)
