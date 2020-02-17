from kinematics_v2 import *

#margin = 4
#z_up = 6
#k = 13
#mode = 40
step_len = 10

sq_file_prefix = 'D:\\Development\\Python\\cybernetic_core\\sequences\\sq_'

grounds_z = [3, 10, 15, 20]

for i in range(len(grounds_z) - 1):
    ground_z = -grounds_z[i+1]
    
    # move forward
    sq_file = f'{sq_file_prefix}forward_{-ground_z}.txt'
    print(sq_file)
    ms = create_new_ms(ground_z, k, step=0.5)
    move_body_straight(ms, 0, step_len, leg_seq=[1, 4, 3, 2], body_to_center=True)    
    ms.print_to_sequence_file(sq_file)

    # move backwards
    sq_file = f'{sq_file_prefix}backwards_{-ground_z}.txt'
    print(sq_file)
    ms = create_new_ms(ground_z, k, step=0.5)
    move_body_straight(ms, 0, -step_len, leg_seq=[2, 3, 4, 1], body_to_center=True)    
    ms.print_to_sequence_file(sq_file)

    # straferight
    sq_file = f'{sq_file_prefix}straferight_{-ground_z}.txt'
    print(sq_file)
    ms = create_new_ms(ground_z, k, step=0.5)
    move_body_straight(ms, step_len, 0, leg_seq=[2, 1, 3, 4], body_to_center=True)    
    ms.print_to_sequence_file(sq_file)

    # strafeleft
    sq_file = f'{sq_file_prefix}strafeleft_{-ground_z}.txt'
    print(sq_file)
    ms = create_new_ms(ground_z, k, step=0.5)
    move_body_straight(ms, -step_len, 0, leg_seq=[4, 3, 1, 2], body_to_center=True)    
    ms.print_to_sequence_file(sq_file)

    # lookright
    sq_file = f'{sq_file_prefix}lookright_{-ground_z}.txt'
    print(sq_file)
    ms = create_new_ms(ground_z, k, step=0.1)
    ms.turn_body(angle_to_rad(-30))
    ms.sleep(30)
    ms.turn_body(angle_to_rad(30))    
    ms.print_to_sequence_file(sq_file)
    
    # lookleft
    sq_file = f'{sq_file_prefix}lookleft_{-ground_z}.txt'
    print(sq_file)
    ms = create_new_ms(ground_z, k, step=0.1)
    ms.turn_body(angle_to_rad(30))
    ms.sleep(30)
    ms.turn_body(angle_to_rad(-30))    
    ms.print_to_sequence_file(sq_file)
    
    # turnright
    sq_file = f'{sq_file_prefix}turnright_{-ground_z}.txt'
    print(sq_file)
    ms = create_new_ms(ground_z, k, step=0.1)
    turn_body(ms, -25)
    ms.print_to_sequence_file(sq_file)

    # turnleft
    sq_file = f'{sq_file_prefix}turnleft_{-ground_z}.txt'
    print(sq_file)
    ms = create_new_ms(ground_z, k, step=0.1)
    turn_body(ms, 25)
    ms.print_to_sequence_file(sq_file)
    
    # lookup
    sq_file = f'{sq_file_prefix}lookup_{-ground_z}.txt'
    print(sq_file)
    ms = create_new_ms(ground_z, k, step=0.1)
    n = 3
    move_legs_z(ms, [-n, n, n, -n], leg_seq=[ms.Leg1, ms.Leg2, ms.Leg3, ms.Leg4])
    ms.sleep(30)
    move_legs_z(ms, [n, -n, -n, n], leg_seq=[ms.Leg1, ms.Leg2, ms.Leg3, ms.Leg4])
    ms.print_to_sequence_file(sq_file)

    # lookdown
    sq_file = f'{sq_file_prefix}lookdown_{-ground_z}.txt'
    print(sq_file)
    ms = create_new_ms(ground_z, k, step=0.1)
    n = 3
    move_legs_z(ms, [n, -n, -n, n], leg_seq=[ms.Leg1, ms.Leg2, ms.Leg3, ms.Leg4])
    ms.sleep(30)
    move_legs_z(ms, [-n, n, n, -n], leg_seq=[ms.Leg1, ms.Leg2, ms.Leg3, ms.Leg4])
    ms.print_to_sequence_file(sq_file)

    # up
    sq_file = f'{sq_file_prefix}up_{grounds_z[i]}_{grounds_z[i+1]}.txt'
    print(sq_file)
    ms = create_new_ms(-grounds_z[i], k, step=0.1)
    activation_move = grounds_z[i+1] - grounds_z[i]
    ms.body_movement(0, 0, activation_move)
    ms.print_to_sequence_file(sq_file)

    # down
    for j in range(i+1):
        sq_file = f'{sq_file_prefix}down_{grounds_z[i+1]}_{grounds_z[j]}.txt'
        print(sq_file)
        ms = create_new_ms(-grounds_z[i+1], k, step=0.1)
        deactivation_move = grounds_z[j] - grounds_z[i+1]
        ms.body_movement(0, 0, deactivation_move)
        ms.print_to_sequence_file(sq_file)

    

#ms.run_animation(delay=50)
