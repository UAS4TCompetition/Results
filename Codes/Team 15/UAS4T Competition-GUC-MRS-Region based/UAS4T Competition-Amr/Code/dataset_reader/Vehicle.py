from __future__ import division
from pyproj import Proj
import numpy as np
import math
class Vehicle:
    def __init__(self, vehicle_data):
        '''
        Class Vehicle takes a line from the dataset and extracts vehicle information intp variables
        '''
        # Obtaining vehicle ID
        self.track_id = int(vehicle_data[0].strip())
        # Obtaining vehicle type
        self.type = vehicle_data[1].strip()
        # Obtaining traveled distance
        self.traveled_distance = float(vehicle_data[2].strip())
        # Obtaining average speed
        self.average_speed = float(vehicle_data[3].strip())
        # Number of vehicle trajectory points
        self.traj_len = (len(vehicle_data)-4)//6
        # Initializing gps path
        self.gps_path = np.zeros((self.traj_len, 2))
        # Initializing speed trajectory
        self.speed_trajectory = np.zeros(shape=self.traj_len)
        # Initializing loongitudinal and lateral accelerations trajectories
        self.long_accel, self.lat_accel = np.zeros(shape=self.traj_len), np.zeros(shape=self.traj_len)
        # Obtaining minimum and maximum timestamps of the vehicle
        self.min_time = float(vehicle_data[9].strip())
        self.max_time = float(vehicle_data[-2].strip())
        
        # Specifying vehicle width (Estimate)
        # Tolerant width
        # self.vehicle_width_list = {'Car':2.0, 'Taxi':2.0, 'Bus':2.2, \
        #  'MediumVehicle':2.2, 'HeavyVehicle':2.4, 'Motorcycle':1.0}

        # Conservative width
        self.vehicle_width_list = {'Car':1.4, 'Taxi':1.4, 'Bus':1.4, \
         'MediumVehicle':1.4, 'HeavyVehicle':1.4, 'Motorcycle':1.0}
        self.vehicle_width = self.vehicle_width_list[self.type]

        # Obtaining position, speed and accelerations of the vehicle from the dataset line
        for i in range(4, len(vehicle_data)-1, 6):
          c = (i-4)//6
          self.gps_path[c,0] = float(vehicle_data[i+1].strip())
          self.gps_path[c,1] = float(vehicle_data[i].strip())
          self.speed_trajectory[c] = float(vehicle_data[i+2].strip())
          self.long_accel[c] = float(vehicle_data[i+3].strip())
          self.lat_accel[c] = float(vehicle_data[i+4].strip())
          
        # Converting GPS path to UTM path
        p = Proj(proj='utm', zone=34, ellps='WGS84', preserve_units=False)
        self.utm_path = np.array(p(self.gps_path.transpose()[0], self.gps_path.transpose()[1])).transpose()
        
        # Initializing pixels path
        self.pixels_path = np.zeros_like(self.utm_path)
        
        # Initializing vehicle's region, queuing status, queue region and index
        self.region = None
        self.queuing_status = None
        self.queue_region = None
        self.queue_idx = None

    def get_lane(self, region, time, time_step):
        '''
        get_lane function return an estimate of the lane occupied by the vehicle at the cuurent time and region
        '''
        p1, p2 = region.end_line
        idx = int(round((time - self.min_time) / time_step))
        n = p2 - p1
        n /= (n[0]**2 + n[1]**2)**0.5
        f = self.utm_path[idx]-p1
        p3 = p1 + n*(f[0]*n[0]+f[1]*n[1]) 
        end_line_dist = ((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)**0.5
        dist = ((p3[0] - p1[0])**2 + (p3[1] - p1[1])**2)**0.5
        # print(self.track_id, dist, end_line_dist)
        return math.ceil((dist/end_line_dist)*self.region.num_lanes)
