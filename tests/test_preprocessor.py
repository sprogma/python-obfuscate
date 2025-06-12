import preprocessor
import pytest

"""
    Not test "" strings, becouse preprocessor sometimes converts them to '' strings.
"""

@pytest.mark.parametrize("code, expected", [
    ("#abc", ""),
    ("x = 5 # abc", "x = 5"),
    ("x = '5 # 5' # abc", "x = '5 # 5'"),
    ('''
class X:
    """
        fun class
    """
    def __init__(): self.x = X()
    ''','''
class X:
    def __init__(): self.x = X()
    ''')
])
def test_Preprocessor_normalize(code, expected):
    a = preprocessor.Preprocessor()
    f = lambda s: s.translate(str.maketrans("",""," \n\t\r"))
    assert f(a.normalize(code)) == f(expected)



