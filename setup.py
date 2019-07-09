import setuptools

requirements = []

with open("requirements.txt", "r") as f:
    for line in f.readlines():
        requirements.append(line[:line.find('==')])

with open('README.md', 'r') as f:
    long_description = f.read()


setuptools.setup(
    name="path_of_pain_daily_build",
    version="0.0.2.dev0",
    author="ilyabelow",
    author_email="belof.ilya@gmail.com",
    description="Simple top view slasher for a uni course on Python & Programming technologies & CI",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/ilyabelow/path_of_pain",
    license='MIT',
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Topic :: Software Development :: Build Tools',
        "Development Status :: 1 - Planning",
        "Natural Language :: English",
        "Topic :: Games/Entertainment",
        "Intended Audience :: End Users/Desktop",
    ],
)
