import unittest
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class NBBlackTest(unittest.TestCase):
    """Run our example notebook and check that the cells are
    formatted as expected.  Requires jupyter notebook to be
    running already."""

    def setUp(self):
        # Get the access token
        completed_process = subprocess.run(
            "jupyter notebook list".split(), capture_output=True
        )
        output_lines = completed_process.stdout.decode("utf-8").split("\n")

        # There should be one intro line, one server line and an empty line
        if len(output_lines) != 3:
            raise RuntimeError("Too many or too few running notebook servers.")

        server = output_lines[1]
        token_starts = server.find("?token=")
        token_ends = server.find(" ")
        self.token = server[token_starts:token_ends]

        # Start the web browser
        options = webdriver.firefox.options.Options()
        # options.headless = True
        self.driver = webdriver.Firefox(options=options)

    def tearDown(self):
        self.driver.quit()

    def test_example_notebook(self):
        # ToDo Get this token somehow (run jupyter as a sub-process?)
        self.driver.get(
            "http://127.0.0.1:8888/notebooks/test/example.ipynb" + self.token
        )

        # ToDo wait for page to be loaded
        time.sleep(1)

        # Restart kernel and run workbook (relies on Ctrl-Shift-a shortcut)
        body = self.driver.find_element_by_tag_name("body")
        body.send_keys(Keys.ESCAPE)
        body.send_keys(Keys.LEFT_CONTROL, Keys.LEFT_SHIFT, "a")

        # ToDo wait for last cell to be run
        time.sleep(1)

        code_cells = self.driver.find_elements_by_class_name("code_cell")
        text_cells = self.driver.find_elements_by_class_name("text_cell")
        text_cells = text_cells[1:]  # ignore the first cell, which is a markdown intro
        assert len(code_cells) > 1
        assert len(code_cells) == len(text_cells)

        # The example notebook has alternating code and text cells
        for i in range(len(code_cells)):
            code = code_cells[i].text

            # We don't want the "In[1]:\n"
            code_starts = code.find("\n") + 1
            code = code[code_starts:]

            # We don't want our JavaScript object at the end
            javascript = code.find("\n<IPython.core.display.Javascript object>")
            if javascript > -1:
                code = code[:javascript]

            text = text_cells[i].text

            self.assertEqual(text, code)


if __name__ == "__main__":
    unittest.main()
