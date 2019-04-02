# This is the math utils module.
# using in heroku, with image utils module.

class Math_utils(object):
    """
    Class Math_utils
        class to calculate player’s values.
    =============
    arguments:
        * senseki: (dictionary) stores values for each game.
        * fu: (<fileutils>) fileutils’ instance.
    attributes:

    """

    def __init__(self, ttl_path=None, htr_path=None, svr_path=None):
        # senseki is the dictionary of the game.

        # get history data
        self.total = pandas.ExcelFile(ttl_path).parse('total')
        self.hunter = pandas.ExcelFile(htr_path).parse('hunter')
        self.surviver = pandas.ExcelFile(svr_path).parse('surviver')
        self.param1 = pandas.ExcelFile(svr_path).parse('param1')
        self.param2 = pandas.ExcelFile(svr_path).parse('param2')
        self.param3 = pandas.ExcelFile(svr_path).parse('param3')
        self.param4 = pandas.ExcelFile(svr_path).parse('param4')
        self.param5 = pandas.ExcelFile(svr_path).parse('param5')

    def _calc_total_rate(self, fact='ifvic', type='shouri', arg=None):
        if arg is None:
            # normal win rate
            return len(self.total[self.total[fact] == type]) \
                / len(self.total['game_id'])
        else:
            ret = {}
            values = self._get_values_from_arg(arg)
            for value in values:
                games = self.total[self.total[arg] == value]
                ret[value] = len(games[games[fact] == type]) / len(games)
            return ret

    def _get_values_from_arg(self, arg):
        data = self.total[arg]
        ret = list(set(data))
        return ret

    def get_win_rate(self, fact='ifvic', type="shouri", *args):

        ret = {}
        if args == ():
            ret[type] = self._calc_total_rate(type)
        else:
            for arg in set(args):
                ret[arg] = self._calc_total_rate(type, arg)
        return ret

    def get_hunter_rate(self):
        """return using rate of hunter."""
        ret = {}
        hunters = self._get_values_from_arg('hunter')
        for hunter in hunters:
            ret[hunter] = self._calc_total_rate('hunter', hunter)
        return ret

    def get_stage_rate(self):
        """return using rate of hunter."""
        ret = {}
        stages = self._get_values_from_arg('stage')
        for stage in stages:
            ret[stage] = self._calc_total_rate('stage', stage)
        return ret

    def get_survs_rate(self):
        """return using rate of hunter."""
        ret = {}
        _survs = self._get_values_from_arg('surviver1')
        print(type(_survs))
        _survs.extend(self._get_values_from_arg('surviver2'))
        _survs.extend(self._get_values_from_arg('surviver3'))
        _survs.extend(self._get_values_from_arg('surviver4'))
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
            ret[surv] = sum([suv1, suv2, suv3, suv4]) / 4
        return ret


if __name__ == '__main__':
    ttl_path = '../data/excel/history/total.xlsx'
    htr_path = '../data/excel/history/hunter.xlsx'
    svr_path = '../data/excel/history/surviver.xlsx'
    m = Math_utils(ttl_path, htr_path, svr_path)
    print(m.get_survs_rate())
