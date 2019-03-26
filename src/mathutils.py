# This is the math utils module.
# using in heroku, with image utils module.
import pandas

class Math_utils(object):
    """
    Class Math_utils
        class to calculate player’s values.
    =============
    arguments:
        * senseki: (dictionary) stores values for each game.
        * history: (string) data path for user's game history(csv file)
    attributes:
        
    """
    
    def __init__(self, senseki=None, history=None):
        # senseki is the dictionary of the game.
        
        # get history data
        self.history = pandas.read_csv(history)
        
        # add game data to the history.
        self._update_history(senseki)
        
        
    def  _update_history(self, senseki):
        # add new game.
        self.history.append(
            senseki,
            ignore_index=True
            )
    
    
    def get_win_rate(self, type='win', *args):
        """
        calculate win_rate or lose, draw rate for each kwargs.
        ex)
        * args == (),return usual win_rate
        * args != (), return win_rate for each factor. as dict.
        argument:
            type: string. 'win', 'lose', or 'draw'.
                when another keyword would be given, 
                this method would calculate win_rate.
            *args: string. can set 'stage', 'hunter',
                '<surviver_name>', or some factor you added
                as custom factor.
        """
        # if type is not 'lose' or 'draw',
        # type would change into 'win'.
        if not type in ('lose', 'draw'):
            type = 'win'
        
        # initialize return dictionary
        # key: given keywords
        # value: win or lose or draw rate.
        ret = {}
        
        # build return dictionary
        # if args is (), return normal rate.
        if args == ():
            # ret['normal'] == scalar number.
            ret['normal'] = self._calc_rate(type)
        
        else:
            # if args is not (), return for each keywords
            for arg in set(args):
                # ret[arg] == dictionary.
                ret[arg] = self._calc_rate(type, arg)
        
        # return
        return ret
    
    
    def _calc_rate(self, type=None, arg=None):
        # type should be in ('win', 'lose', 'draw')
        # calc data from history data.
        if arg is None:
            # normal win rate
            return len(self.history['id']) / sum(self.history[type])
            
        else:
            # initialize return dictionary
            ret = {}
            
            # when arg is given,
            # 1. get all values for the arg.
            values = self._get_values_from_arg(arg)
            
            # 2. calc win-rate for all values.
            for value in values:
                # get information of games.
                # Because self.history[type] is always one-hot vector,
                # we can calculate win-rate by len(games) / sum(games)
                games = [t for i, t in enumerate(self.history[type]) \
                                if value in self.history[arg][i]]
                ret[value] = len(games) / sum(games)
            
            # return
            return ret
    
    def _get_values_from_arg(self, arg):
        # get values from arg.
        data = self.history[arg]
        
        # when arg is 'surviver', data is 2d-array,
        # which must be flattened.
        if len(data[0]) > 2:
            for ret in data:
                ret.extend(ret)
            ret = set(ret)
        else:
            ret = set(data)
        
        # return
        return ret