from __future__ import division
import numpy as np
from pyproj import Proj
from shapely.geometry import LineString, Polygon

class Area:
   def __init__(self, id, points_list, traffic_signs_idx, right_offset, left_offset, lanes_list):
      '''
      Class Area is defined by an ID, a list GPS points of the desired area, indices of the traffic signals, 
      right and left offsets and the number of lanes of each line connecting each two consecutive GPS points
      '''
      # Assining ID to the Area
      self.id = id
      # Converting GPS coordinates to UTM coordinates
      p = Proj(proj='utm', zone=34, ellps='WGS84', preserve_units=False)
      utm_points = [None]*len(points_list)
      for idx, point in enumerate(points_list):
         utm_points[idx] = p(point[0], point[1])

      # Creating lines from given points and their right and left offsets
      center_line = LineString(utm_points)
      right_line = center_line.parallel_offset(right_offset, 'right', join_style=2).coords[:]
      left_line = center_line.parallel_offset(left_offset, 'left', join_style=2).coords[:]

      # Generating area polygon
      self.polygon = Polygon(right_line + left_line)
      self.polygon_pixels = []
      
      # Obtaining bounding box of the generated polygon
      x, y = list(zip(*self.polygon.exterior.coords))
      self.bbox = [min(x), max(x), min(y), max(y)]
      
      # Dividing area into regions = number of given points -1
      self.regions = [None]*(len(utm_points)-1)
      start_line = [self.polygon.exterior.coords[len(utm_points)-1], self.polygon.exterior.coords[len(utm_points)]] 
      for i in range(len(self.regions)):          
         center_line = LineString([utm_points[i], utm_points[i+1]])
         right_line = center_line.parallel_offset(right_offset, 'right', join_style=2).coords[:]
         left_line = center_line.parallel_offset(left_offset, 'left', join_style=2).coords[:]
         normal_line = np.array([right_line[0], left_line[-1]])
         end_point = utm_points[i+1]
         traffic_sign = True if i+1 in traffic_signs_idx else False
         self.regions[i] = Region(self, i, start_line, normal_line, end_point, lanes_list[i], traffic_sign)
         start_line = normal_line
      self.regions.reverse()

      # Initializing maximum queue and maximum queue time and region of the area
      self.max_queue = []
      self.max_queue_time = 0.0
      self.max_queue_region = None

   def update_max_queue(self, current_time):
      '''
      update_max_queue function updates the maximum queue and maximum queue time and region of the area at the given current_time

      '''
      for region in self.regions:
         if region.queue_list:
            queue = max(region.queue_list, key=len)
            if len(self.max_queue) <= len(queue):
               self.max_queue = queue.copy()
               self.max_queue_time = current_time
               self.max_queue_region = region

class Region:
   def __init__(self, parent, id, start_line, end_line, end_point, num_lanes, traffic_sign):
      '''
      Class Region is a subclass from the area. The region is the rectangle defined by each two consecutive GPS points, the right and left offset.
      '''
      self.area = parent
      self.id = id
      self.num_lanes = num_lanes
      self.vehicles = {} 
      self.queue_list = []
      # Generating region polygon
      self.polygon = Polygon([end_line[0], start_line[0], start_line[1], end_line[1]])
      self.start_line =  start_line
      self.end_line =  end_line
      self.start_line_pixels, self.end_line_pixels = None, None
      self.end_point = end_point
      self.traffic_sign = traffic_sign
      self.spillbacks = []
