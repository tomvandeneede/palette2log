

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
        try:
            return struct.unpack('!f', hexnum.decode('hex'))[0]
        except:
            return 0.0

def hex2int( hexnum):
    return  int(hexnum, 16)

def main(args):
    input_file = args['input_file']
    printNum = 0
    inPrint = False
    inPing = False
    pingString=""
    stepspermm = 1

    filamentchanges = []
    filament='-'

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
    filamentProduced = 0
    pongline = ""
    lasttimestamp = -1
    splices = []
    splicefilament=[]


    print("Starting analysis of {} lines".format(len(log_records)))
    for index in range(len(log_records)):
        if  "octoprint.plugins.palette2" in log_records[index]:

            log_line = log_records[index]

            timestamp = int(log_line[11:13])*3600 + int(log_line[14:16])*60 + float(log_line[17:23].replace(",","."))

            if lasttimestamp == -1:
                lasttimestamp = timestamp

            while timestamp < lasttimestamp:
                timestamp += 86400


            if (timestamp-lasttimestamp)>60:
                #print("At {} - Data gap of {:-5.2f}  seconds".format(log_line[0:22],timestamp-lasttimestamp))
                pass
            lasttimestamp = timestamp


            if "Got Version: O21 D0014" in log_line:

                for line in filamentchanges:
                    print(line)
                #start of a new print detected
                printNum += 1
                pintdisy=0
                inPrint = True
                pongline=""
                printinfo = True
                inping = False
                print("\n\n----------------------------PRINT #{:3}---------------------------------\n".format(printNum))
                filamentchanges = []
                filament = "-"
            if inPrint:


                fields = log_line.strip().split(" ")


                if " Omega Write Thread: Sending: O1" in log_line:
                    print("Printing  {}   -=-  length  {:.2f}mm\n".format(fields[-2][1:], hex2float(fields[-1][1:])))

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


                if "Got splice D:" in log_line:
                    splices.append(hex2float(log_line.strip()[-8:]))
                    splicefilament.append(log_line[83])


                if "O97 U26 D" in log_line:
                    filamentProduced = hex2int(log_line.strip()[-8:])

                if "Current Drive:" in log_line:
                    splicefilamentfrom=log_line.strip()[-1]


                if "moving filament in drive" in log_line:
                    splicefilamentact=log_line[89]

                if "O97 U25 D1" in log_line:
                    warning = ""
                    effect_splice= hex2int(log_line.strip()[-4:])
                    if len(splicefilament) > effect_splice:
                        sf = splicefilament[effect_splice]
                        sf2=splices[effect_splice-1]
                        if splicefilamentact == splicefilament[effect_splice]:
                            warning = ""
                        else:
                            warning = "****"
                    else:
                        sf=-1
                        sf2=-1


                    filamentchanges.append("{:04}\t\t{}\t\t{}\t\t{:6}\t\t{}\t\t{:-8.2f}\t\t{}\t\t".format(effect_splice, splicefilamentfrom, splicefilamentact, filamentProduced,sf, sf2,warning))
                    splicefilament.append(splicefilament[-1])
                    splices.append(splices[-1])

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

                    if "Omega: read in line: O34" in log_line:
                        if "O34 D1" in log_line:
                             var_pingnum = float(fields[-2][1:])
                             var_pingidx = hex2int(fields[-1][1:])

                        if (printinfo):
                            print("\n PING\t\t   (%),\t\tGCODE,\t\t ACTUAL,\t\tEX_CT(?),\tAdd Off\t\tPONG \t\tACTUAL")
                            print("-----------------------------------------------------------------------------------------------------")
                            print(pongline[1:])
                            pongline = ""

                        if "O34 D0" in log_line:
                            print("REJECTED PING")
                        else:
                            print("    {:04}\t{:-8.2f}\t{:-8.2f}\t{:-8.2f}\t{:-8}\t{:-8}".format(var_pingidx,var_pingnum,pingdist,var_act,var_exct,var_addoff))


                        inPing = False
                        printinfo = False

    if len(filamentchanges)>0:
        print("\n-------------------------------------------------------------------------")
        print("SPLICE\t\tFROM\tTO\t\t\tPOS\t\tTo(P2)\t\tPos(P2)")
        print("-------------------------------------------------------------------------")
        for line in filamentchanges:
            print(line)
        print("-------------------------------------------------------------------------")

if __name__ == "__main__":
      main(vars(arguments.parse_args()))
