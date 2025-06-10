import matplotlib.pyplot as plt
import matplotlib.image as mpimg

def plot_event_on_field(event_coords, background='assets/field_overlay.png'):
    img = mpimg.imread(background)
    fig, ax = plt.subplots()
    ax.imshow(img)
    x, y = event_coords
    ax.plot(x, y, 'ro')  # Mark event
    plt.axis('off')
    return fig
