import matplotlib.pyplot as plt
import numpy as np

# Set center latitude and longitude
lat_dir = 'N'
lon_dir = 'W'
lat_degree = 30
lon_degree = 60

apparent_latitude = lat_dir + str(lat_degree)

# Calculate longitude spacing based on latitude
lat_spacing = 1
lon_spacing = lat_spacing * np.cos(np.radians(lat_degree)) # ratio of longitude = cos(latitude)

# Dead reckoning
dr_lat = "N 30 12'"
dr_lon = "W 60 10'"

def plot_lat(pos, center_lat=lat_degree):
    dir = pos[0]
    if dir != 'N' and dir != 'S':
        raise ValueError(f"Invalid latitude direction {dir}")

    pos = pos[1:].strip()

    num_args = len(pos.split(' '))

    deg = 0
    min = 0
    if 'd' in pos:
        deg = int(pos.split('d')[0])
        if "'" in pos:
            min = float(pos.split('d')[1].strip("'"))
    elif num_args == 2:
        deg = int(pos.split(' ')[0])
        min = float(pos.split(' ')[1].strip("'"))
    else:
        if "'" in pos:
            min = float(pos.strip("'"))
        else:
            deg = int(pos.strip("d"))
    
    lat_total_minutes = (deg - center_lat) * 60 + min
    y = lat_total_minutes * (1/60.0)

    if dir == "S":
        y *= -1

    return y

def plot_lon(pos, center_lon=lon_degree):
    dir = pos[0]
    if dir != 'W' and dir != 'E':
        raise ValueError(f"Invalid longitude direction {dir}")

    pos = pos[1:].strip()

    num_args = len(pos.split(' '))

    deg = 0
    min = 0
    if 'd' in pos:
        deg = int(pos.split('d')[0])
        if "'" in pos:
            min = float(pos.split('d')[1].strip("'"))
    elif num_args == 2:
        deg = int(pos.split(' ')[0])
        min = float(pos.split(' ')[1].strip("'"))
    else:
        if "'" in pos:
            min = float(pos.strip("'"))
        else:
            deg = int(pos.strip("d"))
    
    lon_total_minutes = (deg - center_lon) * 60 + min
    x = lon_total_minutes * (1/60.0) * lon_spacing

    if dir == 'W':
        x *= -1

    return x

class celestial_body:
    def __init__(self, name, date, time, apparent_lon, azimuth, ho, hc, color='black'):
        # Input parameters
        self.name = name
        self.date = date
        self.time = time
        self.lat = apparent_latitude
        self.lon = apparent_lon
        self.azimuth = azimuth
        self.ho = ho
        self.hc = hc
        self.color = color

        # Calculated position on plot
        self.x, self.y = plot_lon(self.lon), plot_lat(self.lat)

        # Calculated azimuth line on plot
        self.azimuth_math = (450 - azimuth) % 360
        line_length = 1
        self.end_x = self.x + line_length * np.cos(np.radians(self.azimuth_math))
        self.end_y = self.y + line_length * np.sin(np.radians(self.azimuth_math))
        self.start_x = self.x - line_length * np.cos(np.radians(self.azimuth_math))
        self.start_y = self.y - line_length * np.sin(np.radians(self.azimuth_math))

        # Calculated altitude intercept from ho and hc
        ho = ho.strip("'")
        ho = ho.replace("d", " ")
        ho_deg = int(ho.split(' ')[0])
        ho_min = float(ho.split(' ')[1])
        ho_total_minutes = ho_deg * 60 + ho_min

        hc = hc.strip("'")
        hc = hc.replace("d", " ")
        hc_deg = int(hc.split(' ')[0])
        hc_min = float(hc.split(' ')[1])
        hc_total_minutes = hc_deg * 60 + hc_min

        if ho_total_minutes > hc_total_minutes:
            self.intercept = ho_total_minutes - hc_total_minutes
            self.direction = 'T'
        else:
            self.intercept = hc_total_minutes - ho_total_minutes
            self.direction = 'A'

        # Plot apparent position
        ax.scatter(self.x, self.y, color=self.color, s=50)

        # Plot azimuth line
        ax.plot([self.start_x, self.end_x], [self.start_y, self.end_y], color=self.color, label='Sun LL')
        ax.arrow(self.x, self.y, self.end_x - self.x, self.end_y - self.y,
            head_width=0.05, head_length=0.1, fc=self.color, ec=self.color)
        
        # Plot intercept line
        # Determine start point for intercept line: Either along azimuth towards or away from celestial body
        if self.direction == 'T':
            base_x = self.x + (self.intercept / 60 * np.cos(np.radians(self.azimuth_math)))
            base_y = self.y + (self.intercept / 60 * np.sin(np.radians(self.azimuth_math)))
        else:
            base_x = self.x - (self.intercept / 60 * np.cos(np.radians(self.azimuth_math)))
            base_y = self.y - (self.intercept / 60 * np.sin(np.radians(self.azimuth_math)))
        
        visual_length = 1.8

        self.intercept_end_x1 = base_x + (visual_length * np.sin(np.radians(self.azimuth_math)))
        self.intercept_end_y1 = base_y - (visual_length * np.cos(np.radians(self.azimuth_math)))
        
        self.intercept_end_x2 = base_x - (visual_length * np.sin(np.radians(self.azimuth_math)))
        self.intercept_end_y2 = base_y + (visual_length * np.cos(np.radians(self.azimuth_math)))

        # Plot the intercept line
        ax.plot([self.intercept_end_x1, self.intercept_end_x2], 
                [self.intercept_end_y1, self.intercept_end_y2], color='green', linestyle='-', linewidth=2)


def plot_charting_sheet():
    fig, ax = plt.subplots(figsize=(10, 10))

    # Circle representing the chart
    circle = plt.Circle((0, 0), 1, color='black', fill=False)
    ax.add_artist(circle)

    # Horizontal lines representing latitudes
    ax.hlines(0, -1.5, 1.5, colors='black') # Center
    ax.hlines(1, -1.5, 1.5, colors='black') # Top
    ax.hlines(-1, -1.5, 1.5, colors='black') # Bottom

    # Latitude labels
    offset = 0.05
    if lat_dir == 'N':
        ax.text(-1.5, 1 + offset, str(lat_degree + 1) + '°', verticalalignment='center') # Top
        ax.text(-1.5, 0 + offset, lat_dir + str(lat_degree) + '°', verticalalignment='center') # Center
        ax.text(-1.5, -1 + offset, str(lat_degree - 1) + '°', verticalalignment='center') # Bottom
    else:
        ax.text(-1.5, 1 + offset, str(lat_degree - 1) + '°', verticalalignment='center') # Top
        ax.text(-1.5, 0 + offset, lat_dir + str(lat_degree) + '°', verticalalignment='center') # Center
        ax.text(-1.5, -1 + offset, str(lat_degree + 1) + '°', verticalalignment='center') # Bottom

    # Vertical lines representing longitudes
    ax.vlines(0, -1.5, 1.5, colors='black')  # Center
    ax.vlines(-lon_spacing, -1.5, 1.5, colors='black') # Left
    ax.vlines(lon_spacing, -1.5, 1.5, colors='black') # Right

    # Draw additional longitude lines if distance is small
    if lat_degree >= 60:
        ax.vlines(-lon_spacing*2, -1.5, 1.5, colors='black')
        ax.vlines(lon_spacing*2, -1.5, 1.5, colors='black')
   
    # Longitude labels
    lon_label_offset = 1.05  # Adjust this for vertical positioning
    if lon_dir == 'W':
        ax.text(lon_spacing, lon_label_offset, str(lon_degree - 1) + '°', horizontalalignment='right') # Right
        ax.text(0, lon_label_offset, lon_dir + str(lon_degree) + '°', horizontalalignment='right') # Center
        ax.text(-lon_spacing, lon_label_offset, str(lon_degree + 1) + '°', horizontalalignment='right') # Left

        # Label additional longitude lines if distance is small
        if lat_degree >= 60:
            ax.text(lon_spacing*2, lon_label_offset, str(lon_degree - 2) + '°', horizontalalignment='right') # Far right
            ax.text(-lon_spacing*2, lon_label_offset, str(lon_degree + 2) + '°', horizontalalignment='right') # Far left
    else:
        ax.text(-lon_spacing, lon_label_offset, str(lon_degree - 1) + '°', horizontalalignment='right') # Left
        ax.text(0, lon_label_offset, lon_dir + str(lon_degree) + '°', horizontalalignment='right') # Center
        ax.text(lon_spacing, lon_label_offset, str(lon_degree + 1) + '°', horizontalalignment='right') # Right

        # Label additional longitude lines if distance is small
        if lat_degree >= 60:
            ax.text(lon_spacing*2, lon_label_offset, str(lon_degree + 2) + '°', horizontalalignment='right') # Far right
            ax.text(-lon_spacing*2, lon_label_offset, str(lon_degree - 2) + '°', horizontalalignment='right') # Far left

    # Tick marks and their labels
    tick_length = 0.05
    tick_positions = np.linspace(-1, 1, 121)  # 60*2 divisions

    for idx, y in enumerate(tick_positions):
        if idx % 10 == 0: tick_length = 0.07
        elif idx % 5 == 0: tick_length = 0.05
        else: tick_length = 0.03

        ax.plot([0, tick_length], [y, y], color='black')

        # Print only the specified labels
        if idx % 10 == 0 and idx != 0 and idx != 120:
            if y > 0:
                ax.text(tick_length + offset, y, f"{idx-60}'", verticalalignment='center', horizontalalignment='center', fontsize='x-small')
            elif y < 0:
                ax.text(tick_length + offset, y, f"{idx}'", verticalalignment='center', horizontalalignment='center', fontsize='x-small')
    
    # Add extra bottom ticks
    num_bottom_ticks = 30
    bottom_tick_positions = np.linspace(-1.5, -1, num_bottom_ticks)
    for idx, y in enumerate(bottom_tick_positions):
        if idx % 10 == 0: tick_length = 0.07
        elif idx % 5 == 0: tick_length = 0.05
        else: tick_length = 0.03

        ax.plot([0, tick_length], [y, y], color='black')

        if idx % 10 == 0 and idx != 0:
            ax.text(tick_length + offset, y, f"{idx+num_bottom_ticks}'", verticalalignment='center', horizontalalignment='center', fontsize='x-small')

    # Add extra top ticks
    num_top_ticks = 30
    bottom_tick_positions = np.linspace(1, 1.5, num_top_ticks)
    for idx, y in enumerate(bottom_tick_positions):
        if idx % 10 == 0: tick_length = 0.07
        elif idx % 5 == 0: tick_length = 0.05
        else: tick_length = 0.03

        ax.plot([0, tick_length], [y, y], color='black')

        if idx % 10 == 0 and idx != 0:
            ax.text(tick_length + offset, y, f"{idx}'", verticalalignment='center', horizontalalignment='center', fontsize='x-small')

    # Tick marks for circle
    for angle in range(360):
        adjusted_angle = (90 - angle) % 360

        # Calculate the position for each tick mark
        x = np.cos(np.radians(adjusted_angle))
        y = np.sin(np.radians(adjusted_angle))

        # Define different lengths for the tick marks
        if angle % 10 == 0 and angle % 90 != 0:
            tick_length = 0.07
            # Label every 10 degrees
            ax.text(x * (1 - tick_length - 0.05), y * (1 - tick_length - 0.05), str(angle) + '°', fontsize='xx-small')
            
        elif angle % 5 == 0:
            tick_length = 0.05
        else:
            tick_length = 0.03

        # Draw tick marks
        ax.plot([x * (1 - tick_length), x], [y * (1 - tick_length), y], color='black')


    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect('equal', 'box')
    ax.axis('off')
    
    return fig, ax

# Create empty charting sheet
fig, ax = plot_charting_sheet()

# Plot dead reckoning
dr_x, dr_y = plot_lon(dr_lon), plot_lat(dr_lat)
ax.scatter(dr_x, dr_y, color='black', s=50)

# CB #1
sun = celestial_body('Sun', "12/25/14", "13:35:09", "W 60 46.5'",
    141.9, "26 28.2'", "25 52.4'", color='orange')

# CB #2
diphda = celestial_body('Diphda', "12/25/14", "21:57:05", "W 60 31.0'",
    169.8, "41 27.1'", "41 28.6'", color='blue')

# CB #3
capella = celestial_body('Capella', "12/25/14", "22:02:25", "W 60 28.8'",
    51.5, "31 42.3'", "31 1.5'", color='purple')

# Display plot
plt.show()