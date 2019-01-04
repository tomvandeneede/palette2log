

import argparse
import struct

arguments = argparse.ArgumentParser(description='Octoprint Palette2 Log analyzer')

arguments.add_argument('-i',
                       '--input-file',
                       required=True)


def hex2float( hexnum):
    try:
        return struct.unpack('!f', bytes.fromhex(hexnum))[0]
    except:
        return struct.unpack('!f', hexnum.decode('hex'))[0]

def hex2int( hexnum):
    return  int(hexnum, 16)

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

    var_exct = 0
    var_act = 0
    var_addoff = 0
    var_pingnum = 0
    var_pinglen = 0
    pongline = ""

    for index in range(len(log_records)):
        if  "octoprint.plugins.palette2" in log_records[index]:
            log_line = log_records[index]
            if "Got Version: O21 D0014" in log_line:
                #start of a new print detected
                printNum += 1
                pintdisy=0
                inPrint = True
                pongline=""
                printinfo = True
                inping = False
                print("\n\n----------------------------PRINT #{:3}---------------------------------\n".format(printNum))

            if inPrint:


                fields = log_line.rstrip('\n').split(" ")

                if " Omega Write Thread: Sending: O1" in log_line:
                    print("Printing  {}   ===  length  {:-8.2f}mm\n".format(fields[-2][1:], hex2float(fields[-1][1:])))

                if printinfo and "sending to palette: O22" in log_line:
                    print("P2 - Printer Profile: {}".format(fields[-1][1:]))

                if printinfo and "sending to palette: O26 D" in log_line:
                    print("P2 - Number of Splices: {}".format(hex2int(fields[-1][1:])))

                if printinfo and "sending to palette: O27 D" in log_line:
                    print("P2 - Number of Pings: {}".format(hex2int(fields[-1][1:])))

                if printinfo and "read in line: profile id" in log_line:
                    print("P2 - Profile index: {}".format(fields[-1]))

                if printinfo and "read in line: spmm" in log_line:
                    stepspermm = int(fields[-1]) / 10
                    print("P2 ENCODER steps per mm: {:-3.2f}mm".format(stepspermm))


                if printinfo and "read in line: Tube length" in log_line:
                    print("P2 Tube length: {:-3.2f}cm".format(int(fields[-1])/100))

                if "sending to palette: O31 D" in log_line:
                    pingdist = hex2float(fields[-1][1:])
                    inPing = True
                    var_dist = format(pingdist)
                    var_exct = 0
                    var_act  = 0
                    var_addoff = 0
                    var_pingnum = 0
                    var_pinglen = 0

                if "Omega: read in line: O34 D2 " in log_line:
                    pongline = pongline + "\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t{:04}\t{:-8.2f}".format( hex2int(fields[-1][1:]),float(fields[-2][1:]) )
                    if not (printinfo):
                        print(pongline[1:])
                        pongline = ""

                if inPing:

                    if "Ping_ex_ct" in log_line:
                        var_exct =int(fields[-1])

                    if "Ping_actual_st:" in log_line:
                        var_act = int(fields[-1])/stepspermm

                    if printinfo and "Loading Error" in log_line:
                        print("Filament Load Err: {:-3.2f}mm {}".format(int(fields[-1])/stepspermm, int(fields[-1])))

                    if printinfo and "Loading Offset" in log_line:
                        print("Extruder Length.: {:-3.2f}mm".format(int(fields[-1] )/stepspermm))

                    if "Ping Additive Offset (st):" in log_line:
                        var_addoff =int(fields[-1])



                    if "Omega: read in line: O34 D1" in log_line:
                        var_pingnum = float(fields[-2][1:])
                        var_pingidx = hex2int(fields[-1][1:])
                        if (printinfo):
                            print("\n PING\t\t   (%),\t\tGCODE,\t\t ACTUAL,\t\tEX_CT(?),\tAdd Off\t\tPONG \t\tACTUAL")
                            print("-----------------------------------------------------------------------------------------------------")
                            print(pongline[1:])
                            pongline = ""

                        print("    {:04}\t{:-8.2f}\t{:-8.2f}\t{:-8.2f}\t{:-8}\t{:-8}".format(var_pingidx,var_pingnum,pingdist,var_act,var_exct,var_addoff))

                        inping = False
                        printinfo = False




if __name__ == "__main__":
      main(vars(arguments.parse_args()))
