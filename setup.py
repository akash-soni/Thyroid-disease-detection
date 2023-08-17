import setuptools
from typing import List


def get_requirements(file_path: str) -> List[str]:
    """
    This function will return list of requirements
    """
    HYPEN_E_DOT = "-e ."
    requirements = []
    with open(file_path) as file_obj:
        requirements = file_obj.readlines()
        requirements = [req.replace("\n", "") for req in requirements]

        if (
            HYPEN_E_DOT in requirements
        ):  # when running requirements.txt it will ignore -e . as we already have setup.py which will build setup for us
            requirements.remove(HYPEN_E_DOT)
    requirements_list: List[str] = [requirements]
    return requirements_list


# edit below variables as per your requirements -
REPO_NAME = "Thyroid-disease-detection"
AUTHOR_USER_NAME = "akash-soni"


setuptools.setup(
    name=REPO_NAME,
    version="0.0.1",
    author=AUTHOR_USER_NAME,
    description="Thyroid-disease-detection",
    long_description="Classifiy wheather patient is suffering with thyroid or not",
    long_description_content_type="text/markdown",
    url=f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}",
    author_email="akash.200287@gmail.com",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=get_requirements("requirements.txt"),
    license="MIT",
)