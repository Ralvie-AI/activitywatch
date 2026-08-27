build:
	poetry install

package:
	pyinstaller tls-generator.spec --clean --noconfirm

clean:
	rm -rf build dist
	rm -rf tls_generator/__pycache__