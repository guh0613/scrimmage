import importlib
import unicodedata
from multiprocessing import process
from nonebot import  logger
import pygtrie
import zhconv

from . import _pcr_data

UNKNOWN = 1000

def normalize_str(string) -> str:
    """
    规范化unicode字符串 并 转为小写 并 转为简体
    """
    string = unicodedata.normalize('NFKC', string)
    string = string.lower()
    string = zhconv.convert(string, 'zh-hans')
    return string

class Roster:

    def __init__(self):
        self._roster = pygtrie.CharTrie()
        self.update()

    def update(self):
        importlib.reload(_pcr_data)
        self._roster.clear()
        result = {'success': 0, 'duplicate': 0}
        for idx, names in _pcr_data.CHARA_NAME.items():
            for n in names:
                n = normalize_str(n)
                if n not in self._roster:
                    self._roster[n] = idx
                    result['success'] += 1
                else:
                    result['duplicate'] += 1
                    logger.warning(f'priconne.chara.Roster: 出现重名{n}于id{idx}与id{self._roster[n]}')
        return result

    def get_id(self, name):
        name = normalize_str(name)
        return self._roster[name] if name in self._roster else UNKNOWN

    def guess_id(self, name):
        """@return: id, name, score"""
        name, score = process.extractOne(name, self._roster.keys(), processor=normalize_str)
        return self._roster[name], name, score

    def parse_team(self, namestr):
        """@return: List[ids], unknown_namestr"""
        namestr = normalize_str(namestr.strip())
        team = []
        unknown = []
        while namestr:
            item = self._roster.longest_prefix(namestr)
            if not item:
                unknown.append(namestr[0])
                namestr = namestr[1:].lstrip()
            else:
                team.append(item.value)
                namestr = namestr[len(item.key):].lstrip()
        return team, ''.join(unknown)


roster = Roster()

def name2id(name):
    return roster.get_id(name)
