"""
    Python Script to get data logs
    Made by Michael Ah-Kiow on 2019-12-30
    Note that This is a simple algorithm with no regards to memory management
    or efficiency. I do not have a background if computer science.
    I'm sure there are better ways of doing this

    The algorithm simply
    1.finds all possible substring in given inputStream
    2. Check if each substring is Palindromic, and if it is, it saves the
    largest.

"""

"Importing Libraries"
from statistics import mean
import pandas as pd
import os
import csv
import matplotlib.pyplot as plt
import simplekml

class Plotutil:
    @staticmethod
    def plot_sd(time, x_sd, y_sd):
        print("Plotting SD")
        plt.figure()
        plt.plot(time, x_sd)
        plt.plot(time, y_sd)
        plt.xlabel("Epoch Time (s)")
        plt.title("Positional Errors from BestPos")
        plt.ylabel("Error (m)")
        plt.legend(["x sd", "y sd"])

    @staticmethod
    def Create_KML_plot(time, long, lat, height):
        print("Creating KML File")
        # Building KML Struct
        kml = simplekml.Kml(open = 1)

        # Document Name (Probably have a user input)
        kml.document.name = "output"

        # Declaring Point Format ('Shared Style' to reduce KML generator workload)
        sharedstyle = simplekml.Style()
        sharedstyle.labelstyle.color = 'ff0000ff'  # Red
        sharedstyle.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/paddle/red-circle.png"
        sharedstyle.labelstyle.scale =0

        # Assembling Data in a list
        Data = [time, long, lat, height]
        # Note that Plotkml uses long lat convension (y then x)
        for epoch, y, x, z in zip(time, long, lat, height):
            pnt = kml.newpoint(name = str(epoch), coords = [(x, y, z)])
            pnt.style = sharedstyle

        kml.save("map.kml")

    @staticmethod
    def Create_Folium_plot(time, lat, long):
        print("Creating Folium Plot")
        import folium
        from folium.plugins import FastMarkerCluster
        map = folium.Map(location = [mean(lat), mean(long)])

        # Different BaseMaps Selection:
        # folium.TileLayer('stamentoner').add_to(map)
        # folium.TileLayer('Mapbox Control Room').add_to(map)
        # folium.TileLayer('MapQuest Open Aerial').add_to(map)
        folium.TileLayer('StamenTerrain').add_to(map)

        for t, x, y in zip(time, lat, long):
            folium.CircleMarker(
                                location = (x, y),
                                radius = 1,
                                popup = "<i>{}<\i>".format(t),
                                tooltip = "Time(s)"
            ).add_to(map)

        map.save("map.html")


class Readutil:
    pass


class cBestpos:
    fields = ["LogName",
              "Port",
              "Sequence #",
              "%Idle Time",
              "Time Status",
              "Week",
              "Seconds",
              "Receiver Status",
              "Reserved1",
              "S/W Version",
              "Sol Status",
              "pos type",
              "lat(degrees)",
              "long(degrees)",
              "hgt(m)",
              "Undulation(m)",
              "Datum ID",
              "lat sd",
              "long sd",
              "height sd",
              "std id",
              "diff age",
              "sol_age",
              "#SVs",
              "#SolnSvs",
              "#solnL1SVs",
              "#solnMultiSVs",
              "Reserved",
              "ext Sol stat",
              "Galleo & Beidou Sig mask",
              "GPS & GLONASS SIG MASK",
              "CheckSum"
              ]
    # Returns the fields as a list
    # The property allows listout = bestpos.fields instead of having to do listout = bestpos.getfields()
    @property
    def getfields(self):
        return self.fields

    # @property
    # def fields_(self):
    #     return self.fields

    ## The whole purpose of proerty is to reduce code complexity and add convention.
    ## Usually when you have a getter or setter function such as:

    # 1. get_var(self): return self.var
    # the caller needs to be Output = object.get_var()
    # With property you can do output = object.var without using the gettter function itself OR having to use ()

    #Same for Setter (better example)
    # 2. set_var(self,input): self.var = 4
    # The Caller can just be object.var = 5 instead of object.setvar(5)

    @staticmethod
    def filterBestpos(filepath, filename):
        '''
        Grabs A GPS File and returns only bestpos logs
        Possible Update is to precise logname, so taht it can pull anylog
        instead of just bestpos
        Args:
            filepath: Directory of file
            filename: File Name

        Returns:
            Will ALWAYS write an ascii csv file named bestpos.csv
            Returns file name (a string)

        '''
        file = os.path.join(filepath, filename)
        with open(file, 'rt') as ifstream, \
                open("bestpos.csv", 'wt', newline = '') as ofstream:
            BestposWriter = csv.writer(ofstream)

            for line in csv.reader(ifstream):  # Now Reading instream
                if line[0] == "#BESTPOSA":  # If FIrst element of Csv is #BestposA
                    BestposWriter.writerow(line)
        return "bestpos.csv"


def read_data(filepath, filename):
    """
    Reads BESTPOS into a panda array.
    Possible Update is to read any LOG IF supplied the fields (i.e, names)

    Args:
        *names*: Fields that constitute bestpos logs,
        filepath:
        filename:

    Returns:
        Panda object
    """
    file = os.path.join(filepath, filename)
    print("Reading Data at {}".format(file))


    RawData = pd.read_csv(filepath_or_buffer = file,
                          delimiter = r",|;|\*",
                          names = cBestpos.fields,
                          header = None,
                          engine = 'python')


    return RawData


def main():
    print("Program Start")
    # To User Assign Later
    filename= "EastSoock_Downsampled.gps"
    filepath = r"C:\Users\micde\OneDrive - University of Calgary\Projects\Python\GNSS Plot"
    bestposfile = cBestpos.filterBestpos(filepath, filename)
    bestpos = read_data(filepath, bestposfile)

    # Plots
    Plotutil.plot_sd(bestpos['Seconds'], bestpos['lat sd'], bestpos['long sd'])
    Plotutil.Create_KML_plot(bestpos['Seconds'],bestpos["lat(degrees)"],bestpos["long(degrees)"],bestpos["hgt(m)"])
    Plotutil.Create_Folium_plot(bestpos['Seconds'],bestpos["lat(degrees)"],bestpos["long(degrees)"])

    print("Close Window when Finished")
    plt.show()


if __name__ == "__main__":
    main()
