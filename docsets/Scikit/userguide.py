from doc2dash.parsers.intersphinx import (InterSphinxParser,
                                          inv_entry_to_path,
                                          ParserEntry)


class ScikitLearnDocs(InterSphinxParser):
    def convert_type(self, inv_type):
        if inv_type == 'std:doc':  # sphinx type
            return 'Guide'  # Dash type
        if inv_type.endswith(':attribute'):
            # Hide attributes in scikit-learn, at least for now
            return
        return super(ScikitLearnDocs, self).convert_type(inv_type)

    def create_entry(self, dash_type, key, inv_entry):
        if dash_type == 'Guide':
            path_str = inv_entry_to_path(inv_entry)
            name = inv_entry[3]
            if name == '<no title>':
                return
            if inv_entry[2].startswith('modules/generated/'):
                return
            if inv_entry[2].startswith('auto_examples/'):
                name = 'Example: ' + name
            if inv_entry[2].startswith('tutorial/'):
                name = 'Tutorial: ' + name
            return ParserEntry(name=name, type=dash_type,
                               path=path_str)
        return super(ScikitLearnDocs,
                     self).create_entry(dash_type, key, inv_entry)
