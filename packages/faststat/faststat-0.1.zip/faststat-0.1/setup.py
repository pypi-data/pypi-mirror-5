from distutils.core import setup, Extension

_faststat = Extension('_faststat', sources=['faststat/_faststat.c'])

setup(
    name='faststat',
    version='0.1',
    author="Kurt Rose",
    author_email="kurt@kurtrose.com",
    description='fast online statistics collection',
    license="MIT",
    url="http://github.com/doublereedkurt/faststat",
    long_description='...',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
    ],
    packages=['faststat'],
    ext_modules=[_faststat])
