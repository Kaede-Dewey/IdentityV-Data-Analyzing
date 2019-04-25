# This is the math utils module.
# using in heroku, with image utils module.
import pandas
import numpy as np

class Math_utils(object):
    """
    Class Math_utils
        class to calculate player's values.
    =============
    arguments:
        * senseki: (dictionary) stores values for each game.
        * history: (string) data path for user's game history(csv file)
    attributes:

    """

    def __init__(self, ttl_path=None, htr_path=None, svr_path=None):
        # senseki is the dictionary of the game.

        # get history data
        self.total = pandas.ExcelFile(ttl_path).parse('total').fillna(0)
        self.hunter = pandas.ExcelFile(htr_path).parse('hunter').fillna(0)
        self.surviver = pandas.ExcelFile(svr_path).parse('surviver').fillna(0)
        self.param1 = pandas.ExcelFile(svr_path).parse('param1').fillna(0)
        self.param2 = pandas.ExcelFile(svr_path).parse('param2').fillna(0)
        self.param3 = pandas.ExcelFile(svr_path).parse('param3').fillna(0)
        self.param4 = pandas.ExcelFile(svr_path).parse('param4').fillna(0)
        self.param5 = pandas.ExcelFile(svr_path).parse('param5').fillna(0)

        # holds the total length
        self.total_len = len(self.total['game_id'])

        # set survivers columns
        self.survs_columns = ['surviver1','surviver2','surviver3','surviver4']

    def _calc_total_rate(self, fact='ifvic', type='shouri', arg=None):
        if arg is None:
            # normal win rate
            return len(self.total[self.total[fact] == type]) \
                / len(self.total['game_id'])
        else:
            ret = {}
            values = self.get_values_from_arg(arg)
            for value in values:
                games = self.total[self.total[arg] == value]
                ret[value] = len(games[games[fact] == type]) / len(games)
            return ret

    def get_values_from_arg(self, arg):
        data = self.total[arg]
        ret = list(set(data))
        return ret

    def get_win_rate(self):
        """return using rate of hunter."""
        ret, _ret = {}, {}
        ifvics = self.get_values_from_arg('ifvic')
        for ifvic in ifvics:
            _ret[ifvic] = self._calc_total_rate('ifvic', ifvic)
        if len(_ret) > 4:
            for i, (k, v) in enumerate(
                sorted(_ret.items(), key=lambda x: -x[1])):
                if i < 5:
                    ret[k] = v
                else:
                    if 'others' in ret.keys():
                        ret['others'] += v
                    else:
                        ret['others'] = v
        else:
            ret = _ret
        return ret

    def get_hunter_rate(self):
        """return using rate of hunter."""
        ret, _ret = {}, {}
        hunters = self.get_values_from_arg('hunter')
        for hunter in hunters:
            _ret[hunter] = self._calc_total_rate('hunter', hunter)
        if len(_ret) > 3:
            for i, (k, v) in enumerate(
                sorted(_ret.items(), key=lambda x: -x[1])):
                if i < 4:
                    ret[k] = v
        else:
            ret = _ret
        return ret

    def get_stage_rate(self):
        """return using rate of hunter."""
        ret, _ret = {}, {}
        stages = self.get_values_from_arg('stage')
        for stage in stages:
            _ret[stage] = self._calc_total_rate('stage', stage)
        if len(_ret) > 4:
            for i, (k, v) in enumerate(
                sorted(_ret.items(), key=lambda x: -x[1])):
                if i < 5:
                    ret[k] = v
        else:
            ret = _ret
        return ret

    def get_survs_rate(self):
        """return using rate of hunter."""
        ret, _ret = {}, {}
        _survs = self.get_values_from_arg('surviver1')
        _survs.extend(self.get_values_from_arg('surviver2'))
        _survs.extend(self.get_values_from_arg('surviver3'))
        _survs.extend(self.get_values_from_arg('surviver4'))
        survs = set(_survs)
        for surv in survs:
            suv1 = len(self.surviver[self.surviver['surviver1'] == surv]) \
                / len(self.surviver['game_id'])
            suv2 = len(self.surviver[self.surviver['surviver2'] == surv]) \
                / len(self.surviver['game_id'])
            suv3 = len(self.surviver[self.surviver['surviver3'] == surv]) \
                / len(self.surviver['game_id'])
            suv4 = len(self.surviver[self.surviver['surviver4'] == surv]) \
                / len(self.surviver['game_id'])
            _ret[surv] = sum([suv1, suv2, suv3, suv4]) / 4
        if len(_ret) > 6:
            for i, (k, v) in enumerate(
                sorted(_ret.items(), key=lambda x: -x[1])):
                if i < 7:
                    ret[k] = v
        else:
            ret = _ret
        return ret

    def get_ave_ctime(self, window_size=1):
        """return average chase time"""
        ret = []
        window = len(self.param5['surviver1']) - window_size
        sur1 = \
            self.param5['surviver1'][window:]
        sur2 = \
            self.param5['surviver2'][window:]
        sur3 = \
            self.param5['surviver3'][window:]
        sur4 = \
            self.param5['surviver4'][window:]
        for (a,b,c,d) in zip(sur1, sur2, sur3, sur4):
            ret.append(
                sum([int(a), int(b), int(c), int(d)]) / 4
            )
        return np.array(ret)

    def get_ave_decode(self, window_size=1):
        """return average decoding progress"""
        ret = []
        window = len(self.param1['surviver1']) - window_size
        sur1 = \
            self.param1['surviver1'][window:]
        sur2 = \
            self.param1['surviver2'][window:]
        sur3 = \
            self.param1['surviver3'][window:]
        sur4 = \
            self.param1['surviver4'][window:]
        for (a,b,c,d) in zip(sur1, sur2, sur3, sur4):
            ret.append(
                sum([a, b, c, d]) / 4
            )
        return np.array(ret)

    def get_extra_decode(self, window_size=1):
        """ return extra decoding progress"""
        # get number of decoded machine.
        ret = []
        window = len(self.hunter['param1']) - window_size
        decoded = self.hunter['param1'][window:]
        sur1 = self.param1['surviver1'][window:]
        sur2 = self.param1['surviver2'][window:]
        sur3 = self.param1['surviver3'][window:]
        sur4 = self.param1['surviver4'][window:]
        for (a,b,c,d, dcd) in zip(sur1, sur2, sur3, sur4, decoded):
            ret.append(
                (sum([a,b,c,d]) - (5 - dcd) * 100)
            )
        return np.array(ret)

    def get_ita_break(self, window_size=5):
        """return the list of numbers for ita breaking."""
        window = len(self.hunter['param2']) - window_size
        return np.array(self.hunter['param2'][window:])

    def get_terror_attack(self, window_size=5):
        """return the list of numbers for terror attack."""
        window = len(self.hunter['param4']) - window_size
        return np.array(self.hunter['param4'][window:])

    def get_usual_attack(self, window_size=5):
        """return the list of numbers for usual attack."""
        window = len(self.hunter['param3']) - window_size
        return np.array(self.hunter['param3'][window:])

    def get_ita_morau(self, window_size=5):
        """return the list of numbers for ita morau number."""
        window = len(self.hunter['param2']) - window_size
        ret = []
        sur1 = \
            self.param2['surviver1'][window:]
        sur2 = \
            self.param2['surviver2'][window:]
        sur3 = \
            self.param2['surviver3'][window:]
        sur4 = \
            self.param2['surviver4'][window:]
        for (a,b,c,d) in zip(sur1, sur2, sur3, sur4):
            ret.append(
                sum([a, b, c, d])
            )
        return np.array(ret)

    def get_osanpo_time(self, window_size=5):
        """ return length of osanpo time."""
        # get number of decoded machine.
        ret = []
        window = len(self.hunter['param1']) - window_size
        game_time = self.total['time'][window:]
        sur1 = self.param5['surviver1'][window:]
        sur2 = self.param5['surviver2'][window:]
        sur3 = self.param5['surviver3'][window:]
        sur4 = self.param5['surviver4'][window:]
        for (a,b,c,d,time) in zip(sur1, sur2, sur3, sur4, game_time):
            (minute, second) = time.split(':')
            g_time = int(minute) * 60 + int(second)
            ret_time = g_time - sum([a, b, c, d])
            if ret_time < 0:
                ret.append(0)
            else:
                ret.append(ret_time)
        return np.array(ret)

    def get_survs_with_param(self, parametor, factor, window_size=10):
        """get paramators related to surviver. """

        # survs is the set of survivers.
        _survs = self.get_values_from_arg('surviver1')
        _survs.extend(self.get_values_from_arg('surviver2'))
        _survs.extend(self.get_values_from_arg('surviver3'))
        _survs.extend(self.get_values_from_arg('surviver4'))
        survs = set(_survs)

        # set param
        if parametor == 'param1':
            param = self.param1
        elif parametor == 'param2':
            param = self.param2
        elif parametor == 'param3':
            param = self.param3
        elif parametor == 'param4':
            param = self.param4
        elif parametor == 'param5':
            param = self.param5

        # get values of the set of factors.
        factor_values = self.get_values_from_arg(factor)

        # initialize the return dictionary.
        dic = {k:{ks:[] for ks in survs} for k in factor_values}

        for line in range(self.total_len):
            fact = self.total[factor][line]
            survs = [
                self.surviver['surviver1'][line],
                self.surviver['surviver2'][line],
                self.surviver['surviver3'][line],
                self.surviver['surviver4'][line]
            ]
            for i, surv in enumerate(survs):
                value = param[self.survs_columns[i]][line]
                dic[fact][surv].append(value)
        return dic













if __name__ == '__main__':
    ttl_path = '../data/excel/history/total.xlsx'
    htr_path = '../data/excel/history/hunter.xlsx'
    svr_path = '../data/excel/history/surviver.xlsx'
    m = Math_utils(ttl_path, htr_path, svr_path)
    print(m.get_survs_rate())
