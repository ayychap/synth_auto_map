import setuptools

setuptools.setup(
    name='synth_auto_map',
    version='0.1',
    packages=['synth_auto_map'],
    url='https://github.com/ayychap/synth_auto_map',
    license='mit',
    author='ayychap',
    author_email='',
    description='Automation tools for Synth Riders beatmapping',
    package_dir={'': 'src'},
    python_requires='>=3.10',
    install_requires=['librosa', 'spleeter', 'numpy', 'scipy', 'pandas', 'matplotlib', 'synth-mapping-helper', 'mplcyberpunk']
)