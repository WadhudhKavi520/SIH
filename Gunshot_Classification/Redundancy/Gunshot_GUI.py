import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from matplotlib.animation import FuncAnimation

class PolarPlotter:
    def __init__(self, root):
        self.root = root
        self.root.title("Polar Coordinate Plotter")
        
        # Make the window full-screen
        self.root.attributes('-fullscreen', True)
        
        # Top content - white background
        self.top_frame = tk.Frame(root, bg='white')
        self.top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        self.radius_label = ttk.Label(self.top_frame, text="Radius (r):", font=("Helvetica", 12))
        self.radius_label.grid(row=0, column=0, padx=10, pady=10)
        self.radius_entry = ttk.Entry(self.top_frame, font=("Helvetica", 12))
        self.radius_entry.grid(row=0, column=1, padx=10, pady=10)
        
        self.theta_label = ttk.Label(self.top_frame, text="Angle (θ in degrees):", font=("Helvetica", 12))
        self.theta_label.grid(row=1, column=0, padx=10, pady=10)
        self.theta_entry = ttk.Entry(self.top_frame, font=("Helvetica", 12))
        self.theta_entry.grid(row=1, column=1, padx=10, pady=10)
        
        self.add_button = ttk.Button(self.top_frame, text="Add Coordinates", command=self.add_coordinates)
        self.add_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.clear_button = ttk.Button(self.top_frame, text="Clear Graph", command=self.clear_graph)
        self.clear_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Separator line
        separator = ttk.Separator(root, orient='horizontal')
        separator.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Bottom content - black background (for the polar plot)
        self.bottom_frame = tk.Frame(root, bg='black')
        self.bottom_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
        
        # Set up the matplotlib figure and axis with a black theme
        self.figure, self.ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})
        self.figure.patch.set_facecolor('black')  # Set figure background color
        self.ax.set_facecolor('black')  # Set axis background color
        self.ax.tick_params(colors='white')  # Set tick color to white
        self.ax.xaxis.label.set_color('white')  # Set x-axis label color to white
        self.ax.yaxis.label.set_color('white')  # Set y-axis label color to white
        self.ax.spines['polar'].set_color('white')  # Set polar spine color to white
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.bottom_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initial axis settings
        self.ax.set_ylim(0, 10)  # Increase initial radius to accommodate the beam
        self.ax.grid(True, color='white')  # Set grid color to white
        self.ax.plot([0], [0], 'go')  # Green dot at the origin
        
        # Animation settings
        self.animation_interval = 50  # Faster animation
        self.animation_max_radius = 10  # Ensure it reaches the outer edge
        self.animation_line = None
        self.animation = FuncAnimation(self.figure, self.animate, frames=np.linspace(0, self.animation_max_radius, 100), interval=self.animation_interval, blit=True)
        
        # Make the graph larger and responsive to screen size
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # List to store the points
        self.points = []
    
    def add_coordinates(self):
        try:
            # Get user input
            r = float(self.radius_entry.get())
            theta_deg = float(self.theta_entry.get())
            theta_rad = np.deg2rad(theta_deg)
            
            # Store the point
            self.points.append((theta_rad, r))
            
            # Update the radius limit dynamically
            max_radius = max(r for _, r in self.points)
            self.ax.set_ylim(0, max_radius + 1)  # Add a little padding
            
            # Plot the point
            self.ax.plot([theta_rad], [r], 'ro')  # Red dot for each point
            self.canvas.draw()
        except ValueError:
            print("Please enter valid numeric values for radius and angle.")
        
    def clear_graph(self):
        # Clear the plot and reset the points
        self.points.clear()
        self.ax.clear()
        self.ax.set_ylim(0, 10)  # Reset limit to accommodate animation
        self.ax.grid(True, color='white')  # Ensure grid stays white after clearing
        self.ax.plot([0], [0], 'go')  # Green dot at the origin
        self.canvas.draw()

    def animate(self, radius):
        if self.animation_line:
            self.animation_line.remove()
        
        # Draw a circle (beam) expanding from the origin
        self.animation_line, = self.ax.plot(np.linspace(0, 2 * np.pi, 100), np.full(100, radius), color='cyan', alpha=0.5)
        return self.animation_line,

if __name__ == "__main__":
    root = tk.Tk()
    app = PolarPlotter(root)
    root.mainloop()
