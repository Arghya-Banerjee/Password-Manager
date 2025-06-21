from setuptools import setup, find_packages

setup(
    name="password_manager",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "cryptography>=41.0.0",
        "PySimpleGUI>=4.60.0",
    ],
    entry_points={
        "console_scripts": [
            "pm-cli = password_manager.cli:main",
            "pm-gui = password_manager.gui:main",
        ],
    },
    python_requires=">=3.9",
)
