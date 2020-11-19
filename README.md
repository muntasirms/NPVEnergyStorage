# NPVEnergyStorage - Energy Storage TEA Tool

## Table of Contents

* [Introduction](#introduction)
* [Technologies](#technologies)
* [Setup and Use](#setup-and-use)
* [Next Steps](#next-steps)


## Introduction

This project serves as a tool for quickly performing techno-economic analyses for energy storage technologies. 
Profit revolves around using the energy storage technology for "peak shaving", while accounting for losses over time or during conversion. Economic viability is determined using
a discounted cash flow model under customizable conditions, currently developing net present value as a key metric.

This project is unique in that it uses Monte Carlo simulations to account for uncertainty in day to day real time electricity market fluctuations and in storage period.
To that end, rather than giving a point estimate value for a key variable of interest, a distribution of possible values and their likelihoods is produced. 

Currently, the model returns P5 and P95 values of the plant's net present value (NPV) as well as a kernel density estimate of the distribution of NPVs.


## Technologies

* Python 3.6
* matplotlib 3.3.3
* numpy 1.19.4
* seaborn 0.11.0


## Setup and Use

All parameters are filled in with default values associated with price fluctuations observed from the New England ISO (https://www.iso-ne.com/), normalized for delivery costs
and other nominal charges beyond wholesale pricing. The default values are approximately representative of a 250 MWh pumped water or compressed air storage. 

Parameters are broken up into the following categories:
* Electricity Pricing Parameters
  * These are parameters associated with the randomized peak and trough electricity pricing, as well as the simulated storage time (to account for losses over time for, say, thermal storage)

* Storage Technology Parameters
  * Parameters associated with the specific energy storage technology under analysis. This is where values like capacity, efficiency, and heat/energy recycling can be adjusted.

* Simulation Parameters
  * Parameters regarding the plant life (simulated years), as well as the number of simulations run can be adjusted here. More simulations increase accuracy at the cost of computing power and simulation time.

* Economic Parameters
  * Initial investment cost parameters, loan periods, equity, loan rates, internal rate of return, and depreciation rates can be adjusted here. Operating cost parameters are a subcategory of this.

## Next Steps

Planning on adding a GUI for ease of access to variables and user friendliness. Also looking to format the graphs so they arent default matplotlib graphs.
