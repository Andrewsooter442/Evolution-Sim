@echo off
REM Define project variables
SET REPO_URL=https://github.com/Andrewsooter442/Evolution-Sim.git
SET PROJECT_DIR=Evolution-Sim
SET ENV_NAME=Evolution-Sim
SET PYTHON_VERSION=3.13

echo Cloning repository...
git clone %REPO_URL%

cd %PROJECT_DIR% || (echo Failed to enter project directory & exit /b)
echo cd into the %cd% directory

where conda > nul 2>nul
IF %ERRORLEVEL% == 0 (
    echo Conda is available. Setting up a Conda environment.
    conda create -y -n %ENV_NAME% python=%PYTHON_VERSION%

    conda init

    call conda activate %ENV_NAME%
    echo Created the conda environment successfully
) ELSE (
    echo Conda is not available. We recommend using Conda for better dependency management.
    echo Falling back to python -m venv.
    python -m venv %ENV_NAME%
    call %ENV_NAME%\Scripts\activate.bat
)

echo Installing project dependencies...
IF EXIST "environment.yml" (
    IF EXIST "%CONDA_PREFIX%" (
        conda env update -f environment.yml
    )
) ELSE IF EXIST "requirements.txt" (
    pip install -r requirements.txt
) ELSE (
    echo No environment.yml or requirements.txt found.
)

cd Scripts
echo Running the program...
python main.py

echo Setup complete. Exiting.

