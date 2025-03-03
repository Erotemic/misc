#!/usr/bin/env python3
"""
Requirements:
    libcst
"""
import scriptconfig as scfg
import ubelt as ub
import libcst as cst
# from libcst import matchers as m
from libcst.metadata import PositionProvider
# import os


class FunctionDecoratorTransformer(cst.CSTTransformer):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, decorator_name, import_statement):
        super().__init__()
        self.decorator_name = decorator_name
        self.import_statement = import_statement
        self.has_import = False  # Track if the import statement has been added

    def leave_Module(self, original_node, updated_node):
        # Add the import statement below any module-level docstring, comments, or __future__ imports
        if not self.has_import:
            import_node = cst.parse_statement(self.import_statement)
            new_body = list(updated_node.body)

            # Find the index to insert the import statement
            insert_index = 0
            for i, node in enumerate(new_body):
                # Skip docstrings (Expr with a string literal) and comments
                if isinstance(node, cst.SimpleStatementLine):
                    # Check for docstrings
                    if (
                        isinstance(node.body[0], cst.Expr) and
                        isinstance(node.body[0].value, cst.SimpleString)
                    ):
                        continue
                    # Check for comments
                    if any(isinstance(part, cst.Comment) for part in node.leading_lines):
                        continue
                    # Check for __future__ imports
                    if (
                        isinstance(node.body[0], cst.ImportFrom) and
                        node.body[0].module.value == "__future__"
                    ):
                        insert_index = i + 1
                        continue
                # Stop at the first non-docstring, non-comment, non-__future__ node
                insert_index = i
                break

            # Insert the import statement at the correct position
            new_body.insert(insert_index, import_node)
            self.has_import = True
            return updated_node.with_changes(body=new_body)
        return updated_node

    def leave_FunctionDef(self, original_node, updated_node):
        # Create the decorator node
        decorator = cst.Decorator(
            decorator=cst.Name(value=self.decorator_name)
        )

        # Add the decorator as the first decorator in the list
        new_decorators = list(updated_node.decorators) +  [decorator]
        return updated_node.with_changes(decorators=new_decorators)


def add_decorator_to_functions(file_path, decorator_name, import_statement, output_path=None):
    # Read the file content
    with open(file_path, "r") as file:
        code = file.read()

    # Parse the code into a CST
    module = cst.parse_module(code)

    # Create the transformer and apply it
    transformer = FunctionDecoratorTransformer(decorator_name, import_statement)
    modified_module = module.visit(transformer)
    new_text = modified_module.code

    # Write the modified code back to disk
    if output_path is None:
        output_path = file_path

    import xdev
    print(f"Modified code written to {output_path}")
    print(xdev.difftext(code, new_text, colored=True, context_lines=3))

    with open(output_path, "w") as file:
        file.write(modified_module.code)


class AddDecoratorCLI(scfg.DataConfig):
    dpath = '/home/joncrall/code/home-assistant/core/homeassistant/components/jellyfin'
    decorator_name = 'debug_decorator'
    import_statement = 'from .debug import debug_decorator'

    @classmethod
    def main(cls, argv=1, **kwargs):
        """
        Example:
            >>> # xdoctest: +SKIP
            >>> from add_decorator import *  # NOQA
            >>> argv = 0
            >>> kwargs = dict(dpath=ub.Path('~/code/home-assistant/core/homeassistant/components/jellyfin').expand())
            >>> cls = AddDecoratorCLI
            >>> config = cls(**kwargs)
            >>> cls.main(argv=argv, **config)
        """
        import rich
        from rich.markup import escape
        config = cls.cli(argv=argv, data=kwargs, strict=True)
        rich.print('config = ' + escape(ub.urepr(config, nl=1)))

        decorator_name = config.decorator_name
        import_statement = config.import_statement

        import kwutil
        fpaths = kwutil.util_path.coerce_patterned_paths(config.dpath, '.py')
        print(f'fpaths={fpaths}')
        for file_path in fpaths:
            add_decorator_to_functions(file_path, decorator_name,
                                       import_statement)


__cli__ = AddDecoratorCLI

if __name__ == '__main__':
    """

    CommandLine:
        python ~/misc/poc/add_decorator.py
        python -m add_decorator
    """
    __cli__.main()
