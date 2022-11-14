"""
Tests that the basic yaml bot runs
"""


from examples.yaml_bot import main


class TestMainRuns:
    @staticmethod
    def test_main_method_runs() -> None:
        main()

    @staticmethod
    def test_foo_serialie() -> None:

        local_bot = main()
        local_bot.serialise()
