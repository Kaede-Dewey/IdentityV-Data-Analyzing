# This is a file utils file.
# usage: from excel path to calcable dictionary file

from pandas import ExcelFile

class fileutils(object):
    """
    Class fileutils
        class to prepare dictionary data for 
        calculation inn mathutils.py
    argument:
        in_dir(str): path to excel files.
    attributes:
        maps(dict): {<map_name>:<Pandas.DataFrame>}
        hunter(dict): {<name>:<Pandas.DataFrame>}
        surviver(dict): {<name>:<Pandas.DataFrame>}
        history(<Pandas.DataFrame>): history data
    """
    
    def __init__(self, in_dir=None):
        maps = ExcelFile(in_dir + '/map.xlsx')
        hunter = ExcelFile(in_dir + '/hunter.xlsx')
        surviver = ExcelFile(in_dir + '/surviver.xlsx')
        history = ExcelFile(in_dir + '/history.xlsx')
        
        # parse excel files.
        self.maps = self._excel_parser(maps)
        self.hunter = self._excel_parser(hunter)
        self.surviver = self._excel_parser(surviver)
        self.history = self._excel_parser(history)
        
    def _excel_parser(self, excel):
        ret = {}
        for sheet in excel.sheet_names:
            ret[sheet] = excel.parse(sheet)
        return ret