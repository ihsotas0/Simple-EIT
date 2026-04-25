---
title: "ECE 202 Final Report: Simple EIT"
author: |
  Team Members: Jonah Spector, Connor Cassidy, Christian Rayner  
  EIR Mentor: Chuck Duey
date: "April 24, 2026"
geometry: margin=2cm
---

<!-- Use this command to make the report, remove nix-shell part if your run
this on a different OS: -->
<!-- nix-shell --pure -p pandoc -p texlive.combined.scheme-small --run "pandoc --number-sections
-H img_fix.tex -f markdown+table_captions EIT_Final_Report.md -o EIT_Final_Report.pdf" -->

Electrical Impedance Tomography (EIT) is a method of medical imaging which
visualizes the internal resistivity of the human body, most commonly for
real-time monitoring of the lungs. It measures voltage on n-1 pairs of
electrodes, and sends an alternating current through the remaining pair of
electrodes. The pair of electrodes which produces the alternating current is
then replaced with a different pair of electrodes until all possible
combinations of electrodes are exhausted. This results in a non-linear,
ill-posed boundary value problem which, when solved, gives a 2D tomogram of
resistivity. We created a 4 electrode EIT device which utilizes machine learning
algorithms running locally to predict the location of an object of higher
resistivity (OHR) within one of 16 sectors. This probability distribution is
then visualized on a computer monitor in real time.

Link to code and other documentation: <https://github.com/ihsotas0/simple-eit>

![Simple EIT Setup on Demo Day](title_image.jpg){ width=85% }

\newpage

# Introduction

We chose EIT as the topic of our ECE 202 project because we believe it
encompassed a wide range of disciplines within electrical engineering. For
Jonah, he was interested in the software used to analyze voltages, interface
with hardware, and produce a visualization. Jonah is also interested in working
in Dr. Mueller's EIT lab here on campus, and used this project as an opportunity
to learn about EIT, get experience with real hardware and software, and form and
 present a research question. For Connor and Christian, they were both
interested in the hardware necessary for high-speed multiplexing and
instrumentation. Early on, we decided our device would not solve for the
impedances at different locations, but only the location of one specific
introduced impedance (our OHR). This major restriction in scope allowed us to
complete this project in one semester.

Since our ability to design and manufacture entirely custom EIT circuits was
limited, we had to reduce the number of electrodes we used down to 4 to allow us
to use dedicated evaluation boards given to us by our EIR mentor Chuck Duey.
With only 4 electrodes, the resolution of our boundary conditions, necessary for
the computation of internal impedances, was far to limited to implement full
EIT. Despite this, we were able to achieve 16 pixel resolution of a known
impedance. By keeping the frequency and other parameters constant, the impedance
constant, it was possible to extract more information from the 6 voltage
measurements: enough for a proper demonstration of the device.

We don't think our instrument has many applications, but it does show the
feasibility of using simple conditional models on low dimensional data with
constant parameters to extract usable information (as opposed to full EIT
algorithms on significantly higher dimensional data). It may even have
applications for the detection of objects in anatomy given ground truth data
using EIT.

![Example of Real EIT Image](eit_demo.png)

\newpage

# Final Device

## Hardware

Team members responsible: Jonah, Connor, Christian

The final test rig design consisted of a 14cm diameter 3.5cm tall open cylinder
of PETG which served to contain the water (100ml). Four stainless steel
electrodes (2.5 x 2.5cm) were clamped to the corners of each quadrant using
alligator clips. The test rig presented at the industry advisory board meeting
included slots for the electrodes. The top of each alligator clip is soldered to
four wires which have pomona grabbers on the opposite end. The 16 pomona
grabbers (4 for each quadrant) are secured to the MUX36D04EVM-PDKs (MUXs),
labeled as M1 and M2 shown in the circuit diagram. The positive probes of the
EDU33212A Keysight Waveform Generator and DSOX1202A Keysight Oscilloscope are
connected to DA and DB of M1 respectively, while the negative probes are
connected to DA and DB of M2. VSS of each MUX is shorted to GND using a wire. A
second wire bridges the VDD and GND of each MUX. VDD of M1 is then connected to
a 10V DC power supply and GND is connected to the ground of the DC power supply.

The GPIO pins of the Raspberry Pi 3B are connected as shown in the circuit
diagram. They operate on a 3.3V logic to enable and disable each MUX, and switch
which outputs (SA/B 1-4) to the inputs (DA/DB). Pin 39 also grounds the
Raspberry Pi 3B to the GND of the MUXs. The Raspberry Pi 3B is connected to the
EDU33212A Keysight Waveform Generator and DSOX1202A Keysight Oscilloscope via
USB. It is also wired to a keyboard and mouse over USB, and the monitor over
HDMI. The configuration of the wavegen and oscilloscope was controlled by the
RPi, and the frequency of the wavegen was set to 10 kHz after some
experimentation. For testing, PLA cylinders (our OHRs) of 3.0, 6.0, 8.0, 12.5,
and 15.0mm radius were used.

To ensure the area of each sector was equal, the inner radius is defined as:

$$ r_i = \frac{r_o}{\sqrt{2}} $$

![Circuit Diagram](./Circuit_Diagram.png){ width=85% }

| Component           | Model/Specification                      | Purpose                              | Source               |
| :------------------ | :--------------------------------------- | :----------------------------------- | :------------------- |
| Digital Multimeter  | Keysight (any VISA-compatible)           | RMS voltage measurement              | C105                 |
| Waveform Generator  | Agilent/Keysight (any VISA-compatible)   | Excitation signal                    | C105                 |
| Analog Multiplexers | 2× MUX36D04EVM-PDK                       | Electrode selection (S+, S-, V+, V-) | Borrowed, EIR Mentor |
| DC Power Supply     | 10 V DC                                  | Power multiplexer evaluation boards  | C105                 |
| Controller          | Raspberry Pi 3B (recommended)            | GPIO control and computation         | Borrowed, Friend     |
| 3D Printed Test Rig | PET G                                    | Hold OHR and water                   | I2P Lab, Free        |
| Electrodes          | 4x Stainless steel electrodes            | Measure voltage/generate current     | Given, Free          |
| Connectors          | (16 + 2 + 2 + 4)x Banana hook connectors | Wire devices together                | $30, Amazon    |

Table: Hardware bill of materials

## Software

Team members responsible: Jonah

All software can be found on the GitHub linked on the title page. Most details
on installation and setup are in the README and too technical for this report.
All parts of the code extensively log and report specific errors to help with
hardware debugging.

Simple EIT uses a complete software stack and machine learning pipeline that:

- **Acquires voltage data** from 6 electrode configurations using multiplexed
  hardware
- **Classifies measurements** using trained ML models to identify OHR location
- **Visualizes results** in a real-time circular 16-sector display
- **Supports multiple classifiers**: SVM (recommended), Random Forest, XGBoost,
  Neural Networks, and more
- **Caches trained models** for each object to avoid redundant training
- **Auto-calibrates new objects** by collecting small datasets for ML training
  real-time

Simple EIT architecture:

- `main.py`: GUI and orchestration (includes autocalibration for less data)
- `simple_eit.py`: EIT control layer
- `device_manager.py`: PyVISA instrument control
- `classifier.py`: ML model management
- `data_collector.py`: Training data collection (for more data)

One essential part of the code, which defines the `scikit-learn` ML models used
for classification:

```py
MODEL_FACTORY = {
    "gb": lambda: GradientBoostingClassifier(),
    "knn": lambda: KNeighborsClassifier(n_neighbors=6),
    "lda": lambda: LinearDiscriminantAnalysis(),
    "logreg": lambda: LogisticRegression(max_iter=2500),
    "mlp": lambda: MLPClassifier(
        hidden_layer_sizes=(10, 10), max_iter=2500, random_state=RANDOM_STATE
    ),
    "rf": lambda: RandomForestClassifier(n_estimators=200, random_state=RANDOM_STATE),
    "svm": lambda: SVC(kernel="rbf", probability=True),
    "xgb": lambda: XGBClassifier(
        n_estimators=200, learning_rate=0.05, max_depth=4, verbosity=0)}
```

Libraries used: `gpiozero, joblib, matplotlib, numpy, pandas, pyvisa,
scikit-learn, scipy, xgboost, tkinter`, among others.

\newpage

# Experiment 4

Summary: Verified device on large OHR to differentiate four quadrants.

Date: March 27, 2026

Team members present: Jonah, Connor, Christian

Our first experiment since the mid-report, we started by using new four channel
pomona grabber to alligator clip cables for the MUX in order to switch between
configurations. First we used the MUX manually to find trends in the data. We
observed that the index of the 2nd highest of the non-diagonal voltage
measurements defined the location of the object. Using this newfound method, we
decided to test our code using an eraser as our OHR and conducted a second
manual MUX test. Unfortunately, no image was captured of the visualization output.

![Experiment 4: Full Device Setup](./experiment_4_images/full_view.jpg){ width=50% }

![Experiment 4: Wiring Closeup](./experiment_4_images/closeup.jpg){ width=50% }

![Experiment 4: Eraser as OHR in Test Rig](./experiment_4_images/eraser_rig.jpg){ width=50% }

The device output the wrong location when tested for all four quadrants. But, we
noticed that this was caused by an issue where the indices were labelled
according to the source configuration and not voltage measurement configuration
(where V_AB represented the nodes the signal was sent across instead of the
voltage measured). This was what caused Experiment 3 (found in the mid-report)
to fail:

![Experiment 4: Mislabeled Voltage Configurations](./experiment_4_images/eperiment_4_wiring_issue.jpg){ width=50% }

This experiment was the first full device integration, including RPi, MUXs, and
visualizer. We used an eraser as our OHR and voltmeter instead of oscilloscope,
and the 2nd highest method (limited to 4 quadrants) instead of an ML model.

\newpage

# Experiment 5

Summary: Switched the device from a slow voltmeter to a faster oscilloscope.

Date: April 3, 2026

Team members present: Jonah, Connor

Our original device used a voltmeter to measure the RMS voltage between
electrodes, but this took almost 5-10 seconds per measurement, well below our
requirements. Despite that, we decided to collect data to look for patterns for
new location classification algorithms. Our data collection script required
manually labeling of datapoints and was not intuitive to use, which made data
collection very difficult. We tried and failed to speed up the voltmeter, so we
switched to an oscilloscope:

![Experiment 5: Full View](./experiment_5_images/full_view_better.jpg){ width=50% }

![Experiment 5: Oscilloscope Output](./experiment_5_images/scope_output.jpg){ width=50% }

The data we got from the oscilloscope was significantly different from the
voltmeter, but we were able to redo the data collection quickly. The patterns we
used in the voltmeter data to classify the location as being in one of four
quadrants were gone and the noise increased, so we decided to use machine
learning to classify the location of the OHR using perviously collected data. An
early test of some ML models on the data we collected showed promise:

![Experiment 5: Early ML Testing on OHR Data](./experiment_5_images/testing_models_on_data.jpg){ width=50% }

(It should be noted that we split each quadrant into 4 sectors to improve the
quality of the data we collected, and it was at this point that we decided to
improve the resolution of the device from 4 to 16 sectors.)

\newpage

# Experiment 6

Summary: Collected 22000 16-sector location data points and 2000 instrument
data points for the CURC poster and verification of ML models.

Date: April 12, 2026

Team members present: Jonah

For both CURC and our real-time demonstration of the device, I wanted to collect
significant data on different objects. To do this, I rewrote `data_collector.py`
to automatically collect measurements and only stop to tell the user to move the
object to a preselected location. Unlike the auto-calibration code written after
this experiment, 200 measurements were collected per location per object, unlike
the 10 necessary for auto-calibration. Because of this, the data collection
alone, for the instrument and objects, took almost 5 hours. Debugging the device
took many additional hours.

![Experiment 6: Full Hardware Setup](./experiment_6_images/full_view.jpg){ width=50% }

While debugging the device before taking measurements, I realized the MUXs were
not enabling when the RPi triggered GPIO pins 5 and 16. I performed the same
testing of the GPIO pins as we performed to find the grounding issue as
explained in the mid-report. GPIO pin 5 did not output the correct voltage, so I
moved it to a different pin to ensure the proper function of the MUX toggle
control.

![Experiment 6: Wiring Closeup](./experiment_6_images/closeup.jpg){ width=50%}

I also added dividers for each of the now 16 sectors in the test rig to ensure
the OHR was placed correctly. When the OHR was smaller than the sector, I moved
it around in the sector to ensure all possible voltages for said sector were
recorded for small objects. More discursion of this is included in the poster.

![Experiment 6: New Sector Divisions on Test Rig](./experiment_6_images/clean_test_rig.jpg){ width=50% }

![Experiment 6: Test Rig with Standardized Object `curc_a`](./experiment_6_images/test_rig_closeup.jpg){ width=50% }

![Experiment 6: Measurements Being Performed on `curc_a`](./experiment_6_images/logs_closeup.jpg){ width=50% }

\newpage

# Designing CURC Poster

Summary: Created research poster on data collected for the device on different OHRs.

Date: April 13-14, 2026

Team members present: Jonah

I decided to present an evaluation of our device at CURC, the undergraduate
poster conference. I wanted to see the smallest object our device could detect
and evaluate different ML models at different radii of the OHR.

After collecting the data for the five different objects (see Experiment 6), I
used an early version of `classifier.py` to generated the ML models and evaluate
their accuracies for each of the OHRs:

![CURC: Training Models](./training_curc_models_in_chem_lecture.jpg){ width=85% }

Then, using `visualization.py`, I started making figures for the poster,
which proved to be quite challenging given the large amount of data that needed
to be presented:

![CURC: Early Figures for Voltage Distribution Visualization](./making_curc_figures.jpg){ width=85% }

Here are the final figures we used for CURC:

![CURC: Voltage Distribution Data (curc_a)](../curc_figures/curc_a_data.png)

![CURC: Voltage Distribution Data (curc_b)](../curc_figures/curc_b_data.png)

![CURC: Voltage Distribution Data (curc_c)](../curc_figures/curc_c_data.png)

![CURC: Voltage Distribution Data (curc_d)](../curc_figures/curc_d_data.png)

![CURC: Voltage Distribution Data (curc_e)](../curc_figures/curc_e_data.png)

![CURC: Voltage Distribution Data for Different Frequencies](../curc_figures/instrument_data.png)

![CURC: Voltage Distribution Data for Saline Solution](../curc_figures/instrument_salt_data.png)

![CURC: Loss Curves for MLP Models](../curc_figures/loss_figure.png)

![CURC: Accuracy vs OHR Radius](../curc_figures/model_accuracy.png)

Our data was fit using the function:

$$ y = 1 - ae^{bx} $$

We linearized this in order to use linear regression to find the values of $a$ and $b$
and the coefficient of determination:

$$ \ln(1 - y) = bx + ln(a) $$

I put all this information on the poster and included other text describing the research. Here is the final poster we presented at CURC on April 21, 2026 after submitting it on April 14:

![CURC Poster](../Simple_EIT_CURC_Poster.png)

\newpage

# Experiment 7

Summary: Final debugging and verification of device for 16-sector visualization
and ML model caching.

Date: April 19, 2026

Team members present: Jonah, Christian

At this point in the project, the code was mostly complete aside from some small
GUI issues that were fixed an hour before demo day with little hassle. We
decided to do a final verification of the new auto-calibration script and
real-time ML classification code, including model caching and on-the-fly
training.

![Experiment 7: Finalized Hardware Setup ](./experiment_7_images/full_setup.jpg){ width=50% }

![Experiment 7: Wiring Closeup](./experiment_7_images/MUX_setup.jpg){ width=50% }

We encountered an issue with our device connection code that, for some reason,
had not caused issue. At first we thought the issue was with changing the
oscilloscope we used, so we checked the ID of the scope and realized it didn't
match the VISA ID:

![Experiment 7: PyVISA Device Selection ID Issue](./experiment_7_images/USB_ID_sectors.jpg){ width=50% }

Our device manager still didn't connect, but, luckily, the code reported errors
cleanly enough for us to find the issue.

![Experiment 7: ResourceManager Connection Issue](./experiment_7_images/USB_ID_fix.jpg){ width=50% }

The device manager tried to connect to certain devices more than once; an issue
with this function, which was fixed with two conditional statements:

```py
def _find_by_idn(self, resources, keyword):
        """Select wavegen and scope by keyword."""
        print(f"[DeviceManager]: Selecting {keyword} instruments:")

        for resource in resources:
            # SKIP already opened/assigned devices to prevent "Resource busy"
            if self.scope is not None and self.scope.resource_name == resource:
                continue
            if self.wavegen is not None and self.wavegen.resource_name == resource:
                continue

            try:
                inst = self.rm.open_resource(resource)
                idn = inst.query("*IDN?")
                if keyword.upper() in idn.upper():
                    print(f"-> Selected resource: {resource}")
                    print(f"-> IDN: {idn.strip()}")
                    return inst
                else:
                    inst.close()
            except Exception as e:
                # LOG and CONTINUE instead of returning False immediately
                print(f"[DeviceManager]: Skipping {resource}: {e}")
                continue

        print(f"[DeviceManager]: No device found matching '{keyword}'")
        return None
```

The program still could not connect to the devices. Upon further testing, a
serial output was being found by PyVISA and when the program tried to open the
resource to send commands for configuration and prep to record voltages, it
threw an error:

![Experiment 7: Identification of USB Connection Issue (Serial Output)](./experiment_7_images/USB_ID_debug.jpg){ width=50% }

This was fixed by modifying the code to only return USB outputs:

```py
# Filters out 'ASRL/dev/ttyS0::INSTR' serial issue
resources = self.rm.list_resources("USB?*::INSTR")
```

The device was fully functional at this point and could be auto-calibrated to any object in real-time:

![Experiment 7: Live Data Log ](./experiment_7_images/live_data.jpg){ width=50% }

![Experiment 7: 16 Section Probability Visualizer](./experiment_7_images/visualizer.jpg){ width=50% }

![Experiment 7: Test Rig with Standardized Objects](./experiment_7_images/test_rig.jpg){ width=50% }

![Experiment 7: Improved Clips for Test Rig](./experiment_7_images/Test_Rig_Improved_Clips.jpg){ width=50% }

\newpage

# Conclusion

When developing this system, the most significant skills we developed were
centered on electrical measurement, signal integrity, and hardware--software
integration. A major challenge throughout the project was managing noise in the
acquired signals. This was primarily mitigated though improving electrical
connections between components, and using solder to create custom connectors.
Using multiplexers (MUX) to switch between electrode pairs introduced additional
complexity, requiring research into datasheets and GPIO connections on the
Raspberry Pi. Experience with oscilloscopes and digital multimeters was helpful
in determining how best to use the equipment. We also learned to use PyVISA to
communicate with these instruments. On the data side, we gained significant
insight into how to implement various machine learning models, and the ability
to display the results of these models in real time using Matplotlib. The last
major improvement in intuition was how current flows through a medium of water,
and an understanding of the way objects within that path affect the flow of
current to alter the voltage difference in the electrodes that allow this entire
system to work. Overall we each gained a greater understanding of electric
fields, hardware-software interfacing and machine learning algorithms.

## Possible Hardware Improvements

When testing the EIT device at a higher sampling rate the largest issue with
keeping accurate measurements was noise. We believe this is primarily due to the
length and number of connections between the electrodes and the measurement
devices. Movement within the water also was shown to increase noise, but it is
more difficult to correct. If we were to do this device again with more time we
would create a custom PCB and wiring scheme to reduce connections length. We
would also add a band pass filter and a capacitor to smooth out the signal to
the oscilloscope. The other significant flaw in our current version is the
reliance on a voltage source instead of a current source. To improve this, we
would attach a large (100k ohms) resistor in series with the voltage source to
keep the current consistent even if the impedance changes. We might even create
a more advanced dedicated current source that can deliver consistent current
without significant power loss over high impedances.

Framerate is restricted by the speed of the measurement device, however if we
had access to an oscilloscope with a faster measurement we could improve it. It
also may be limited by the speed in which data is transmitted to the Pi.
Additional improvements consist of increasing the number of electrodes. In this
project we were limited by the number of MUXs and complexity. Increasing the
number of electrodes would increase the number of measurements possible, which
would also enable us to reduce the noise by increasing measurements. This
reduction in noise will also help increase the separability in measurements,
leading to detection of smaller objects.

## Possible Software Improvements

The software for this project was significantly more polished and complete than
the hardware, but could still benefit from some improvements. Some of these
possible improvements are laid out in the GitHub repo in `todo.txt`. Mainly, the
code logging needs to be done properly using Python libraries instead of
`print()` to ensure logs can be saved are reread at a later date. The
configuration variables (like the voltage of the wavegen, or the IDN string of
the voltmeter) are all currently hardcoded as Python constants. A better system
would employ `config.yaml` to configure the entire program from one file. The
`requirements.txt` file is also incomplete and not reproducible. Some of the
Python files in `src` are also used separately from `main.py` for CURC figures
and testing, and should be moved and path variables changed. Type hints also
need to be added, and the documentation of the code could be improved. The
project also needs to be properly packaged, so it can be downloaded to any
Raspberry Pi easily. The CLI interface and GUI also need to be combined and
improved for user experience.

\newpage

# Appendix

![Hardware Documentation](./whiteboard_5_hardware_details.jpg){ width=50% }

![Poster Design 1](./whiteboard_1.jpg){ width=50% }

![Poster Design 2](./whiteboard_3.jpg){ width=50% }

![Data Collection Method for CURC and Calcuations](./whiteboard_4.jpg){ width=50% }

![Early 16 Sector Display using Matplotlib](./first_16_sector_display.jpg){ width=50% }

## Original Tables

| Bill of Materials                                         |                      |
| --------------------------------------------------------- | :------------------- |
| Keysight digital multimeter (34470A)                      | C105                 |
| Agilent waveform generator (33600A)                       | C105                 |
| (16 + 2 + 2 + 4) x Banana-to-hook/hook-to-plug test leads | C105                 |
| 2 x MUX36D04EVM-PDK                                       | Borrowed, EIR Mentor |
| 4 x stainless steel electrodes                            | Given for Free       |
| Raspberry Pi 3B                                           | Borrowed, Friend     |
| 3D printed test rig, OHR, and other plastic apparatus     | I2P Lab, Free        |
| Water                                                     | Free                 |

| Deadlines             |                                                                                                                                  |
| --------------------- | :------------------------------------------------------------------------------------------------------------------------------- |
| Week 2                | Advanced proof of concept, test rig, device requirements.                                                                        |
| Week 3-4              | Hard-/software requirements, order DEMUXs, pseudo-code manual algorithm, AC power supply, digital multimeter.                    |
| Week 5                | Manual MUX, manual algorithm (PyVISA).                                                                                           |
| Week 6 (Mid-report)   | Implement microcontroller, microcontroller program, computer real-time visualization algorithm.                                  |
| Week 7 (Spring Break) | Break\! No catch up needed\!                                                                                                     |
| Week 8                | Fix algorithm to correctly identify location, speed up voltage measurements (from \>1 s to <5 ms), improve wiring and apparatus. |
| Week 9                | Complete system integration, debugging (device complete).                                                                        |
| Week 10               | Improve speed of microcontroller, DEMUX, visualizer.                                                                             |
| Week 11               | Finalize demo presentation and project report.                                                                                   |
| Week 12 (Demo)        | Catch-up week.                                                                                                                   |

| Goals   |                                                                                                                                                                                                 |
| ------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Must    | Test rig, 4 electrode network, independent AC power supply, digital voltmeter, DEMUX to switch configurations (30 Hz), Python visualizer (4 pixel display), microcontroller system integration. |
| Want    | Higher speed configuration switching (~360 Hz), faster Python/C visualizer, custom AC power supply, full lumped element model solver.                                                          |
| Great   | More electrodes (5), bigger test rig, full BVP solver.                                                                                                                                          |
| Miracle | Even more electrodes, more DEMUXs, organic tests (arteries, veins, trachea). Full EIT with lung test (impossible).                                                                              |

## Acknowledgments

Chuck Duey, Dr. Elaine Linde, Dr. Jennifer Mueller, Dr. Diego Krapf, Prof.
Olivera Notaros, Alaa Jallad, Nicholas Green, and Jennifer Kreinbrink.

