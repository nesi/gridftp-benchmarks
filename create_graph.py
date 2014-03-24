import argparse
import csv
import matplotlib.pyplot as plt
import datetime as dt

__author__ = 'markus'


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Creates graphs from csv files created by transfer.py')
    parser.add_argument('-i', '--input', help="csv input file(s), comma seperated")
    parser.add_argument('-o', '--output', help="graph output file")
    args = parser.parse_args()

    input = args.input
    output = args.output

    x_axis = []
    y_axis = []

    with open(input, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            start = row[0]
            end = row[1]
            elapsed = row[2]
            speed = row[3]
            size = row[4]
            run_name = row[5]
            exe = row[6]
            parameters = row[7]
            source = row[8]
            target = row[9]
            cmd = row[10]

            start_time = dt.datetime.fromtimestamp(float(start))

            x_axis.append(start_time)
            y_axis.append(speed)

    plt.xlabel('Time')
    plt.ylabel('MB/s')
    plt.plot(x_axis, y_axis, 'ro')
    plt.savefig(output, bbox_inches='tight')
