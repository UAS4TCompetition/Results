from __future__ import division
from dataset_reader.Vehicle import Vehicle
from tqdm import tqdm
from colorama import Fore
import numpy as np

class DatasetReader:
    def __init__(self, file_path):
      '''
      DatasetReader Class reads the CSV file of the dataset and extracts its lines into vehicle objects
      '''
      try:
        reader = open(file_path)
        dataset = reader.readlines()
        del dataset[0]
        self.vehicles_list = {}        
        self.max_time = 0.0
        pbar = tqdm(dataset, bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.RED, Fore.RESET))
        pbar.set_description("Reading Dataset")
        for vehicle_data in pbar:
          vehicle_data = vehicle_data.replace(" ","").replace("\n","").split(';')
          vehicle = Vehicle(vehicle_data)
          self.max_time = vehicle.max_time if vehicle.max_time > self.max_time else self.max_time
          self.vehicles_list[vehicle.track_id] = vehicle
      except Exception as e:
        print (e)
        exit()
     
'''
min_lat =  37.989523
max_lat =  37.99281
min_long =  23.730278
max_long =  23.736517
'''
