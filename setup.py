from setuptools import setup
from Cython.Build import cythonize
from glob import glob
from pathlib import Path
import shutil
import os
from cython_config import find_target_module
import time
import re

TARGET_MODULE = find_target_module('all')
ALL_SUBMODULE = [submodule.name for submodule in TARGET_MODULE]
ROOT = Path.cwd()

class SetUpFile():

    def __init__(self, file_path: str, file_list: list[str]):
        self.file_path = file_path
        self.file_list = file_list

        self.extention_path = f'{self.file_path}/extensions'
        self.module_name = Path(file_path).name
        matched = re.search(r"(?:sd_|tls_).*", str(file_path))
        if matched:
            self.module_path = matched.group()

        self.target_path = f'{ROOT}/{self.module_path}'


    def run(self):

        self._clear()

        print('================ Lets Me Protect Your File ================')

        setup(
            ext_modules = cythonize(
                self.file_list,
                compiler_directives={
                    'language_level': "3",
                    'annotation_typing': False,
                },
                force=True,
                verbose=True,
            )
        )


        self._move_file()

    def _move_file(self):
        print(f'================ Lets Me Moving YOUR file ================')
        print(f"My extention path: {self.extention_path}")
        Path(self.extention_path).mkdir(parents=True, exist_ok=True)
        file_type = ['.so', '.c']

        for i in file_type:
            if i == '.so':
                target_file = glob(os.path.join(self.target_path, f'*{i}')) 

                for filename in target_file:

                    short_name = filename.split('.')[0] + '.so'
                    if filename != short_name:
                        os.rename(filename, short_name)
                        shutil.move(short_name, self.extention_path)                
            else:
                target_file = glob(os.path.join(f'{self.file_path}', '*.c'))

                for filename in target_file:
                    shutil.move(filename, self.extention_path)


        if self._is_leaf_submodule():
            path = re.sub(r"(/activitywatch/[^/]+).*", r"\1", str(self.target_path))
            shutil.rmtree(path)

    def _clear(self):

        print(f'================ Lets Me Clearing YOUR old file ================')
        print(f"Clearing path: {self.extention_path}")

        if Path(self.extention_path).exists():

            all_file = glob(os.path.join(f'{self.extention_path}', '*'))

            for file in all_file:
                Path(file).unlink(missing_ok=True)

            Path(self.extention_path).rmdir()

    def _is_leaf_submodule(self) -> bool:

        is_leaf_submodule: list[bool] = []
        for path in self.file_path.iterdir():
            if path.is_dir():
                if path.name in ALL_SUBMODULE:
                    is_leaf_submodule.append(False)
                else:
                    is_leaf_submodule.append(True)
                    
        return True if all(is_leaf_submodule) else False

def main():

    # For other modules    
    for module in TARGET_MODULE:
        SetUpFile(
            file_path=module,
            file_list=[
                file
                for file in glob(os.path.join(module, '*.py')) 
                if ("sd-core" in file) or ("sd-client" in file) or (bool(Path(file).name.startswith('__')) == False)
            ],
        ).run()

if __name__ == "__main__":
   main()
