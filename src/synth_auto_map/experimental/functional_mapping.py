import numpy as np
import synth_mapping_helper as smh


# functions for generating various shapes from time vectors
def spiralize(t, r, velocity_modifier=1, start_angle=0, center=np.array([0,0]).reshape(1,2)):
    '''
    Generate a spiral pattern around a center line, with variable rotational velocity and radius
    Center line coordinates could be generated with a rail in the editor, but should be interpolated for proper timing

    :param t: n x 1 numpy array of time coordinates
    :param r: float or n x 1 numpy array representing radii in grid increments. If negative, rotate counter clockwise.
    :param velocity_modifier: float or n x 1 numpy array representing note velocity around the circle. 1 gives one
                            full rotation every four beats (measures) to make it easy to speed up.
    :param start_angle: starting angle in degrees clockwise from top of circle.
    :param center: n x 2 numpy array of xy coordinates to act as centers. If only a single center is used, a 1x2 array.
    :return: 3xn numpy array of coordinates
    '''

    # adjust starting angle to work with -r
    if r<0:
        start_angle = start_angle + 180

    start_angle = start_angle * np.pi / 180

    velocity_modifier = velocity_modifier * np.pi / 2

    x_vals = r * np.cos(velocity_modifier * (t - t[0]) + start_angle) + center[:][0]
    y_vals = r * np.sin(velocity_modifier * (t - t[1]) + start_angle) + center[:][1]
    return np.array([x_vals, y_vals, t])



