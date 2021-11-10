# Micro Hidroponic
> Small project to interact with python, C, HTML, JavaScript, PHP.

## Table of Contents
* [General Info](#general-information)
* [Technologies Used](#technologies-used)
* [Screenshots](#screenshots)
* [Usage](#usage)
* [Project Status](#project-status)
* [Contact](#contact)
<!-- * [License](#license) -->


## General Information
- Create a small hydroponics greenhouse with web interaction.
- Create small server on Raspberry Pi
- Interact Python, C and DB
- Development of webpage (backend and frontend)

## Technologies Used
- RPi
- Arduino
- Sensor reading
- WordPress
- MariaDB
- MyPHPAdmin


## Screenshots

<div align="center">

![screenshot1](/img/Web.jpg)

![screenshot2](/img/DB.jpg)

![screenshot2](/img/shell.jpg)

</div>



## Usage
This project was developed in 4 parts.

#### First Arduino:
Made to comunicate with RPI(using serial port and JSON),read the sensors and give information to the motors .
[ARDUINO](Arduino_Final.ino)

#### Second Python:
Manager of the all system. Interaction with DB and Arduino.
[Python](Gestor_Final.py)

#### Third RPI CONFIG:
Here you can find a .img of the RPI fully configurated.
[SDCARD](Filipe.img)

#### Fourth WEB development:
The main template was created with WordPress and the content of each page was:
 - Interior Data: [Interior](Dados_interior.html)
 - Levels: [LVLs](NIveis.html)
 - To plant: [ToPlant](Plantar.html)
 - Manual Action: [Manual](Manual.html)

## Project Status

Project is: Complete.
* If you want to have a full documentation about this project just click [Here](FilipeMartins_RelatorioFinal.pdf).
The all project is in Portuguese (my main language), any question be free to concact me.


## Contact
Created by [@FilipeMartins](https://www.linkedin.com/in/filipe-martins-541088b0/) - feel free to contact me!
