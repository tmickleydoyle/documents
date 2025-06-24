"""
Setup configuration for the Universal Code Evaluation Framework.
"""

from pathlib import Path

from setuptools import find_packages, setup

# Read README file
readme_file = Path(__file__).parent / "README.md"
long_description = (
    readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""
)

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = requirements_file.read_text().strip().split("\n")

# Read dev requirements
dev_requirements_file = Path(__file__).parent / "dev-requirements.txt"
dev_requirements = []
if dev_requirements_file.exists():
    dev_requirements = dev_requirements_file.read_text().strip().split("\n")

setup(
    name="fern-nextjs-eval",
    version="1.0.0",
    description=(
        "Universal Code Evaluation Framework for comparing any type "
        "of application"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Fern Team",
    author_email="team@fern.dev",
    url="https://github.com/fern-api/fern-nextjs-eval",
    packages=find_packages(include=["src", "src.*"]),
    package_dir={"": "."},
    include_package_data=True,
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "test": dev_requirements,
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "fern-eval=cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
    ],
    keywords="code evaluation, ai models, semantic similarity, code quality",
    project_urls={
        "Bug Reports": "https://github.com/fern-api/fern-nextjs-eval/issues",
        "Source": "https://github.com/fern-api/fern-nextjs-eval",
        "Documentation": (
            "https://github.com/fern-api/fern-nextjs-eval/blob/main/README.md"
        ),
    },
)
