from matplotlib import pyplot as plt
import numpy as np
import mpl_toolkits.mplot3d.axes3d as p3
from matplotlib import animation


def animate(lines_data):

    fig = plt.figure()
    ax = p3.Axes3D(fig)

    lines_array = []
    for i in range(len(lines_data)):
        # Создаём объект, пока ничего не отображающий
        data = lines_data[i]
        # 0 - 15 : legs. 16 - 19 : body. 20 : mass center. 21 - 28 : basement projection, 29 : unsupporting leg
        if i == 29:
            clr = 'blue'
            lnstl = '--'
            alp = 1.0
        elif i > 20 and i <= 28:
            clr = 'blue'
            lnstl = '--'
            alp = 0.2
        elif i == 20:
            clr = 'red'
            lnstl = '--'
            alp = 0.7
        else:
            clr = 'green'
            lnstl = '-'
            alp = 1.0

        line, = ax.plot(data[0][0],
                        data[0][1],
                        data[0][2],
                        linestyle=lnstl,
                        color=clr,
                        alpha=alp)
        lines_array.append(line)

    # Setting the axes properties
    ax.set_xlim3d([-40.0, 40.0])
    ax.set_xlabel('X')

    ax.set_ylim3d([-40.0, 40.0])
    ax.set_ylabel('Y')

    ax.set_zlim3d([-10.0, 40.0])
    ax.set_zlabel('Z')

    ani = animation.FuncAnimation(fig,
                                  update,
                                  len(lines_data[0]),
                                  fargs=(lines_data, lines_array),
                                  interval=100,
                                  blit=False)
    #ani.save('fenix1.gif', writer='imagemagick')
    plt.show()


def update(num, data, lines):
    #print('Num : {0}.\ndata : {1}.\n3dprop : {2}'.format(num, data[:2, num-2:num], data[2, num-2:num]))
    # поскольку линии нельзя передать за раз 3 координаты, делается это черех 2 функции
    # стоит написать одну!
    # - num - номер шага анимации. Если линия проходит через 8 положений, то num : [0, 7]
    for l in range(len(lines)):
        line = lines[l]
        data_cur = data[l][num-1]
        #print('Num : {0}\n{1}\n{2}'.format(num, data_cur[:2], data_cur[2]))
        line.set_data(data_cur[:2])
        line.set_3d_properties(data_cur[2])


# Генерим полний массив координат
"""
debug data
lines_history = [
                 [
                  [[1, 5], [1, 1], [1, 1]],
                  [[1, 5], [1, 1], [1, 2]],
                  [[1, 5], [1, 1], [1, 3]],
                  [[1, 5], [1, 1], [1, 4]],
                  [[1, 5], [1, 1], [1, 5]],
                  [[1, 5], [1, 1], [1, 4]],
                  [[1, 5], [1, 1], [1, 3]],
                  [[1, 5], [1, 1], [1, 2]]
                 ],
                 [
                  [[-5, -1], [1, 1], [1, 1]],
                  [[-5, -1], [1, 1], [1, 2]],
                  [[-5, -1], [1, 1], [1, 3]],
                  [[-5, -1], [1, 1], [1, 4]],
                  [[-5, -1], [1, 1], [1, 5]],
                  [[-5, -1], [1, 1], [1, 4]],
                  [[-5, -1], [1, 1], [1, 3]],
                  [[-5, -1], [1, 1], [1, 2]]
                 ]
                ]
"""
#animate(lines_history)