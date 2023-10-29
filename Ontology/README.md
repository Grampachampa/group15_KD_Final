# Group 15 K&D Final Project

Group 15 is proud to present their final project. If you are reading this, it means you are ready to jump into the world of visualization!
## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the necessary packages. If you have any issues, consult the first cell of the .ipynb file, and check that you have everything that is required installed.

```bash
pip install rdflib
pip install pandas
pip install folium
pip install branca
pip install selenium
pip install imageio
```

### (OPTIONAL) GeckoDriver
In order to simulate more than one day, Images have to be saved. We do this via automating a process where firefox is repeatedly opened, the tab is captured and saved as an image, and then closed. In order to do this, you need [GeckoDriver](https://github.com/mozilla/geckodriver/releases). You will need to add it to your [path](https://www.softwaretestinghelp.com/geckodriver-selenium-tutorial/#:~:text=Click%20on%20the%20Environment%20Variables,Click%20on%20the%20Edit%20button.&text=Paste%20the%20path%20to%20the%20GeckoDriver%20file.)

**THIS IS COMPLETELY OPTIONAL. THE EXPERIENCE FOR THE TA GRADING THIS PROJECT WAS DESIGNED WITHOUT THIS FEATURE IN MIND. IT ONLY EXISTS FOR THE PURPOUSE OF GIF CREATION.**

## Setup
We ask that you house the .ttl ontology file in the same directory as you house the .ipynb file that comes with this document. This allows us to easily find it's location and minimizes issues on your end.

## Usage
The only point at which the user has to interact with the code is in the second code cell. Here, you are asked to pick a day:

```python
single_day = True
date = 123 # 0-364; CHANGE THIS TO CHANGE THE DATE

year = 2022

date = max(0, min(date, 364)) + 1

ymd = datetime.date(year, 1, 1) + datetime.timedelta(date - 1)
```
You are asked to replace the number 123 to any number you desire that is between 0 and 364 (or not).

Other than this, you are just asked to run the cells one by one. Some cells (like the last one) might not do anything, based on your settings. This is normal. Some cells may also take a large amount of time to run. We ask that you be patient and give it a minute. The ontology is large, and opening it up with python takes a while.

## Potential Issues
Everyone's system is different. This code was largely run on windows machines, so in the event that there are any unexpected issues, please do not hesitate to get in touch with group 15.

