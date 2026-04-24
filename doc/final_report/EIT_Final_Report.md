---
title: "ECE 202 Final Report: Simple EIT"
author: |
  Team Members: Jonah Spector, Connor Cassidy, Christian Rayner  
  EIR Mentor: Chuck Duey
date: "April 24, 2026"
geometry: margin=3cm
---

<!-- Use this command to make the report: -->
<!-- nix-shell --pure -p pandoc -p texlive.combined.scheme-small --run "pandoc -H img_fix.tex -f markdown+table_captions EIT_Final_Report.md -o EIT_Final_Report.pdf" -->

Electrical Impedance Tomography (EIT) is a method of medical imaging which
visualizes the internal resistivity of the human body, most commonly for
real-time monitoring of the lungs. It measures voltage on n-1 pairs of
electrodes, and sends an alternating current through the remaining pair of
electrodes. The pair of electrodes which produces the alternating current is
then replaced with a different pair of electrodes until all possible
combinations of electrodes are exhausted. This results in a non-linear,
ill-posed boundary value problem which, when solved, gives a 2D tomogram of
resistivities. We created a 4 electrode EIT device which utilizes machine
learning algorithms running locally to predict the location of an object of
higher resistivity (OHR) within one of 16 sectors. This probability distribution
is then visualized on a computer monitor in real time.

Link to code and other documentation: <https://github.com/ihsotas0/simple-eit>

![Simple EIT Setup on Demo Day](title_image.jpg){ width=85% }

\newpage

# Experiment 4

Jonah, Lory, Connor

Basic manual MUX test and 2nd highest on that. Fixed RPi MUX switching being backwards. Wrapped cables.

First time full integration of RPi, MUX, and visualizer. For 4 sectors with eraser and voltmeter, not scope, and 2nd highest method.

# Experiment 5

Jonah, Connor

Original version of data collect with manual labeling (painfully) with scope and tried 4 pixel display running 2nd highest, which didn't work. It did work for voltmeter, but the voltmeter voltage measurements were more seperatble than the scope. First test of using scope vs wavegen to improve speed. Spend hours trying to speed up voltmeter and failed, so which used scope, rewrote code, etc.

# Experiment 6

Jonah: Used EDU scope, got data using data_collector.py

# Made CURC Poster

Jonah

# Experiment 7

Jonah, Lory: Verified device, fixed device_manager bugs (serial input and reloading connection twice).

# Presented CURC Poster

Jonah

