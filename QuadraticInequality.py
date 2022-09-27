import math
import re
from Segment import Segment, SegmentSet, NEG_INFINITY, POS_INFINITY

class Polynom:

    def __init__(self, pol):
        if isinstance(pol, list):
            self.__polynom = {pow1: coef for pow1, coef in enumerate(pol[::-1])}
        if isinstance(pol, Polynom):
            self.__polynom = pol.__polynom
        if isinstance(pol, dict):
            self.__polynom = pol.copy()
        if isinstance(pol, str):
            self.__polynom = Polynom.pol_to_dict(pol)

    def __str__(self):
        str_pol = ''
        for i in sorted(self.__polynom.keys())[::-1]:
            coef = self.__polynom[i]
            if coef != 0 and i != 0 and i != 1:
                if i==max(self.__polynom.keys()):
                    str_pol += f'{"" if coef==1 else "-" if coef==-1 else coef}x^{i}'
                elif coef>0:
                    str_pol += f'{"+"+str(coef) if (coef!=1) else "+"}x^{i}'
                elif coef<0:
                    str_pol += f'{"-" if (coef==-1) else coef}x^{i}'
            elif coef == 0:
                continue
            elif i == 0:
                str_pol += f"{'+'+str(coef) if coef>0 else coef}"
            elif i==1:
                str_pol += f'{"+"+str(coef) if coef>0 else coef}x'
        str_pol = str_pol.replace('+-','+')
        return str_pol
    def __repr__(self):
        return self.__str__()
    def get_polynom(self):
        return self.__polynom.copy()

    @staticmethod
    def pol_to_dict(pol):
        pol='+'+pol
        pol = pol.replace(' ','')
        pattern = '(?P<coef>[-+][.\d]*(?=[x]))((x\^)|x)(?P<pow>\d*)'
        dict_pol = {1 if i['pow'] == '' else int(i['pow']): -1.0 if i['coef'] == '-' else 1.0 if i['coef'] == '+' else float(i['coef']) for i in re.finditer(pattern, pol)}
        free_coef = re.search('(?<!\^)[-+][.\d]+(?![x])', pol)
        dict_pol[0] = 0 if not free_coef else float(free_coef.group(0))
        for i in range(max(dict_pol.keys())):
            if dict_pol.get(i) is None:
                dict_pol[i] = 0
        return dict_pol

class QuadraticInequality(Polynom):
    def __init__(self, ineq:str):
        self.sign = ''
        if '=' in ineq:
            self.sign+='='
        if '>' in ineq:
            self.sign+='>'
        elif '<' in ineq:
            self.sign+='<'

        super().__init__(ineq)
        if max(self.get_polynom().keys()) != 2:
            raise Exception('Its not quadratic equation')

    def solve(self):
        #    print(polynom)
        dict_pol = self.get_polynom()
        a, b, c = dict_pol[2], dict_pol[1], dict_pol[0]
        D = b * b - 4 * a * c
        sign = self.sign
        try:
            assert D >= 0, 'D<0'
            x1 = (-b - math.sqrt(D)) / (2 * a)
            x2 = (-b + math.sqrt(D)) / (2 * a)
            if '=' in sign:
                border = True # square skobki
            else: border = False
            if '>' in sign:
                if a>0:
                    return SegmentSet([Segment(NEG_INFINITY, x1, False, border), Segment(x2, POS_INFINITY, border, False)])
                else:

                    return SegmentSet([Segment(x2, x1, border, border)])
            elif '<' in sign:
                if a>0:
                    return SegmentSet([Segment(x1, x2, border, border)])
                else:
                    return SegmentSet([Segment(NEG_INFINITY, x2, False, border), Segment(x1, POS_INFINITY, border, False)])

        except (AssertionError, ZeroDivisionError):
            if (a>0 and '>' in sign) or (a<0 and '<' in sign):
                return SegmentSet([Segment(NEG_INFINITY, POS_INFINITY, False, False)])
            else:
                return SegmentSet([Segment(0,0, False, False)])

class Iterator:
    def __init__(self, segset: SegmentSet):
        self.sets = segset._segments
        self.__index = -1
    def __iter__(self):
        return self
    def __next__(self):
        if self.__index>=len(self.sets)-1:
            raise StopIteration
        else:
            self.__index+=1
            return self.sets[self.__index]

if __name__ == '__main__':
    n = int(input('Input count of quadratic inequalities>> '))
    ineqs = []#['x^2+2x+3>0', 'x^2- 1<0', 'x^2+5x+4>0']
    for i in range(n):
        ineq = QuadraticInequality(input('Input inequality at format ax^2+bx+c...0>> '))
        print('Solution: ', ineq.solve())
        ineqs.append(ineq)
    Solution = ineqs[0].solve()
    for i in ineqs[::]:
        try:
            Solution = Solution*i.solve()
        except:
            continue
    print('Solution of system inequality:', Solution)
    print('WITH ITERATOR')
    for set in Iterator(Solution):
        print(set)