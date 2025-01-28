from setuptools import setup, find_packages

setup(
    name="autosearch",
    version="0.1",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "autogen",
        "arxiv",
        "requests",
        "PyPDF2",
        "ipython",
        "unstructured[all-docs]",
        "azure-ai-formrecognizer",
        "azure-common",
        "azure-core",
        "azure-functions",
        "azure-identity",
        "tiktoken",
        "langchain",
        # Add other dependencies here
    ],
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)