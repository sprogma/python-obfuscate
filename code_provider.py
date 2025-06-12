import common


"""
    "expression" base output must be False-equal.
    becouse we will join expressions using "and"
    operator, (arrays and tuples cause additional
    space consumption and may be them are slower)
"""


class CodeProvider:
    """
        this is base class for all code generation classes
    """

    def custom_header(self):
        """
            this method must return "expression" wich will be
            inserted in front of resulting code.
        """
        return ""

    def custom_imports(self):
        """
            this method must return array of lib names wich
            will be included in front of resulting code and
            custom headers. Repeated imports will be removed
        """
        return [""]