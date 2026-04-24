---
title: "ECE 202 Final Report: Simple EIT"
author: |
  Team Members: Jonah Spector, Connor Cassidy, Christian Rayner  
  EIR Mentor: Chuck Duey
date: "April 24, 2026"
geometry: margin=3cm
---

<!-- Use this command to make the report: -->
<!-- pandoc -H img_fix.tex -f markdown+table_captions midreport.md -o EIT_Mid_Report.pdf -->

Electrical impedance tomography is a method for medical imaging which visualizes
the internal resistivity of the human body, namely for real-time monitoring of
the lungs. It measures the voltage on n-electrodes and sends an alternating
current through 2 other electrodes. This results in a non-linear, ill-posed
boundary value problem which, when solved, gives a 2D tomogram of resistivities.
We have decided to make a 4 electrode electrical impedance tomography device for
our project using an *empirical algorithm* to calculate the location of an
object. Our visualization will, at the very least, show four pixels, each
representing the four quadrants outlined on the sides by the electrodes. Each
pixel will show the likelihood that there is an object of higher resistivity
(OHR) contained in that quadrant. This visualization, we hope, will update at a
reasonable framerate of 5-60 fps. If we succeed at this, we may expand our
project to have more electrodes, a better framerate, a complete inverse
algorithm, or improve it in other ways.

Link to code and other documentation: <https://github.com/ihsotas0/simple-eit>

\newpage

# Experiment 4

Jonah, Lory, Connor

Basic manual MUX test and 2nd highest on that. Fixed RPi MUX switching being backwards. Wrapped cables.

First time full integration of RPi, MUX, and visualizer. For 4 sectors with eraser and voltmeter, not scope, and 2nd highest method.

# Experiment 5

Jonah, Connor

Original version of data collect with manual labeling (painfully) with scope and tried 4 pixel display running 2nd highest, which didn't work. It did work for voltmeter, but the voltmeter voltage measurements were more seperatble than the scope. First test of using scope vs wavegen to improve speed. Spend hours trying to speed up voltmeter and failed, so which used scope, rewrote code, etc.

# Experiment 6

Jonah

# Made CURC Poster

Jonah

# Experiment 7

Jonah, Lory

# Presented CURC Poster

Jonah

