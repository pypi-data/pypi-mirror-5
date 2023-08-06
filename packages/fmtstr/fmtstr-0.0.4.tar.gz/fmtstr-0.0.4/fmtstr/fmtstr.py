r"""Colored strings that behave mostly like strings

>>> s = fmtstr("Hey there!", 'red')
>>> s
red("Hey there!")
>>> s[4:7]
red("the")
>>> red_on_blue = fmtstr('hello', 'red', 'on_blue')
>>> blue_on_red = fmtstr('there', fg='blue', bg='red')
>>> green = fmtstr('!', 'green')
>>> full = red_on_blue + ' ' + blue_on_red + green
>>> full
on_blue(red("hello"))+" "+on_red(blue("there"))+green("!")
>>> str(full)
'\x1b[31m\x1b[44mhello\x1b[49m\x1b[39m \x1b[34m\x1b[41mthere\x1b[49m\x1b[39m\x1b[32m!\x1b[39m'
>>> fmtstr(', ').join(['a', fmtstr('b'), fmtstr('c', 'blue')])
"a"+", "+"b"+", "+blue("c")
"""
#TODO add a way to composite text without losing original formatting information

from escseqparse import parse
from termformatconstants import FG_COLORS, BG_COLORS, STYLES
from termformatconstants import FG_NUMBER_TO_COLOR, BG_NUMBER_TO_COLOR
from termformatconstants import RESET_ALL, RESET_BG, RESET_FG
from termformatconstants import seq

xforms = {
    'fg' : lambda x, v: seq(v)+x+seq(RESET_FG),
    'bg' : lambda x, v: seq(v)+x+seq(RESET_BG),
    'bold' : lambda x: seq(STYLES['bold'])+x+seq(RESET_ALL),
    'underline' : lambda x: seq(STYLES['underline'])+x+seq(RESET_ALL),
    'blink' : lambda x: seq(STYLES['blink'])+x+seq(RESET_ALL),
    'invert' : lambda x: seq(STYLES['invert'])+x+seq(RESET_ALL),
}

class BaseFmtStr(object):
    """Formatting annotations on a string"""
    def __init__(self, string, atts=None):
        self._s = string
        self.atts = {k:v for k,v in atts.items()} if atts else {}

    s = property(lambda self: self._s) #making self.s immutable

    def __len__(self):
        return len(self.s)

    def __str__(self):
        s = self.s
        for k, v in self.atts.items():
            if k not in xforms: continue
            if v is True:
                s = xforms[k](s)
            elif v is False:
                continue
            else:
                s = xforms[k](s, v)
        return s

    def __getitem__(self, index):
        return fmtstr(str(self)[index])

    def __repr__(self):
        def pp_att(att):
            if att == 'fg': return FG_NUMBER_TO_COLOR[self.atts[att]]
            elif att == 'bg': return 'on_' + BG_NUMBER_TO_COLOR[self.atts[att]]
            else: return att
        return (''.join(
                        pp_att(att)+'('
                        for att in sorted(self.atts)) +
               ('"%s"' % self.s) + ')'*len(self.atts))

class FmtStr(object):
    def __init__(self, *components):
        assert all(isinstance(x, BaseFmtStr) for x in components)
        self.basefmtstrs = [x for x in components if len(x) > 0]

    @classmethod
    def from_str(cls, s):
        r"""
        >>> fmtstr("|"+fmtstr("hey", fg='red', bg='blue')+"|")
        "|"+on_blue(red("hey"))+"|"
        >>> fmtstr('|\x1b[31m\x1b[44mhey\x1b[49m\x1b[39m|')
        "|"+on_blue(red("hey"))+"|"
        """
        tokens_and_strings = parse(s)
        bases = []
        cur_fmt = {}
        for x in tokens_and_strings:
            if isinstance(x, dict):
                cur_fmt.update(x)
            elif isinstance(x, basestring):
                atts = parse_args('', {k:v for k,v in cur_fmt.items() if v is not None})
                bases.append(BaseFmtStr(x, atts=atts))
            else:
                raise Exception("logic error")
        return FmtStr(*bases)

    def set_attributes(self, **attributes):
        for k, v in attributes.items():
            for fs in self.basefmtstrs:
                fs.atts[k] = v

    def join(self, iterable):
        iterable = list(iterable)
        basefmtstrs = []
        for i, s in enumerate(iterable):
            if isinstance(s, FmtStr):
                basefmtstrs.extend(s.basefmtstrs)
            elif isinstance(s, basestring):
                basefmtstrs.extend(fmtstr(s).basefmtstrs) #TODO just make a basefmtstr directly
            else:
                raise TypeError("expected basestring or FmtStr, %r found" % type(s))
            if i < len(iterable) - 1:
                basefmtstrs.extend(self.basefmtstrs)
        return FmtStr(*basefmtstrs)

    def __str__(self):
        return ''.join(str(fs) for fs in self.basefmtstrs)

    def __len__(self):
        return sum(len(fs) for fs in self.basefmtstrs)

    def __repr__(self):
        return '+'.join(repr(fs) for fs in self.basefmtstrs)

    def __eq__(self, other):
        return str(self) == str(other)

    def __add__(self, other):
        if isinstance(other, FmtStr):
            return FmtStr(*(self.basefmtstrs + other.basefmtstrs))
        elif isinstance(other, basestring):
            return FmtStr(*(self.basefmtstrs + [BaseFmtStr(other)]))
        else:
            raise TypeError('Can\'t add %r and %r' % (self, other))

    def __radd__(self, other):
        if isinstance(other, FmtStr):
            return FmtStr(*(x for x in (other.basefmtstrs + self.basefmtstrs)))
        elif isinstance(other, basestring):
            return FmtStr(*(x for x in ([BaseFmtStr(other)] + self.basefmtstrs)))
        else:
            raise TypeError('Can\'t add those')

    @property
    def shared_atts(self):
        """Gets atts shared among all nonzero length component BaseFmtStrs"""
        #TODO cache this, could get ugly for large FmtStrs
        atts = {}
        first = self.basefmtstrs[0]
        for att in first.atts:
            #TODO how to write this without the '???'?
            if all(fs.atts.get(att, '???') == first.atts[att] for fs in self.basefmtstrs if len(fs) > 0):
                atts[att] = first.atts[att]
        return atts

    def __getattr__(self, att):
        # thanks to @aerenchyma/@jczetta
        def func_help(*args, **kwargs):
             result = getattr(self.s, att)(*args, **kwargs)
             if isinstance(result, basestring):
                 return fmtstr(result, **self.shared_atts)
             elif isinstance(result, list):
                 return [fmtstr(x, **self.shared_atts) for x in result]
             else:
                 return result
        return func_help

    @property
    def s(self):
        return "".join(fs.s for fs in self.basefmtstrs)

    def __getitem__(self, index):
        index = normalize_slice(len(self), index)
        counter = 0
        output = ''
        for fs in self.basefmtstrs:
            if index.start < counter + len(fs) and index.stop > counter:
                s_part = fs.s[max(0, index.start - counter):index.stop - counter]
                piece = str(BaseFmtStr(s_part, fs.atts))
                output += piece
            counter += len(fs)
            if index.stop < counter:
                break
        return fmtstr(output)

    def __setitem__(self, index, value):
        index = normalize_slice(len(self), index)
        if isinstance(value, basestring):
            value = FmtStr(BaseFmtStr(value))
        elif not isinstance(value, FmtStr):
            raise ValueError('Should be str or FmtStr')
        counter = 0
        old_basefmtstrs = self.basefmtstrs[:]
        self.basefmtstrs = []
        inserted = False
        for fs in old_basefmtstrs:
            if index.start < counter + len(fs) and index.stop > counter:
                start = max(0, index.start - counter)
                end = index.stop - counter
                front = BaseFmtStr(fs.s[:start], fs.atts)
                # stuff
                new = value
                back = BaseFmtStr(fs.s[end:], fs.atts)
                if len(front) > 0:
                    self.basefmtstrs.append(front)
                if len(new) > 0 and not inserted:
                    self.basefmtstrs.extend(new.basefmtstrs)
                    inserted = True
                if len(back) > 0:
                    self.basefmtstrs.append(back)
            else:
                self.basefmtstrs.append(fs)
            counter += len(fs)

def normalize_slice(length, index):
    is_int = False
    if isinstance(index, int):
        is_int = True
        index = slice(index, index+1)
    if index.start is None:
        index = slice(0, index.stop, index.step)
    if index.stop is None:
        index = slice(index.start, length, index.step)
    if index.start < -1:
        index = slice(length - index.start, index.stop, index.step)
    if index.stop < -1:
        index = slice(index.start, length - index.stop, index.step)
    if index.step is not None:
        raise NotImplementedError("You can't use steps with slicing yet")
    if is_int:
        if index.start < 0 or index.start > length:
            raise IndexError("index out of bounds")
    return index

def parse_args(args, kwargs):
    if 'style' in kwargs:
        args += (kwargs['style'],)
        del kwargs['style']
    for arg in args:
        if not isinstance(arg, basestring):
            raise ValueError("args must be strings:" + repr(args))
        if arg.lower() in FG_COLORS:
            if 'fg' in kwargs: raise ValueError("fg specified twice")
            kwargs['fg'] = FG_COLORS[arg]
        elif arg.lower().startswith('on_') and arg[3:].lower() in BG_COLORS:
            if 'bg' in kwargs: raise ValueError("fg specified twice")
            kwargs['bg'] = BG_COLORS[arg[3:]]
        elif arg.lower() in STYLES:
            kwargs[arg] = True
        else:
            raise ValueError("couldn't process arg: "+repr(arg))
    for k in kwargs:
        if k not in ['fg', 'bg'] + STYLES.keys():
            raise ValueError("Can't apply that transformation")
    if 'fg' in kwargs:
        if kwargs['fg'] in FG_COLORS:
            kwargs['fg'] = FG_COLORS[kwargs['fg']]
        if kwargs['fg'] not in FG_COLORS.values():
            raise ValueError("Bad fg value: %s", kwargs['fg'])
    if 'bg' in kwargs:
        if kwargs['bg'] in BG_COLORS:
            kwargs['bg'] = BG_COLORS[kwargs['bg']]
        if kwargs['bg'] not in BG_COLORS.values():
            raise ValueError("Bad bg value: %s", kwargs['bg'])
    return kwargs

def fmtstr(string, *args, **kwargs):
    """
    Convenience function for creating a FmtStr

    >>> fmtstr('asdf', 'blue', 'on_red')
    on_red(blue("asdf"))
    """
    atts = parse_args(args, kwargs)
    if isinstance(string, FmtStr):
        string.set_attributes(**atts)
        return string
    elif isinstance(string, basestring):
        string = FmtStr.from_str(string)
        string.set_attributes(**atts)
        return string
    else:
        raise ValueError("Bad Args: %r %r %r" % (string, args, kwargs))

if __name__ == '__main__':
    #import doctest
    #doctest.testmod()
    f = FmtStr.from_str(str(fmtstr('tom', 'blue')))
    print(repr(f))
    f = fmtstr('stuff', fg='blue', bold=True)
    print(repr(f))

