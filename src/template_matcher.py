import cv2
import numpy as np
import math

class TemplateMatcher:
    # Define all available template matching methods
    METHODS = {
        'TM_CCOEFF': cv2.TM_CCOEFF,
        'TM_CCOEFF_NORMED': cv2.TM_CCOEFF_NORMED,
        'TM_CCORR': cv2.TM_CCORR,
        'TM_CCORR_NORMED': cv2.TM_CCORR_NORMED,
        'TM_SQDIFF': cv2.TM_SQDIFF,
        'TM_SQDIFF_NORMED': cv2.TM_SQDIFF_NORMED
    }
    
    def __init__(self, template_path, methods=None, threshold=0.8, distance_pixels_threshold=50):
        self.template = self.load_template(template_path)
        self.template_h, self.template_w = self.template.shape
        self.threshold = threshold
        self.distance_threshold = distance_pixels_threshold
        
        # Use specified methods or all methods if none provided
        self.methods = methods if methods else list(self.METHODS.keys())
        
    def load_template(self, template_path):
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            raise FileNotFoundError(f"Could not load template: {template_path}")
        return template

    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points."""
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

    def match_template(self, screenshot_path):
        # Can accept either a path or a pre-loaded image
        if isinstance(screenshot_path, str):
            screenshot = cv2.imread(screenshot_path, cv2.IMREAD_GRAYSCALE)
            if screenshot is None:
                raise FileNotFoundError(f"Could not load screenshot: {screenshot_path}")
        else:
            screenshot = cv2.cvtColor(screenshot_path, cv2.COLOR_BGR2GRAY)
        
        # Store results for all methods
        match_results = {}
        threshold_failures = []
        
        # First pass: Get match results and check threshold for each method
        for method_name in self.methods:
            method = self.METHODS.get(method_name)
            result = cv2.matchTemplate(screenshot, self.template, method)
            
            # For SQDIFF methods, the best match is the minimum value
            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                match_value = 1.0 - min_val if method == cv2.TM_SQDIFF_NORMED else -min_val
                match_location = min_loc
            else:
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                match_value = max_val
                match_location = max_loc
            
            # Store result for this method
            match_results[method_name] = {
                'value': match_value,
                'location': match_location
            }
            
            # For normed methods, check threshold
            if 'NORMED' in method_name and match_value < self.threshold:
                threshold_failures.append(method_name)
        
        # Second pass: Check distances between all matches and track agreeing methods
        distance_failures = []
        method_names = [m for m in match_results.keys()]
        
        # Track which methods have close matches with other methods
        agreeing_methods = {method: set() for method in method_names}
        
        for i in range(len(method_names)):
            for j in range(i+1, len(method_names)):
                method1 = method_names[i]
                method2 = method_names[j]
                
                loc1 = match_results[method1]['location']
                loc2 = match_results[method2]['location']
                
                # Calculate distance between match locations
                distance = self.calculate_distance(loc1, loc2)
                
                # Store distance in results for visualization
                match_results[method1]['distance_to_' + method2] = distance
                match_results[method2]['distance_to_' + method1] = distance
                
                # Check if distance is within threshold
                if distance <= self.distance_threshold:
                    # These methods agree with each other
                    agreeing_methods[method1].add(method2)
                    agreeing_methods[method2].add(method1)
                else:
                    distance_failures.append((method1, method2, distance))
        
        # Count methods that have at least one agreement with another method
        agreeing_method_count = sum(1 for method, agreements in agreeing_methods.items() if len(agreements) > 0)
        
        # Determine match status - need at least two methods in agreement
        if threshold_failures:
            match_status = f"MATCH NOT FOUND - Methods below threshold: {', '.join(threshold_failures)}"
            best_match = None
        elif agreeing_method_count < 2:
            # Not enough methods agree with each other
            close_pairs = [f"{m1}-{m2}" for m1, agreements in agreeing_methods.items() for m2 in agreements if m1 < m2]
            if close_pairs:
                match_status = f"MATCH NOT FOUND - Only {agreeing_method_count} methods in agreement: {', '.join(close_pairs)}"
            else:
                match_status = f"MATCH NOT FOUND - No methods agree with each other"
            best_match = None
        else:
            match_status = f"MATCH FOUND - {agreeing_method_count} methods in agreement"
            
            # Find the best match among agreeing methods
            best_value = -float('inf')
            best_method = None
            
            # Get the methods that have the most agreements
            most_agreeing = max(agreeing_methods.items(), key=lambda x: len(x[1]))[0]
            agreeing_set = {most_agreeing} | agreeing_methods[most_agreeing]
            
            for method_name in agreeing_set:
                result = match_results[method_name]
                if result['value'] > best_value:
                    best_value = result['value']
                    best_method = method_name
                    loc = result['location']
                    best_match = (loc[0], loc[1], self.template_w, self.template_h)
        
        # Add match status to results
        match_results['match_status'] = match_status
        match_results['threshold'] = self.threshold
        match_results['distance_pixels_threshold'] = self.distance_threshold
        match_results['agreeing_methods'] = agreeing_methods
            
        return best_match, match_results