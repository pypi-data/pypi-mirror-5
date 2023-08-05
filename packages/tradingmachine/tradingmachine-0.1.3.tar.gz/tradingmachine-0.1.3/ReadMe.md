TradingMachine
=======

TradingMachine is intend to bring optimization and machine techniques into finance algorithmic trading.

Discussion and Help
===================

TODO

Features
========

* Optimization on strategy parameters.
* PyBrain Integration (Reinforcement Learning, Neural Network ...).
* TA-Lib Integration (Most common technical analysis available.)
* Pandas (High speed time series data analysis)


Installation
============

# You will first need to install TALib. ta-lib is a python wrapper for that. Please refer [TA-Lib](http://ta-lib.org/hdr_doc.html)

TradingMachine can be installed via pip

```
pip install numpy
pip install matplotlib
pip install pandas
pip install ta-lib		
pip install tradingmachine
```

If there are problems installing the dependencies, please consider install scipy stack.
For Windows, the [Enthought Python Distribution](http://www.enthought.com/products/epd.php)
includes most of the necessary dependencies. 
On OSX, the [Scipy Superpack](http://fonnesbeck.github.com/ScipySuperpack/) works very well.
Other platforms, the [Scipy Stack](http://www.lfd.uci.edu/~gohlke/pythonlibs/) has binary available to install.

After installation, you will need to create a configuration file in home directory named ".tmconfig.ini".

Example:
```
  1 [DEFAULT]
  2 HistoricalDataPath = /Users/chen/Repository/historicaldata
```

Dependencies
------------

* Python (>= 3.3.1)
* numpy (>= 1.7.1)
* pandas (>= 0.11.0)
* pytz
* ta-lib

Contact
=======

For other questions, please contact Chen Huang <chinux@gmail.com>.
