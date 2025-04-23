from setuptools import setup, find_packages

setup(
    name='llm-policy-analysis',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    # Add other metadata like author, description, license, etc.
    install_requires=[
        # List your project dependencies here
        # e.g., 'requests',
    ],
    extras_require={
        'dev': [
            'pytest',
            # Add other development dependencies
        ]
    },
)
