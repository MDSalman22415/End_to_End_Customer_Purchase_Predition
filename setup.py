from setuptools import find_packages , setup 
from typing import List

HYPEN_E_DOT = '-e .'
def get_requiremtns(file_path:str)->List[str]:
    '''
    This function return list of requirements
    '''
    requiremtns=[]
    with open(file_path) as file_obj:
        requirements=file_obj.readlines()
        requirements = [req.replace("\n","") for req in requirements]
        
        if HYPEN_E_DOT in requiremtns:
            requiremtns.remove(HYPEN_E_DOT)
            
    return requiremtns

setup(
    name="End_to_End_E-Commerce_Purchsed_Prediction",
    version='0.0.1',
    author='MD Salman',
    author_email="mdsalmankhan41868@gmail.com",
    packages=find_packages(),
    install_requires=get_requiremtns('requirements.txt')
)
    