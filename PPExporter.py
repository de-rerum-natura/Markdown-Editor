import pypandoc

class PPExporter():
    def __init__(self):
        self.file=""

    def export(self, input_string, output_type, output_file):
        output = pypandoc.convert_text(input_string, output_type, format='md', outputfile=output_file)
        print(output)
