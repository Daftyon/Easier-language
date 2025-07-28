from setuptools import setup, find_packages

setup(
    name='easierlang',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        # List your dependencies here
    ],
    entry_points={
        'console_scripts': [
            'easierlang = compiler.main:main',
        ],
    },
    author='AHMED HAFDI',
    author_email='ahmed.hafdi.contact@gmail.com',
    description='A brief description of your compiler',
    long_description='Longer description of your compiler',
    url='https://github.com/HAFDIAHMED/Easier-Lang',  # Replace with your GitHub repository URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
