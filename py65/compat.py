import sys

PY2 = sys.version_info[0] == 2

if PY2:
    unicode = unicode

    def as_string(s, encoding='utf-8'):
        if isinstance(s, unicode):
            return s
        else:
            return s.decode(encoding)

else:
    unicode = str

    def as_string(s, encoding='utf-8'):
        if isinstance(s, str):
            return s
        else:
            return s.decode(encoding)
