from setuptools import setup

setup(name='taskbridge',
      version='0.0.1',
      py_modules=['taskbridge'],
      install_require=[
          'Click'
      ],
      entry_points={
          'console_scripts': [
              'taskbridge=taskbridge:main'
          ]
      }
)
