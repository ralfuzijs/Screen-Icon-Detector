import cv2
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
import matplotlib

def display_results(screenshot, match_coordinates, match_results=None, template_name=None, monitor=None):
    # Create a copy of the screenshot to avoid modifying the original
    img = screenshot.copy()
    
    # Define colors for each method (BGR for OpenCV and RGB for matplotlib)
    method_colors = {
        'TM_CCOEFF': ((255, 0, 0), 'red'),         # Blue in OpenCV, Red in matplotlib
        'TM_CCOEFF_NORMED': ((0, 0, 255), 'blue'), # Red in OpenCV, Blue in matplotlib
        'TM_CCORR': ((0, 255, 0), 'green'),        # Green in both
        'TM_CCORR_NORMED': ((255, 0, 255), 'magenta'), # Magenta in both
        'TM_SQDIFF': ((255, 255, 0), 'cyan'),      # Cyan in OpenCV, Yellow in matplotlib
        'TM_SQDIFF_NORMED': ((0, 255, 255), 'yellow') # Yellow in OpenCV, Cyan in matplotlib
    }
    
    # Get match status from results
    match_status = match_results.get('match_status', "No match status") if match_results else "No match results"
    
    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
    
    # First subplot: Display the image with match
    if match_coordinates:  # Check if a best match was found
        # Draw a rectangle around the best matched template (thicker border)
        x, y, w, h = match_coordinates
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)  # Thick green rectangle for best match
    
    # Define metadata fields to exclude from visualization
    metadata_fields = ['match_status', 'threshold', 'distance_threshold', 'distance_pixels_threshold', 'agreeing_methods']
    
    # Draw rectangles for each method's match
    if match_results:
        for method_name, result in match_results.items():
            if method_name not in metadata_fields and method_name in method_colors:
                # Get method color
                cv_color = method_colors[method_name][0]
                
                # Get match location
                if 'location' in result:
                    loc_x, loc_y = result['location']
                    
                    # Draw a thinner rectangle for each method's match
                    w = h = 0
                    if match_coordinates:
                        _, _, w, h = match_coordinates
                    else:
                        w, h = 100, 100  # Default size if no match coordinates
                        
                    cv2.rectangle(img, 
                                (loc_x, loc_y), 
                                (loc_x + w, loc_y + h), 
                                cv_color, 1)
                    
                    # Add method name as text near the rectangle
                    cv2.putText(img, method_name, (loc_x, loc_y - 5), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, cv_color, 1)
                    
                    # Draw lines between matches to show distances
                    for other_method, other_result in match_results.items():
                        if (other_method not in metadata_fields and 
                            other_method != method_name and 
                            isinstance(other_result, dict) and 'location' in other_result):
                            
                            distance_key = f'distance_to_{other_method}'
                            if distance_key in result:
                                other_x, other_y = other_result['location']
                                # Draw a line between match centers
                                center1 = (loc_x + w//2, loc_y + h//2)
                                center2 = (other_x + w//2, other_y + h//2)
                                
                                cv2.line(img, center1, center2, cv_color, 1)
                                
                                # Add distance text at midpoint
                                mid_x = (center1[0] + center2[0]) // 2
                                mid_y = (center1[1] + center2[1]) // 2
                                cv2.putText(img, f"{result[distance_key]:.1f}px", 
                                            (mid_x, mid_y), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 
                                            0.5, cv_color, 1)

    # Convert BGR to RGB for matplotlib
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Display the image with the matched template
    ax1.imshow(img_rgb)
    ax1.set_title(f"Template: {template_name or 'Unknown'}\n{match_status}")
    ax1.axis('off')  # Hide axes
    
    # Second subplot: Bar chart of match values if results are provided
    if match_results:
        methods = [m for m in match_results.keys() if m not in metadata_fields]
        values = [match_results[m]['value'] for m in methods]
        
        # Create bar chart with method-specific colors
        bars = []
        for i, method in enumerate(methods):
            plt_color = method_colors.get(method, ('skyblue', 'skyblue'))[1]
            bar = ax2.bar(method, values[i], color=plt_color)
            bars.extend(bar)
        
        ax2.set_title('Match Values by Method')
        ax2.set_ylabel('Match Value')
        ax2.set_xlabel('Template Matching Method')
        ax2.tick_params(axis='x', rotation=45)
        
        # Add threshold line
        threshold = match_results.get('threshold', 0.8)
        ax2.axhline(y=threshold, color='r', linestyle='-', label=f'Threshold ({threshold})')
        
        # Highlight the best match
        if match_coordinates:
            best_index = values.index(max(values))
            bars[best_index].set_edgecolor('black')
            bars[best_index].set_linewidth(2)
            
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax2.annotate(f'{height:.3f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8)
    
    # Add a legend to explain the colors
    if match_results:
        legend_elements = []
        for method, (_, plt_color) in method_colors.items():
            if method in methods:
                legend_elements.append(plt.Line2D([0], [0], color=plt_color, lw=4, label=method))
        
        # Add threshold to legend
        legend_elements.append(plt.Line2D([0], [0], color='r', lw=2, linestyle='-', label=f'Threshold ({threshold})'))
        
        # Add legend to the right of the second subplot
        ax2.legend(handles=legend_elements, title="Methods", 
                  bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    
    # Position the matplotlib window on the selected monitor if provided
    if monitor:
        try:
            # Get the figure manager
            fig_manager = plt.get_current_fig_manager()
            
            # Different backends have different ways to set window position
            backend = matplotlib.get_backend().lower()
            
            if 'tk' in backend:  # Tkinter backend
                fig_manager.window.wm_geometry(f"+{monitor['left']+50}+{monitor['top']+50}")
            elif 'qt' in backend:  # Qt backend
                fig_manager.window.move(monitor['left'] + 50, monitor['top'] + 50)
            elif 'wx' in backend:  # WxPython backend
                fig_manager.window.SetPosition((monitor['left'] + 50, monitor['top'] + 50))
            elif 'gtk' in backend:  # GTK backend
                fig_manager.window.move(monitor['left'] + 50, monitor['top'] + 50)
            
            print(f"Positioned visualization window on selected monitor at ({monitor['left']+50}, {monitor['top']+50})")
        except Exception as e:
            print(f"Error positioning visualization window: {e}")
    
    plt.show()