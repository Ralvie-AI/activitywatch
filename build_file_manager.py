from pathlib import Path
import os
import shutil
import argparse
from glob import glob
from cython_config import find_target_module

TARGET_MODULE = find_target_module('all')

class FileManager():

    def __init__(self, module_path: str):

        self.module_path = module_path

        self.backup = f'{module_path}/backup'
        Path(self.backup).mkdir(parents=True, exist_ok=True)

        self.target_path = glob(os.path.join(f'{self.module_path}', '*.py'))
        self.backup_files = glob(os.path.join(f'{self.backup}', '*.py'))

    def move_file(self):

        for file_path in self.target_path:
            if ("sd-core" in file_path) or ("sd-client" in file_path) or (bool(Path(file_path).name.startswith('__')) == False):
                shutil.move(file_path, self.backup)

    def restore_file(self):

        for file_path in self.backup_files:      
            dst_path = self.module_path
            shutil.move(file_path, dst_path)

        shutil.rmtree(self.backup)

def main():

    parser = argparse.ArgumentParser()
    #parser.add_argument('--target_module', nargs='+', required=True)
    parser.add_argument('--action', type=str, required=True)
    args = parser.parse_args()

    #for module in args.target_module:
    for module in TARGET_MODULE:
        
        module_path = module

        file_manager = FileManager(module_path)

        if args.action == 'move':
            file_manager.move_file()
        elif args.action == 'restore':
            file_manager.restore_file()

if __name__ == "__main__":
    main()