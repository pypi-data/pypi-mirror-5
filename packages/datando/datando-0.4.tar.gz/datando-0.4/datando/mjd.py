# -*- coding: utf-8 -*-

# Code written by Dr. Diego Gnesi Bartolani, Archaeologist (diego.gnesi@gmail.com).
# http://www.diegognesi.it

import re
from datando.kernel import *

class MJDDateTime(CalendarBase):
    __SECS_PER_DAY = 86400
    __MICROSECS_PER_DAY = 86400000000.0
    __MJD_DIFFERENCE = 58628880000L

    def __init__(self, day = 0, fraction = 0):
        # fraction is a number of
        self.day = day
        self.fraction = fraction

    def __str__(self):
        return "MJD \\ {0}.{1:020}".format(self.day, self.fraction)

    def to_LPDateTime(self):
        secs = self.day * self.__SECS_PER_DAY
        microsecs = int(self.fraction * (self.__MICROSECS_PER_DAY / 1000000000000000000000))
        secs += microsecs / 1000000
        microsecs = microsecs % 1000000
        positive = (self.day >= 0)
        lpd1 = LPDateTime(positive, secs, microsecs)
        return lpd1 + LPDateTime(True, self.__MJD_DIFFERENCE, 0)

    @classmethod
    def from_LPDateTime(cls, lp_datetime):
        lp2 = lp_datetime - LPDateTime(True, cls.__MJD_DIFFERENCE, 0)
        day = lp2.second / cls.__SECS_PER_DAY
        if not lp2.positive:
            day = -day
        float_fraction = (lp2.second % cls.__SECS_PER_DAY) / float(86400.0) + lp2.microsecond / cls.__MICROSECS_PER_DAY
        # fraction is <= 1,000,000,000,000,000,000,000 = 10^21
        fraction = int(float_fraction * 1000000000000000000000)
        return MJDDateTime(day, fraction)

    @classmethod
    def parse(cls, date_string):
        reg_expr = r'^MJD \\ (?P<sign>\+|\-){0,1}(?P<day>\d+).(?P<fraction>\d{1,20})$'
        m = re.match(reg_expr, date_string)
        if m:
            gd = m.groupdict()
            day = int(gd['day'])
            fraction = int(gd['fraction'])
            len_fr = len(gd['fraction'])
            if len_fr < 20:
                fraction = fraction * (10**(20 - len_fr))
            if gd['sign'] == '-':
                day = -day
            return MJDDateTime(day, fraction)
        else:
            return None

    @staticmethod
    def get_prefix():
        return "MJD \\"
