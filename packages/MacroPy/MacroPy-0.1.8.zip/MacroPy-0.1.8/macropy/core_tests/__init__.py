
import unittest
import sys
import macropy.core.macros

class Tests(unittest.TestCase):
    def test_basic_identification_and_expansion(self):
        import basic_expr
        assert basic_expr.run() == 10

        import basic_block
        assert basic_block.run() == 13

        import basic_decorator
        assert basic_decorator.run() == 14

    def test_arguments(self):
        import argument
        argument.run() == 31

    def test_gen_sym(self):
        import gen_sym
        gen_sym.run() == 10

    def test_ignore_macros_not_explicitly_imported(self):
        import not_imported
        assert not_imported.run() == 10

    def test_line_numbers_should_match_source(self):
        import line_number_source
        assert line_number_source.run(0, False) == 10
        try:
            line_number_source.run(0, True)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            assert exc_traceback.tb_next.tb_lineno == 8

    def test_expanded_line_numbers_should_match_source(self):
        import line_number_error_source
        assert line_number_error_source.run(11) == 1


        # this still doesn't give the correct line numbers
        # in the stack trace

        # line_number_error_source.run(10)


    def test_quasiquote_expansion_line_numbers(self):
        import quote_source
        assert quote_source.run(8) == 1
        try:
            quote_source.run(4)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            assert exc_traceback.tb_next.tb_lineno == 6, exc_traceback.tb_next.tb_lineno

        try:
            quote_source.run(2)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            assert exc_traceback.tb_next.tb_lineno == 6