########################################################################
#   Created by Alexander Hanel <alexander.hanel<at>gmail<dot>com>
#   Version: 1.0 
#   Data: November Something 2012 
#   This is file is part of cospare.py. A tool that is used for comparing
#   microsoft executable functions using normalization of x86 assembly and
#   cosine similiarity. The script reliese on IDA to create the ".jsin" 
#   output. The output file is then compared to another output file. If
#   there are matches in functions they will be added to the count. This
#   script (idb2jsin.py) is to be passed to IDA via the command line to
#   create the output MD5.jsin file. The extension '.jsin' is a json file.
#   The extenstion is unique so it can be used when scanning a directory.
#   The scanned executable does not need to have the import table rebuilt.
#   To create the output run the following command line the PE file. 
#   Command line option
#   %IDA_DIR%\idaw.exe -A -Sidb2jsin.py <bad.(exe|dll|sys|etc)>
########################################################################

import idautils
import idc
import idaapi
from itertools import izip 
import json

class Parse():
    def __init__(self):
        self.ea = ScreenEA()
        self.opTypes = { 0:'', 2:'o_mem', 3:'o_phrase', 4:'o_displ', 6:'o_far', 7:'o_near'}
        self.function_eas = []
        self.getFunctions()
        
    def instructionCount(self, instructionList):
        'gets the unique count of each instruction line in a function'
        count = {}
        for mnem in instructionList:
            if mnem in count:
                count[mnem] += 1
            else:
                count[mnem]  = 1
        # returns dictionary { sub_func { unique_norm_intruction1: count_value, unique_norm_intruction2: count_value2}}
        return count     
        
    def getFunctions(self):
        'get a lit of function addresses'
        for func in idautils.Functions():
            # Ignore Library Code
            flags = GetFunctionFlags(func)  
            if flags & FUNC_LIB:
                continue
            self.function_eas.append(func)    
        
    def getInstructions(self, function):
        'get all instruction in a function'
        buff = []
        for x in FuncItems(function):
            buff.append(self.normalize(x))
        return buff
        
    def normalize(self, i_ea):
        'Normalize the instructions' 
        line = ''
        op1 = GetOpType(i_ea, 0)
        op2 = GetOpType(i_ea, 1)
        if self.opTypes.get(op1):
            op1 = self.opTypes.get(op1)
        else:
            op1 = GetOpnd(i_ea, 0)
        if self.opTypes.get(op2):
            op2 = self.opTypes.get(op2)
        else:
            op2 = GetOpnd(i_ea, 1)
        return GetMnem(i_ea) + ' ' + op1 + ' ' +  op2
        
    def run(self):
        'start'
        funcBuffer = []
        jsonDict = []
        md5 = GetInputFileMD5()
        jsonDict.append('MD5')
        jsonDict.append(md5) 
        for func in self.function_eas:
            jsonDict.append(GetFunctionName(func))
            fun = idaapi.get_func(func)
            # get instructions of a function 
            funcBuffer = self.getInstructions(fun.startEA) 
            funcCount = self.instructionCount(funcBuffer)
            jsonDict.append(funcCount)
        # convert list to dict
        # source: http://stackoverflow.com/a/4576128
        tmp = iter(jsonDict)
        jsonDict = dict(izip(tmp,tmp))
        out = open(md5 + '.jsin', 'wb')
        # dump dict to j
        json.dump(jsonDict,out)
        out.close()
        
if __name__ == '__main__':
    idaapi.autoWait()
    x = Parse()
    x.run()
    idc.Exit(0) 
