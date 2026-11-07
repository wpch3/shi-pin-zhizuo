"""Oval comic-speech-bubble tail geometry.

Adapted from splargdotcom/speechbubble (MIT License):
https://github.com/splargdotcom/speechbubble
Original geometry.js copyright (c) 2025-2026 Louie Savva.
See assets/licenses/speechbubble-MIT.txt for the complete license.
"""
from math import atan2, cos, hypot, sin


def clamp(value, low, high):
    return min(high, max(low, value))


def lerp(a, b, amount):
    return a + (b - a) * amount


def quad_point(p0, p1, p2, t):
    u = 1 - t
    return (u*u*p0[0] + 2*u*t*p1[0] + t*t*p2[0],
            u*u*p0[1] + 2*u*t*p1[1] + t*t*p2[1])


def oval_tail(center, size, target, tail_length=30, tail_width=28, bend=2):
    """Return sampled open-source Q-curve tail contours and the tail tip."""
    cx, cy = center
    rx, ry = size[0] / 2, size[1] / 2
    theta = atan2((target[1]-cy)/ry, (target[0]-cx)/rx)
    edge = (cx+cos(theta)*rx, cy+sin(theta)*ry)
    ux, uy = cos(theta), sin(theta)
    remaining = max(0, hypot(target[0]-edge[0], target[1]-edge[1]))
    length = min(tail_length, max(20, remaining*0.22))
    tip = (edge[0]+ux*length, edge[1]+uy*length)

    delta = clamp(tail_width/max(80, min(rx, ry)*2), 0.08, 0.48)
    base_a = (cx+cos(theta-delta)*rx, cy+sin(theta-delta)*ry)
    base_b = (cx+cos(theta+delta)*rx, cy+sin(theta+delta)*ry)
    mx, my = (base_a[0]+base_b[0])/2, (base_a[1]+base_b[1])/2
    angle = atan2(tip[1]-my, tip[0]-mx)
    nx, ny = -sin(angle), cos(angle)
    control_a = (lerp(base_a[0], tip[0], .55)+nx*bend,
                 lerp(base_a[1], tip[1], .55)+ny*bend)
    control_b = (lerp(tip[0], base_b[0], .45)+nx*bend,
                 lerp(tip[1], base_b[1], .45)+ny*bend)
    points = [quad_point(base_a, control_a, tip, i/16) for i in range(17)]
    points += [quad_point(tip, control_b, base_b, i/16) for i in range(1, 17)]
    return points, tip
