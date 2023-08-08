# wrf-web-app
![Project Logo](link_to_your_logo.png)

Flask Web application to use WRF model

## Introduction

This project aims to create a user-friendly UI for running the Weather Research and Forecasting (WRF) model on your local computer. The UI allows users to easily install WRF, specify the desired date for running the model, configure the domain and run parameters, and visualize the outputs.

## Features

- Simple and intuitive UI for running WRF locally.
- Automatic installation of WRF.
- Easy date selection for running the model.
- Customizable domain and run parameters.
- Interactive visualization of WRF model outputs.

## Dependencies

To use this project, you need the following dependencies:
- A Debian based Linux distro like ubuntu, pop-os, linux-mint etc.. 
- Anaconda environment manager of your choice -> [miniconda or anaconda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html)

## Installation
 
- Enter to the directory of your choice to download the project into.
```bash
cd Documents
```

- Clone this repository to your local machine.
```bash
git clone https://github.com/d00dy89/wrf-web-app.git
```

- After downloading the code change directory to the project directory.
```bash
cd wrf-web-app
```

- Create project conda environment and install dependencies
```bash
conda create --prefix ./wrf_conda_env --file spec-file.txt
```

- Activate conda environment
```bash
conda activate wrf_conda_env/
```

- After activating the environment run the app with
```bash
python run_app.py
```
