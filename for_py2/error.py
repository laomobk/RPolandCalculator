import sys
import os.path

def get_line_from_line_no(lno, fp):
    if lno <= 0:
        return '<Illegal line number>'

    if not os.path.exists(fp):
        return '<NULL>'
    
    tlno = 1
    for ln in open(fp):
        if tlno == lno:
            return ln
        tlno += 1
    
    return '<NULL>'


def error_msg(line, msg, filename, errcode=1):
    sys.stderr.write('\tLine {2}: {3}\nFile: {0} :{2}, error: {1}\n'.format(
        filename, msg, line, get_line_from_line_no(line, filename)))

    sys.exit(errcode)



