You should install wiresnake and python 2.7 first


Users:

1. Install autotest through

	Python setup.py install

2. Install "xlrd" module

3. Create a new file folder like "autotest"
	
   The following files should be included in this File

	a) config.conf
	b) autotest.py
	c) The Excel table
	d) Wiresnake executing script

4. Configuring "config.conf"

	If there is no change with the excel file , you just need to
	
	change Cip address and model_name which you want to test

5. Run the test

 	python autotest.py

6. Check log file
	
	After running the test, a new file called "log" will be created which including

	the result of the current test


Developers:

Setup the test widget:

1.setup virtualenv(1.91) (recommand)

2.Create seperate environment so you could make unittest and other tests under pure environment


Email: wenbin.rc@gmail.com
