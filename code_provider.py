import common




class CodeProvider:
    """
        this is base class for all code generation classes
    """

    def custom_header(self):
        """
            this method must return array of "expressions"
            (allow true-evaluated), wich will be
            inserted in front of resulting code.
        """
        return []

    def custom_imports(self):
        """
            this method must return array of pairs: lib names,
            wich will be included in front of resulting code,
            before custom headers.

            Repeated imports will be removed

            Name is changed like this:

            for naming agreement i think to use __ONE_[lib/sync/async/cls/var]_[name]

            lib - libraries
            sync - sync function
            async - async function
            cls - classes
            var - variables
            + __ONE_trash for trash

            For example lib "time" will create
            something like __ONE_lib_time := __import__("time")

        """
        return []