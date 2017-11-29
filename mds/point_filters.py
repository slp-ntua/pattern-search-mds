import numpy as np

import common


class PointFilter(object):
    def __init__(self,
                 min_points_per_turn=0.2,
                 max_points_per_turn=1.0,
                 recalculate_each=10):
        self.min_points_per_turn = min_points_per_turn
        self.max_points_per_turn = max_points_per_turn
        self.recalculate_each = recalculate_each

    def keep(self, points, turn):
        percent_diff = self.max_points_per_turn - self.min_points_per_turn
        line = self.max_points_per_turn - percent_diff * turn / 100.0
        points_percent = max(line, self.min_points_per_turn)
        return int(points.shape[0] * points_percent)

    def _filt(self, points, turn=None, d_goal=None, d_current=None):
        # unused arguments
        del turn, d_goal, d_current
        return points

    def filter(self, points, turn=None, d_goal=None, d_current=None):
        if turn % self.recalculate_each == 0:
            return points
        return self._filt(points,
                          turn=turn,
                          d_goal=d_goal,
                          d_current=d_current)


class IncludeAllPointsFilter(PointFilter):
    pass


class StochasticFilter(PointFilter):
    def _filt(self, points, turn=None, d_goal=None, d_current=None):
        keep = self.keep(points, turn)
        return np.random.choice(points, size=keep, replace=False)


class GSDFilter(PointFilter):
    def filter(self, points, turn=None, d_goal=None, d_current=None):
        if d_current is None or d_goal is None:
            raise ValueError("D_goal and D_current should be provided")
        keep = self.keep(points, turn)
        errors = common.compute_mds_error(d_goal, d_current, axis=1)
        return np.argpartition(-1.0 * errors, keep - 1)[:keep]