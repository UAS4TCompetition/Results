from __future__ import division
from dataset_reader.DatasetReader import DatasetReader
import numpy as np
import os, pygame, time, math
from shapely.vectorized import contains
from tqdm import tqdm
from colorama import Fore
from display import Display
from area import Area

class Engine:
   def __init__(self, gui=False):
      # Setting Time Step as shown in the dataset (0.04)
      self.time_step = 0.04
      # Obtaining dataset path
      dataset_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/dataset/competition_dataset.csv'
      # Reading the competition dataset
      self.dataset_reader = DatasetReader(dataset_path)
      # Obtaining the list of vehicles from the dataset
      self.vehicles_list = self.dataset_reader.vehicles_list
      # Obtaining the maximum time of the dataset
      self.max_time = self.dataset_reader.max_time

      # Defining the areas of interest as specified in the competition requirements
      self.areas = []
      #-------------------- Yellow Area --------------------#
      yellow_area = [[23.7312353, 37.9911296], [23.7312873, 37.9913327], [23.7315771, 37.9914456], [23.7319317, 37.9915806], [23.73207915, 37.991558049999995]]
      # Creating area object
      self.areas.append(Area('yellow', yellow_area, [2,4], right_offset=5, left_offset=7.5, lanes_list=[2]*5))

      #-------------------- Green Area --------------------#
      green_area = [[23.7315183, 37.9928708], [23.7312909, 37.9919591]]
      # Creating area object
      self.areas.append(Area('green', green_area, [1], right_offset=6, left_offset=7, lanes_list=[2]*2))

      #-------------------- Red Area --------------------#
      red_area = [[23.7358687, 37.9910762],[23.7341569, 37.9913435],[23.7324048, 37.9916150],[23.7314991, 37.9917534]]
      # Creating area object
      self.areas.append(Area('red', red_area, [1,2,3], right_offset=11, left_offset=4.2, lanes_list=[3]*4))

      # Obtaining the bounding box of the selected areas
      min_lat_list, max_lat_list = np.zeros(shape=len(self.areas)), np.zeros(shape=len(self.areas))
      min_lon_list, max_lon_list = np.zeros(shape=len(self.areas)), np.zeros(shape=len(self.areas))
      for region_idx, region in enumerate(self.areas):
         min_lon_list[region_idx] = region.bbox[0]        
         max_lon_list[region_idx] = region.bbox[1]
         min_lat_list[region_idx] = region.bbox[2]     
         max_lat_list[region_idx] = region.bbox[3]
      self.areas_bbox = [np.min(min_lon_list), np.min(min_lat_list), np.max(max_lon_list), np.max(max_lat_list)]
      
      # Creating a GUI object to display the vehicles in their areas
      self.gui = Display(self) if gui else None
      
      # Setting a tolerance for the trffic line
      self.end_line_tolerance = 18

   def add_to_queue(self, region, current_vehicle, preceding_queue_idx):
      '''
      add_to_queue function adds a specific vehicle to a specific queue at a specific region (sub-area) at a predefined timestamp (as a member)
      '''
      region.queue_list[preceding_queue_idx].append(current_vehicle.track_id)
      current_vehicle.queuing_status = 'Member'
      current_vehicle.queue_region = region
      current_vehicle.queue_idx = preceding_queue_idx

   def remove_from_queue(self, current_vehicle):
      '''
      remove_from_queue function removes a specific vehicle from its assigned queue
      '''
      region = current_vehicle.queue_region
      if current_vehicle.track_id in region.queue_list[current_vehicle.queue_idx]:
         current_vehicle.queue_region = None
         current_vehicle.queuing_status = None
         region.queue_list[current_vehicle.queue_idx].remove(current_vehicle.track_id)
         if not region.queue_list[current_vehicle.queue_idx]:
            for queue in region.queue_list[current_vehicle.queue_idx+1:]:
               for queue_member_id in queue:
                  self.vehicles_list[queue_member_id].queue_idx -= 1
            del region.queue_list[current_vehicle.queue_idx]
         current_vehicle.queue_idx = None

   def get_preceding_vehicle(self, region, current_vehicle, t_idx):
      '''
      get_preceding_vehicle function returns the very preceding vehicle, if exists, of the given vehicle
      '''
      if not region.vehicles.get(t_idx):
         return
      idx = t_idx - int(round(current_vehicle.min_time / self.time_step))
      p2 = current_vehicle.utm_path[idx]
      n = region.end_line[1] - region.end_line[0]
      n /= (n[0]**2 + n[1]**2)**0.5
      f = p2-region.end_line[0]
      p1 = region.end_line[0] + n*(f[0]*n[0]+f[1]*n[1]) 
      final_idx = region.vehicles[t_idx].index(current_vehicle.track_id) if current_vehicle.track_id in region.vehicles[t_idx] else None
      for id in reversed(region.vehicles[t_idx][0:final_idx]):
         preceding_vehicle = self.vehicles_list[id]
         idx = t_idx - int(round(preceding_vehicle.min_time / self.time_step))
         p3 = preceding_vehicle.utm_path[idx]
         lateral_distance = self.distance_to_line(p1, p2, p3)
         if abs(lateral_distance) <= self.lateral_threshold:
            return preceding_vehicle        

   def distance_to_line(self, p1, p2, p3): # p3 is the point
      '''
      distance_to_line function returns the perpendicular distance from point p3 to the line formed by points p1 and p2
      '''
      px = p2[0]-p1[0]
      py = p2[1]-p1[1]
      u =  ((p3[0] - p1[0]) * px + (p3[1] - p1[1]) * py) / (px*px + py*py)
      u = min(max(u,0),1)
      dx = p1[0] + u * px - p3[0]
      dy = p1[1] + u * py - p3[1]
      return (dx*dx + dy*dy)**0.5

   def run(self):
      '''
      run function assigns vehicles to their regions and execute the main algorithm
      '''
      max_queue = []
      max_queue_time = 0.0
      pbar = tqdm(self.vehicles_list.values(), bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Fore.RESET))
      pbar.set_description("Assigning vehicles to regions")
      
      # Assigning vehicles to their regions at each timestamp, the vehicles that don't belong to the specified areas are excluded
      for vehicle in pbar:
         for area in self.areas:
            for i, region in enumerate(area.regions):
               lista = np.where(contains(region.polygon, vehicle.utm_path.transpose()[0], vehicle.utm_path.transpose()[1]) == True)[0]
               idx = lista + int(round(vehicle.min_time/self.time_step))
               for i in idx:
                  if not region.vehicles.get(i):
                     region.vehicles[i] = []
                  region.vehicles[i].append(vehicle.track_id)

      end_line_tolerance_squared = self.end_line_tolerance**2
      max_idx = int(round(self.max_time/self.time_step))+1
      pbar = tqdm(range(0, max_idx), bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.BLACK, Fore.RESET))
      pbar.set_description("Running")
      
      # Looping over time from zero to the maximum timestamp
      for t_idx in pbar:
         for area in self.areas:
            for i, region in enumerate(area.regions):
               if not region.vehicles.get(t_idx):
                  continue
               
               # Sorting vehicles in each region in each area by distance to the stop line
               dist_list = [None] * len(region.vehicles[t_idx])
               for v_idx, id in enumerate(region.vehicles[t_idx]):
                  current_vehicle = self.vehicles_list[id]
                  idx = t_idx - int(round(current_vehicle.min_time / self.time_step))
                  dist = (region.end_point[0] - current_vehicle.utm_path[idx,0])**2 + (region.end_point[1] - current_vehicle.utm_path[idx,1])**2
                  dist_list[v_idx] = [dist, id]
               dist_list.sort()
               region.vehicles[t_idx] = list(zip(*dist_list))[1]
               queue_member_id = 0

               # Looping over vehicles in each region, from the stop line to the start line
               for id in region.vehicles[t_idx]:
                  # Fetching the vehicle object by its ID
                  current_vehicle = self.vehicles_list[id]
                  current_vehicle.region = region
                  self.lateral_threshold = (current_vehicle.vehicle_width/2.0)
                  idx = t_idx - int(round(current_vehicle.min_time / self.time_step))

                  # Executing the finite state machine on each vehicle
                  # Not in a queue?
                  if not current_vehicle.queuing_status:
                     # At Rest or Decelerating?
                     if current_vehicle.speed_trajectory[idx] == 0 or current_vehicle.long_accel[idx] < 0:
                        preceding_vehicle = self.get_preceding_vehicle(region, current_vehicle, t_idx)
                        # Preceding Vehicle?
                        if preceding_vehicle:
                           # Preceding Vehicle in Queue?
                           if preceding_vehicle.queuing_status:
                              self.add_to_queue(region, current_vehicle, preceding_vehicle.queue_idx)   
                        else:
                           # At Rest?
                           if current_vehicle.speed_trajectory[idx] == 0:
                              # Obtaining distance to stop line
                              d = ((region.end_point[0] - current_vehicle.utm_path[idx,0])**2 + (region.end_point[1] - current_vehicle.utm_path[idx,1])**2)
                              # At stop Line?
                              if d < end_line_tolerance_squared:
                                 # Assign as Queue Head
                                 region.queue_list.append([current_vehicle.track_id])
                                 current_vehicle.queuing_status = 'Head'
                                 current_vehicle.queue_region = region
                                 current_vehicle.queue_idx = len(region.queue_list)-1                        
                  # In A Queue?
                  else:
                     # Leaving The Region?
                     if (region.vehicles.get(t_idx+10) and not id in region.vehicles[t_idx+10]):
                        # Exit Queue
                        self.remove_from_queue(current_vehicle)
                     else:
                        # Obtaining the preceding vehicle
                        preceding_vehicle = self.get_preceding_vehicle(region, current_vehicle, t_idx)
                        # Preceding vehicle exists?
                        if preceding_vehicle:
                           # Preceding vehicle is in queue?
                           if preceding_vehicle.queuing_status:
                              # Preceding vehicle is in the same queue of the current vehicle?
                              if preceding_vehicle.queue_idx==current_vehicle.queue_idx:
                                 # Stay
                                 current_vehicle.queuing_status = 'Member'
                              else:
                                 # Exit Queue
                                 self.remove_from_queue(current_vehicle)
                           else:
                              # Current vehicle is at rest?
                              if current_vehicle.speed_trajectory[idx] == 0:
                                 # Assign as Queue Head
                                 current_vehicle.queuing_status = 'Head'
                                 region.queue_list[current_vehicle.queue_idx].remove(id)
                                 region.queue_list[current_vehicle.queue_idx].insert(0, id)
                              else:
                                 # Exit Queue
                                 self.remove_from_queue(current_vehicle)
                        else:
                           if current_vehicle.queuing_status == 'Member' or (current_vehicle.queuing_status == 'Head' and current_vehicle.speed_trajectory[idx] >= 3):
                              # Exit Queue
                              self.remove_from_queue(current_vehicle)
                           
                  # Visualizing vehicles, the queue members are colored, the queue head is thick, while the non-queue members are thick and white
                  if self.gui:
                     r, color = 5, (255,255,255)
                     if current_vehicle.queuing_status:
                        color = self.gui.queues_color_code[current_vehicle.queue_idx]
                        r = 3 if current_vehicle.queuing_status == 'Member' else r
                     # pygame.draw.circle(self.gui.screen, color, current_vehicle.pixels_path[idx], r)

                  # Checking Spillback
                  # Queue Head?
                  if current_vehicle.queuing_status == 'Head':
                     # At stop line?
                     if region.traffic_sign:
                        # Obtaining distance to stop line 
                        d = ((region.end_point[0] - current_vehicle.utm_path[idx,0])**2 + (region.end_point[1] - current_vehicle.utm_path[idx,1])**2)**0.5
                        if d < 10:
                           # Current region has a preceding traffic line?
                           if i > 0:
                              # Obtaining the preceding vehicle in the preceding region
                              preceding_vehicle = self.get_preceding_vehicle(area.regions[i-1], current_vehicle, t_idx)
                              # Preceding vehicle exists and in queue?
                              if preceding_vehicle and preceding_vehicle.queuing_status:
                                 p_idx = t_idx - int(round(preceding_vehicle.min_time / self.time_step))
                                 # Obtaining distance to the preceding vehicle in the preceding region
                                 distance = ((preceding_vehicle.utm_path[p_idx,0] - current_vehicle.utm_path[idx,0])**2 + (preceding_vehicle.utm_path[p_idx,1] - current_vehicle.utm_path[idx,1])**2)**0.5
                                 if distance < 8:
                                    # Making sure that the spillback is new
                                    if not(region.spillbacks and id in list(zip(*region.spillbacks))[3]):
                                       # Adding new spillback
                                       front_queue_length = area.regions[i-1].queue_list[preceding_vehicle.queue_idx]
                                       rear_queue_length = region.queue_list[current_vehicle.queue_idx]
                                       region.spillbacks.append([t_idx*0.04, area.id, region.id, id, front_queue_length+rear_queue_length])
      
            # Updating the maximum queues of each area with each timestamp
            area.update_max_queue(t_idx*0.04)

         # updating GUI
         if self.gui and not self.gui.update():
            del self.gui
            return

      # Closing GUI at the end
      if self.gui:
         del self.gui

      # Displaying results
      print('Results Report:')
      for i, area in enumerate(self.areas):
         print('   Area', i+1,':')
         print('      Color =', area.id)
         print('      Maximum Queue Length = ', len(area.max_queue))
         print('      Lane of Max Queue = ',self.vehicles_list[area.max_queue[0]].get_lane(area.max_queue_region, area.max_queue_time, self.time_step))
         print('      Coordinates of Max Queue = ', self.vehicles_list[area.max_queue[0]].gps_path[int(round(max_queue_time/0.04))], self.vehicles_list[area.max_queue[-1]].gps_path[int(round(max_queue_time/0.04))])
         print('      Time of Max Queue = ', area.max_queue_time)
         print('      Spillbacks :')
         for j, region in enumerate(area.regions):
            for k, spillback in enumerate(region.spillbacks):
               print('         Region', j+1,':')
               print('         Spillback', k+1,':')
               print('            When?', spillback[0])
               print('            Where?', spillback[1:3])
               print('            Final Queue Length?', len(spillback[4]))

         print('\n')

# main function
if __name__ == '__main__':
   e = Engine(gui=True)
   e.run()
