# import math
# import numpy

from saleae.range_measurements import DigitalMeasurer
import numpy as np
import csv

class MyDigitalMeasurer(DigitalMeasurer):
    supported_measurements = ["c_worst, c_best, c_average"]
    c_worst = None
    c_best = None
    c_average = None
    measurements = []
    c_measurements = []
    t_measurements = []
    t_complete = None
    values = {}
    p_task = []
    data = None
    processed = 0;
    # Initialize your measurement extension here
    # Each measurement object will only be used once, so feel free to do all per-measurement initialization here
    def __init__(self, requested_measurements):
        super().__init__(requested_measurements)

    # This method will be called one or more times per measurement with batches of data
    # data has the following interface
    #   * Iterate over to get transitions in the form of pairs of `Time`, Bitstate (`True` for high, `False` for low)
    # `Time` currently only allows taking a difference with another `Time`, to produce a `float` number of seconds
    def process_data(self, data):  
        if self.data is None:
            self.data = list(data)
        else:
            self.data += list(data);
        

    # This method is called after all the relevant data has been passed to `process_data`
    # It returns a dictionary of the request_measurements values
    def measure(self):
        t_l = None
        t_h = None
        times = 0;
        if len(self.data) == 0:
            return self.values
        
        for t, bit in self.data:
            # set the time to t varables
            if bit:
                t_h = t
            elif t_h is not None:
                t_l = t
        
            if t_l is not None and t_h is not None:
                self.measurements.append([t_l, t_h])
                t_l = None
                t_h = None

        num_measurements = len(self.measurements)
        if num_measurements > 0:
            self.t_measurements = np.array(self.measurements).T
            self.c_measurements = (self.t_measurements[0] - self.t_measurements[1]).astype(float)
            self.values["c_average"] = (float) (self.c_measurements.sum() / num_measurements)

            self.values["c_best"] = self.c_measurements.min()
            self.values["c_worst"] = self.c_measurements.max()
            self.values["t_complete"] = num_measurements
        
        if num_measurements > 1:
            self.values["p_average"] = np.diff(self.t_measurements[0]).sum()/(num_measurements-1)
            self.values["c_std"] = self.c_measurements.std()


        # # open the file in the write mode
        # with open('output.csv', 'w') as f:
        #     # create the csv writer
        #     writer = csv.DictWriter(f,fieldnames=self.values.keys)
        #     # write a row to the csv file
        #     writer.writeheader()
        #     writer.writerow(self.values)

        return self.values

