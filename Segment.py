from functools import total_ordering
from copy import deepcopy

NEG_INFINITY = '-∞'
POS_INFINITY = '+∞'
INFINITY = '∞'
EMPTY_SET = '∅'
class SegmentError(BaseException):
    def __init__(self, text):
        self.txt = text

@total_ordering
class Segment:
    def __init__(self, a, b, left_in=True, right_in=True):
        self._a = a
        self._b = b

        if INFINITY in str(self._a):
            self._left_in = False
            self._right_in = right_in
        elif INFINITY in str(self._b):
            self._left_in = left_in
            self._right_in = False
        else:
            self._left_in = left_in
            self._right_in = right_in
        if self._a == POS_INFINITY or self._b == NEG_INFINITY:
            raise SegmentError(f'Left board {a} more than right board {b}')
        elif self._a == NEG_INFINITY or self._b == POS_INFINITY:
            pass
        elif self._a>self._b:
            raise SegmentError(f'Left board {a} more than right board {b}')
    def is_empty(self):
        if str(self._a) == POS_INFINITY or str(self._b) == NEG_INFINITY:
            return True
        if str(self._a) == NEG_INFINITY:
            return False
        if str(self._b) == POS_INFINITY:
            return False
        else:
            return (self._a > self._b) or (self._a==self._b and not any([self._left_in, self._right_in]))

    def __mul__(self, other):
        if self.is_empty() or other.is_empty():
            return Segment(0,0, False, False)
        self_a, self_b, other_a, other_b = self.__interval_to_nums(other)
        a1, left_in = (self._a, self._left_in) if self_a>other_a else (other._a, other._left_in) if self_a<other_a else (self._a, all([self._left_in,other._left_in]))
        b1, right_in = (self._b, self._right_in) if self_b<other_b else (other._b ,other._right_in) if self_b>other_b else (self._b, all([self._right_in,other._right_in]))
        try:
            return Segment(a1,b1,left_in,right_in)
        except SegmentError:
            return Segment(0,0, False, False)
    def __interval_to_nums(self, other):
        self_a = self._a
        self_b = self._b
        other_a = other._a
        other_b = other._b
        if isinstance(self._a, str):
            if isinstance(other._a, str):
               self_a = 0
               other_a = 0
            else:
                self_a = other._a-1
        else:
            if isinstance(other._a, str):
                other_a = self_a-1

        if isinstance(self._b, str):
            if isinstance(other._b, str):
                self_b = -100
                other_b = 100
            else:
                self_b = other._b + 1
        else:
            if isinstance(other._b, str):
                other_b = self_b + 1

        return self_a, self_b, other_a, other_b
    def this_set_at_set(self, other):
        if self.is_empty() or other.is_empty():
            return False
        self_a, self_b, other_a, other_b = self.__interval_to_nums(other)
        if other_a <= self_a and other_b >= self_b:
            if self_a == other_a:
                if self._left_in>other._left_in:
                    return False
            if self_b == other_b:
                if self._right_in>other._right_in:
                    return False
            return True
        return False

    @staticmethod
    def combine(self, other):
        crossing = self*other
        self_a, self_b, other_a, other_b = self.__interval_to_nums(other)
        if crossing.is_empty():
            return None
        elif self.this_set_at_set(other):
            return deepcopy(other)
        elif other.this_set_at_set(self):
            return deepcopy(self)
        else:
            if self_a<other_a:
                if (self_b==other_a and any([self._right_in, other._left_in])) or self_b > other_a:
                    return Segment(self._a, other._b, self._left_in, other._right_in)
            elif self_a==other_a:
                return Segment(self._a, other._b, any([self._left_in, other._left_in]), any([self._right_in, other._right_in]))
            else:
                return Segment.combine(other, self)

    def __str__(self):
        if self.is_empty():
            return EMPTY_SET
        return ('[' if self._left_in else '(') + str(self._a) +  ' ; ' + str(self._b) + (']' if self._right_in else ')')
    def __repr__(self):
        return self.__str__()

    def __lt__(self, other):
        if str(self._a) == NEG_INFINITY:
            return True
        elif str(other._a) == NEG_INFINITY:
            return False
        return self._a<other._a
    def __eq__(self, other):
        return self._a == other._a and self._b == other._b and self._left_in==other._left_in and self._right_in==other._right_in
class SegmentSet:
    def __init__(self, segments:list):
        if segments:
            self._segments = SegmentSet.simplify(segments)
        # else:
        #     self._segments = ['∅']

    @staticmethod
    def simplify(segments1):
        segments = sorted(segments1.copy())
        k = 0
        while True:
            try:
                if segments[k].is_empty():
                    del segments[k]
                    if len(segments) == 0:
                        return [Segment(0,0,False,False)]
                if not ((comb:=Segment.combine(segments[k], segments[k+1])) is None):

                    del segments[k]
                    del segments[k]
                    segments.insert(k, comb)

                else:
                    k+=1

            except IndexError:
                break
        return segments

    def __str__(self):
        return '∪'.join(map(str,self._segments))
    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        if isinstance(other, SegmentSet):
            return SegmentSet(self._segments+other._segments)
        if isinstance(other, Segment):
            return SegmentSet(self._segments+[other])
    def __mul__(self, other):
        SegmentSets = []
        segments = []
        self_segments = [i for i in self._segments]
        other_segments = [i for i in other._segments]
        for segments_self in self_segments:
            for segments_other in other_segments:
                cross = segments_self*segments_other
                if not cross is None:
                    segments.append(segments_self*segments_other)
            SegmentSets.append(SegmentSet(segments))
            segments = []
        Sets = SegmentSets[0]
        for i in SegmentSets[1::]:
            Sets = Sets + i
        return Sets

