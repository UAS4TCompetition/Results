from __future__ import division
import numpy as np
import os, pygame, time

class Display:
   def __init__(self, parent):
      '''
      Display Class is a class for visualizing the vehiles in the specefied regions and their queuing status; member, head or not in queue 
      '''
      # Initiating pygame
      pygame.init()
      pygame.font.init()
      pygame.display.set_caption("UAS4T Competition")
      self.engine = parent

      # Obtaining bounding box of the whole scene
      self.utm_bbox = self.engine.areas_bbox
      self.full_screen = False
      self.resolution = [1280, 720]
      self.screen = pygame.display.set_mode(self.resolution)
      self.screen.fill((0,0,0))
      
      # Specefying a color for each queue to be distinct
      self.queues_color_code = [(255, 0, 0), (255,255,0), (0,234,255), (170,0,255), 
                                 (255,127,0), (191,255,0), (0,149,255), (255,0,170), 
                                 (255,212,0), (106,255,0), (0,64,255), (237,185,185)]

      # converting areas from utm coordinates to pixel coordinates
      self.areas_to_pixels(self.engine.areas)
      
      # converting vehicle's paths from utm coordinates to pixel coordinates
      for vehicle in self.engine.vehicles_list.values():
         vehicle.pixels_path = np.array(self.utm_to_pixels(vehicle.utm_path))

   def __del__(self):
      '''
      A destructor that closes pygame
      '''
      pygame.quit()

   def utm_to_pixels(self, utm_point):
      '''
      utm_to_pixels function converts the given utm point or path to a point or a path of pixels
      '''
      utm_point = np.array(utm_point).transpose()
      width, height = self.resolution
      min_x, min_y, max_x, max_y = self.utm_bbox
      pixel_x = (width - (width*(max_x-utm_point[0]))/(max_x-min_x)).astype(int)
      pixel_y = (height - (height*(min_y-utm_point[1]))/(min_y - max_y)).astype(int)
      return np.array([pixel_x, pixel_y]).transpose()

   def areas_to_pixels(self, utm_areas):
      '''
      areas_to_pixels function converts the given utm area to pixel coordinates
      '''
      self.pygame_rects = []
      for area in utm_areas:
         self.pygame_rects.append(pygame.Rect(area.bbox[0], area.bbox[3], area.bbox[1]-area.bbox[0], area.bbox[3]-area.bbox[2]))
         area.polygon_pixels = self.utm_to_pixels(np.array(area.polygon.exterior.coords[:]))
         for region in area.regions:
            region.end_line_pixels = self.utm_to_pixels(region.end_line) 

   def update(self):
      '''
      update function updates the pygame scene at each timestamp and returns False if the user closes the pygame window
      '''
      for event in pygame.event.get():
         if event.type == pygame.QUIT:
            return False      

      for area in self.engine.areas:
         if area.id == 'red':
            area_color = (255,0,0)
         elif area.id == 'yellow':
            area_color = (255,255,0)
         elif area.id == 'green':
            area_color = (0,255,0)
         pygame.draw.polygon(self.screen, area_color, area.polygon_pixels, 2)
         for region in area.regions:
            pygame.draw.line(self.screen, (0, 255, 0), region.end_line_pixels[0], region.end_line_pixels[1], 2)
      pygame.display.flip()
      self.screen.fill((0,0,0))
      return True
