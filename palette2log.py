

import argparse
import struct

arguments = argparse.ArgumentParser(description='Octoprint Palette2 Log analyzer')

arguments.add_argument('-i',
                       '--input-file',
                       required=True)


def hex2float( hexnum):
    return struct.unpack('!f', bytes.fromhex(hexnum))[0]


def main(args):
    input_file = args['input_file']
    printNum = 0
    inPrint = False
    inPing = False
    pingString=""
    stepspermm = 1

    try:
        with open(input_file) as opf:
            log_records = opf.readlines()
    except:
        print("Could not open {}".format(input_file))
        exit(1)

    for index in range(len(log_records)):
        if  "octoprint.plugins.palette2" in log_records[index]:
            log_line = log_records[index]
            if "Got Version: O21 D0014" in log_line:
                #start of a new print detected
                printNum += 1
                inPrint = True
                inping = False
                print("PRINT #{}".format(printNum))

            if inPrint:

                fields = log_line.rstrip('\n').split(" ")

                if "sending to palette: O22" in log_line:   #printer profile information
                    print("  Printer Profile: {}".format(fields[-1][1:]))

                if "read in line: profile id" in log_line:
                    print("  Palette 2  Profile index: {}".format(fields[-1]))

                if "read in line: spmm" in log_line:
                    print("  Palette 2 steps per mm: {}".format(fields[-1]))
                    stepspermm = int(fields[-1])/10

                if "read in line: Tube length" in log_line:
                    print("  Tube length: {}cm".format(int(fields[-1])/100))

                if "sending to palette: O31 D" in log_line:
                    pingdist = hex2float(fields[-1][1:])
                    inPing = True
                    pingString = " - PING {:-8.2f}mm - ".format(pingdist)

                if inPing:

                    if "Ping_ex_ct" in log_line:
                        pingString += " EX_CT :{:7}".format(int(fields[-1]))

                    if "Ping_actual_st:" in log_line:
                        pingString += " Actual: {:-8.2f}mm".format(int(fields[-1])/stepspermm)

                    if "Loading Error" in log_line:
                        pingString += " Load Err: {:-3.2f}mm".format(int(fields[-1])/stepspermm)

                    if "Loading Offset" in log_line:
                        pingString += " Load Off.: {:-3.2f}mm".format(int(fields[-1] )/stepspermm)

                    if "Local Offset" in log_line:
                        pingString += "Extruder: {:03}".format(int(fields[-1]))

                    if "Ping Additive Offset (st):" in log_line:
                        pingString += " Add. Off. {:-3.2f}mm".format(int(fields[-1])/stepspermm)

                    if "Omega: read in line: O34 D1" in log_line:
                        pingString = fields[-2][1:]+" At "+fields[-1][1:]+" "+pingString
                        if not  pingString[0] == "1":
                            pingString = " "+pingString
                        print ( pingString)
                        pingString=""
                        inping = False




if __name__ == "__main__":
      main(vars(arguments.parse_args()))
