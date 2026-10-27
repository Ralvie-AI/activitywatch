
from pathlib import Path
import subprocess
from glob import glob
import os
import re
ROOT = Path(__file__).resolve().parent


def find_target_module(target_module: str):

    except_module = ["sd_notify", "sd_watcher_input", "sd_cli"] # all module dont call these module
    submodule_packages = ['storages', 'persistqueue', 'serializers']

    match target_module:
        case "sd_pixel_engine":
            except_module.extend(["tls_generator", "sd_watcher_window", "sd_watcher_afk", "sd_client"])
        case "sd_main" | "sd_server":
            except_module.extend(["tls_generator", "sd_watcher_window", "sd_watcher_afk", "sd_client", "sd_pixel_engine"])
        case "sd_watcher_window":
            except_module.extend(["tls_generator", "sd_watcher_window", "sd_pixel_engine"])
        case "sd_watcher_afk":
            except_module.extend(["tls_generator", "sd_watcher_afk", "sd_pixel_engine"])
        case "tls_generator":
            except_module.extend(["sd_watcher_window", "sd_watcher_afk", "sd_client", "sd_pixel_engine"])
        case "all":
            pass

    target_module = [
        file
        for file in ROOT.rglob("*")
        if (file.is_dir() and (str(file.name).startswith(('sd_', 'tls_')) or file.name in submodule_packages))
        and (file.name not in except_module )
    ]

    return target_module

def find_import(target_module: str):


    import_list: list[str] = [
        'zoneinfo', 'concurrent', 'multiprocessing', 'asyncio', 'xml', 'xmlrpc', 'html', 'json', 'sqlite3', 'ctypes', 'dataclasses', 
        'logging.handlers', 'packaging', 'click', 'filelock', 
        'platformdirs', 'more_itertools', 'cachetools', 'deprecation', 'jsonschema', 'jsonschema_specifications', 'referencing', 'rpds', 
        'attrs', 'attr', 'tomlkit', 'omegaconf', 'yaml', 'dateutil', 'dateutil.parser', 'pytz', 'tzlocal', 'iso8601', 'aniso8601', 
        'timeslot', 'requests', 'urllib3', 'certifi', 'idna', 'charset_normalizer', 'chardet', 'tldextract', 'flask', 'flask_cors', 
        'flask_restx', 'flask_jwt_extended', 'werkzeug', 'jinja2', 'markupsafe', 'itsdangerous', 'blinker', 'peewee', 'playhouse', 
        'playhouse.migrate', 'playhouse.shortcuts', 'playhouse.sqlcipher_ext', 'sqlcipher3', 'pysqlcipher3', 'PIL', 'numpy', 'rapidocr', 
        'pyclipper', 'onnxruntime', 'openvino', 'openvino_telemetry', 'antlr4', 'bidi', 'cryptography', 'cryptography.fernet', 'keyring', 
        'jwt', 'pam', 'PySide6', 'PySide6.QtWidgets', 'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtSvgWidgets', 'PySide6.QtNetwork', 
        'shiboken6', 'qdarktheme', 'darkdetect', 'AppKit', 'Foundation', 'CoreFoundation', 'objc', 'PyObjCTools', 'psutil', 'mss', 'cffi', 
        'pycparser',
        #'distutils', '_distutils_hack', 'pkg_resources', 'trove_classifiers', 'jaraco', 'pydoc_data', 'unittest',
        #'curses', 'smtplib', 'colorlog', 'tqdm', 'importlib_metadata', 'importlib_resources', 'zipp'
    ]

    add_binaries: list[tuple] = []

    for module in target_module:

        files = glob(os.path.join(f'{module}/extensions', '*.so'))

        import_name: list = []
        binaries_location: list = []

        for file_path in files:

            matched = re.search(r"(?:sd_|tls_).*", file_path)

            if matched:
                result = matched.group().replace('/extensions', '')
                import_text = (result.replace('/', '.')).split('.so')[0]

                binaries_path = '/'.join((result.split('/'))[:-1])
                binaries = (file_path, f'./{binaries_path}')

                import_name.append(import_text)
                binaries_location.append(binaries)

        import_list.extend(import_name)
        add_binaries.extend(binaries_location)

    return import_list, add_binaries

def main():

    target_module = find_target_module('all')
    print(*target_module, sep='\n')

if __name__ == "__main__":
    main()