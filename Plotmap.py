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
import argparse
import folium
from folium.plugins import FastMarkerCluster
class UserInteraction:
    def __init__(self, description):
    # Creating the Parser Object, Usually Only 1 is required
        self.Parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=description)


        # Now Adding Arguments
        self.Parser.add_argument('GPS',
                            type=str,
                            #nargs = 2,
                            help='GPS File to grab data from')

        self.Parser.add_argument('-m' ,'--map',
                            nargs='*',
                            choices=['sd' ,'kml' , 'traj', 'heatmap'],
                            type=str,
                            action='append',
                            help='Optional Toggle to Specify which map to use, default uses all.   '
                                 'Specify maps by using: \n \"PlotMap.py GPSFILE -m \'list of maps\''
                                 ' where list of maps include: sd traj KML or Heatmap")')

    def get_args(self):
        return self.Parser.parse_args()


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

    def __init__(self, filename,  fields= [], delimiter=r",|;|\*" ,  filepath=""):
        """
        Declaration for Read Util. Right now it only read csvs.
        Need to include different read type later on probably with a flag
        :param filename: str file to read
        :param fields: If there are no headers in file, takes a list as header
        :param delimiter: a regex string of delimeters, example r",|;|\*"
        :param filepath: Optional path if in different directory

        To do:
        File type (txt, csv, ..etc)
        Read Type (Pandas, Readcsv, ..etc)
        """
        if filepath is False:
            self.filename = filename
        else:
            self.filename =  os.path.join(filepath, filename)

        if fields is False:
            self.header=True
        else:
            self.header = False

        self.fields=fields
        self.delimeter = delimiter

    def Read_Pandas(self):
        print("Reading Data at {} into Pandas".format(self.filename))
        if self.header is True:
            # First row is header in datastructure
            self.rawdata = pd.read_csv(filepath_or_buffer=self.filename,
                                       delimiter = self.delimeter,
                                       engine='python')
        else:
            # Use List headers instead of taking first row as header
            self.rawdata = pd.read_csv(filepath_or_buffer=self.filename,
                                       delimiter = self.delimeter,
                                       names = self.fields,
                                       header=None,
                                       engine='python')
        return self.rawdata


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


def main():
    print("Program Start")

    # ArgParsing & User Input
    Parser = UserInteraction("Welcome to GNSS Plot Utils, \n Simple use: PlotMap.py GPSFILE")
    Input_args = Parser.get_args()
    filename= Input_args.GPS
    filepath = ""

    if Input_args.map is None:
        bSdmap=True
        bKMLPlot=True
        bTrajPlot=True

    else:
        if 'sd' in Input_args.map[0]:
            bSdmap=True
        else:
            bSdmap=False
        if 'kml' in Input_args.map[0]:
            bKMLPlot = True
        else:
            bKMLPlot = False
        if 'traj' in Input_args.map[0]:
            bTrajPlot = True
        else:
            bTrajPlot = False

    # Reading/Parsing Data
    bestposfile = cBestpos.filterBestpos(filepath, filename)

    Read = Readutil(bestposfile,
                    filepath = filepath,
                    delimiter = r",|;|\*",
                    fields = cBestpos.fields)

    bestpos =Read.Read_Pandas()

    # Plots
    if bSdmap:
        print("Ploting Sd Map")
        Plotutil.plot_sd(bestpos['Seconds'],
                         bestpos['lat sd'],
                         bestpos['long sd'])
    if bKMLPlot:
        Plotutil.Create_KML_plot(bestpos['Seconds'],
                                 bestpos["lat(degrees)"],
                                 bestpos["long(degrees)"],
                                 bestpos["hgt(m)"])
        print("KML Successfully Created, Check local directory")

    if bTrajPlot:
        Plotutil.Create_Folium_plot(bestpos['Seconds'],
                                    bestpos["lat(degrees)"],
                                    bestpos["long(degrees)"])
        print("HTML Map Successfully Created, Check local directory")

    print("Close Window when Finished")

    # map2 = folium.Map(location = [mean(bestpos["lat(degrees)"]), mean(bestpos["long(degrees)"])])
    # folium.plugins.HeatMap([bestpos["lat(degrees)"],
    #                          bestpos["long(degrees)"],
    #                          bestpos['lat sd']]).add_to(map2)
    #
    # map2.save("heatmap.html")

    if bSdmap:
        plt.show()


if __name__ == "__main__":
    main()
