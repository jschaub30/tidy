#!/usr/bin/python

'''
Input:  file
Output: stdout
Tidy output of /usr/bin/time --verbose into CSV format
Jeremy Schaub
$ ./timeread.py [time_output_file]
'''

import sys


class Measurement:

    '''
    Data structure for /usr/bin/time measurement
    '''

    def __init__(self):
        self.elapsed_time_sec = ''
        self.user_time_sec = ''
        self.system_time_sec = ''
        self.exit_status = '-1'
        self.cpu_pct = ''
        self._expected_length = 5  # Change this when adding new fields

    def fields(self):
        '''
        Returns a list of all possible measured fields
        '''
        fields = [i for i in self.__dict__.keys() if i[:1] != '_']
        return fields

    def header(self):
        '''
        Returns a csv string with all header fields
        '''
        return ','.join(self.fields())

    def addfield(self, name=None, value=None):
        if name not in self.fields():
            self._expected_length += 1
        setattr(self, name, value)

    def htmlclass(self):
        return "warning" if int(self.exit_status) != 0 else ""

    def rowhtml(self, fields=None, include_tr=True, rowclass=None):
        '''
        Returns an html formatted string with all td cells in row
        include_tr = True --> add "<tr>" and </tr> tags
        prefix = 'FIELD' or ['FIELD1', 'FIELD2']
        suffix = 'FIELD' or ['FIELD1', 'FIELD2']
        '''
        if not fields:
            fields = self.fields()
        if not rowclass:
            rowclass = self.htmlclass()

        values = [str(getattr(self, field)) for field in fields]

        # if prefix:
        #     if isinstance(prefix, list):
        #         prefix.reverse()
        #         # [fields.insert(0, field) for field in prefix]
        #         [values.insert(0, '') for field in prefix]
        #     else:
        #         # fields.insert(0, prefix)
        #         values.insert(0, prefix)
        # if suffix:
        #     if isinstance(prefix, list):
        #         tmp = [values.append(field) for field in suffix]
        #     else:
        #         values.append(suffix)

        if include_tr:
            html_row = '<tr class="%s">\n' % (rowclass)
        else:
            html_row = ''
        html_row += '<td>'
        html_row += '</td>\n<td>'.join(values)
        html_row += '</td>\n'
        if include_tr:
            html_row += '</tr>\n'
        return html_row

    def parse(self, time_fn):
        '''
        This parses the output of "/usr/bin/time --verbose"
        Parsing these fields:  exit_status, user_time_sec, elapsed_time_sec,
                               system_time_sec, cpu_percent
        '''
        # try:
        with open(time_fn, 'r') as fid:
            blob = fid.read()
        self.exit_status = blob.split('Exit status: ')[1].split('\n')[0].strip()
        if self.exit_status != '0':
            sys.stderr.write(
                "WARNING! non-zero exit status = %s in file \n\t%s\n" %
                (self.exit_status, time_fn))
        self.user_time_sec = blob.split(
            'User time (seconds): ')[1].split('\n')[0].strip()
        self.system_time_sec = blob.split(
            'System time (seconds): ')[1].split('\n')[0].strip()
        val = blob.split('Elapsed (wall clock) time (h:mm:ss or m:ss): ')[
            1].split('\n')[0].strip()
        if len(val.split(':')) == 2:   # m:ss
            val = str(
                int(val.split(':')[0]) * 60 + float(val.split(':')[1].strip()))
        elif len(val.split(':')) == 3:   # h:m:ss
            val = str(int(val.split(':')[
                      0]) * 3600 + int(val.split(':')[1]) * 60 +
                      float(val.split(':')[2].strip()))
        self.elapsed_time_sec = val
        self.cpu_pct = blob.split('Percent of CPU this job got: ')[
            1].split('\n')[0].strip('%')
        # except:
        #     sys.stderr.write('Problem parsing time file %s\n' % time_fn)

    def is_valid(self):
        return len(self.fields()) == self._expected_length


def main(time_fn):
    # Wrapper to print to stdout
    m = Measurement()
    sys.stdout.write('%s' % (m.rowhtml()))
    m.parse(time_fn)
    sys.stdout.write('%s' % (m.rowhtml()))


if __name__ == '__main__':
    main(sys.argv[1])
