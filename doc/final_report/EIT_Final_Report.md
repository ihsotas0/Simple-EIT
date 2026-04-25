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

# Final Device



# Experiment 4

Jonah, Lory, Connor

Basic manual MUX test and 2nd highest on that. Fixed RPi MUX switching being backwards. Wrapped cables.

First time full integration of RPi, MUX, and visualizer. For 4 sectors with eraser and voltmeter, not scope, and 2nd highest method.

# Experiment 5

Jonah, Connor

Original version of data collect with manual labeling (painfully) with voltmeter and tried 4 pixel display running 2nd highest, which didn't work. It did work for voltmeter, but the voltmeter voltage measurements were more seperatble than the scope. First test of using scope vs wavegen to improve speed. Spend hours trying to speed up voltmeter and failed, so which used scope, rewrote code, etc.

# Experiment 6

Jonah: Used EDU scope, got data using data_collector.py

# Made CURC Poster

Jonah

# Experiment 7

Jonah, Lory: Verified device, fixed device_manager bugs (serial input and reloading connection twice).

# Presented CURC Poster

Jonah


# TEMP: Images

![Voltage Distributions per Location of curc_a](../curc_figures/curc_a_data.png)
![Voltage Distributions per Location of curc_b](../curc_figures/curc_b_data.png)
![Voltage Distributions per Location of curc_c](../curc_figures/curc_c_data.png)
![Voltage Distributions per Location of curc_d](../curc_figures/curc_d_data.png)
![Voltage Distributions per Location of curc_a](../curc_figures/curc_e_data.png)
![Voltage Distributions for Different Frequencies ](../curc_figures/instrument_data.png)
![Voltage Distributions for Salene Solution](../curc_figures/instrument_salt_data.png)
![Loss Curve for curc Objects using MLP Model](../curc_figures/loss_figure.png)
![Accuracy of ML Models per Radius of the Object](../curc_figures/model_accuracy.png)

![Early 16 Sector Display using MatPlotLib](./first_16_sector_display.jpg)
![Early Models for Voltage Distributions](./making_curc_figures.jpg)
![Demo Day hardware and Software](./title_image.jpg)
![Training Data for curc Models in Chem Lecture](./training_curc_models_in_chem_lecture.jpg)
![Early Visualization designs](./visualization_sticky_notes.jpg)
![Brainstorming Poster Data Presentation](./whiteboard_1.jpg)
![Brainstorming Model Accuracy (delete)](./whiteboard_2.jpg)
![Brainstorming Model Accuracy vs Radius for Poster](./whiteboard_3.jpg)
![Data Collection method for curc Poster & Calcuations for Salinity](./whiteboard_4.jpg)
![Brainstorming Hardware Documentation](./whiteboard_5_hardware_details.jpg)

![CURC Poster](../Simple_EIT_CURC_Poster.png)

![Wiring For MUX Experiment 4](./experiment_4_images/closeup.jpg)
![Hardware Wiring Issue Experiment 4](./experiment_4_images/eperiment_4_wiring_issue.jpg)
![Eraser Locating Test Experiment 4](./experiment_4_images/eraser_rig.jpg)
![Full Device Hardware Setup for Experiment 4](./experiment_4_images/full_view.jpg)
![Benchtop Equipment Hardware for Experiment 4](./experiment_4_images/full_with_benchtop.jpg)

![Full View of Experiment 5](./experiment_5_images/ful_view_better.jpg)
![New Measurement Method for Experiment 5: Oscilicope](./experiment_5_images/scope_output.jpg)
![Early Accuracy Data for Models Experiment 5](./experiment_5_images/testing_models_on_data.jpg)

![New Sector Labeling on Test Rig Experiment 6](./experiment_6_images/clean_test_rig.jpg)
![MUX Wiring Experiment 6](./experiment_6_images/closeup.jpg)
![Full Hardware Setup for Experiment 6](./experiment_6_images/full_view.jpg)
![Data Log for Experiment 6](./experiment_6_images/logs_closeup.jpg)
![Test Rig with Standardized Object curc_a Experiemnt 6](./experiment_6_images/test_rig_closeup.jpg)

![Finalized Setup with new Oscilicope](./experiment_7_images/benchtop_equipment.jpg)
![Finalized Hardware Setup Experiment 7](./experiment_7_images/full_setup.jpg)
![Live Data Log Experiment 7](./experiment_7_images/live_data.jpg)
![MUX Wiring Experiment 7](./experiment_7_images/MUX_setup.jpg)
![Finalized Test Rig with Standardized Objects a-e](./experiment_7_images/test_rig.jpg)
![Debugging Filter for USB Connection ID](./experiment_7_images/USB_ID_debug.jpg)
![Fix for Filter of USB Connection ID](./experiment_7_images/USB_ID_fix.jpg)
![Name of Device to USB Connection IDs](./experiment_7_images/USB_ID_sectors.jpg)
![16 Section Probability Visualizer Experiment 7](./experiment_7_images/visualizer.jpg)







