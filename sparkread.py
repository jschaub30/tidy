#!/usr/bin/python

'''
Input:  file
Output: stdout
Tidy output of spark stderr file CSV format
Jeremy Schaub
$ ./sparkread.py [time_output_file]
'''

import sys


class Measurement:

    '''
    Data structure for /usr/bin/time measurement
    '''

    def __init__(self):
        self.stage_times = ['0']
        self.spill_count = -1
        self._expected_length = 2

    def fields(self):
        '''
        Returns a list of fields in the data structure
        '''
        fields = ['spill_count']
        num_stages = len(self.stage_times) - 1
        stage_header = ['stage %d [sec]' % i for i in range(num_stages)]
        stage_header.append('total time [sec]')
        fields.extend(stage_header)
        return fields

    def headercsv(self):
        '''
        Returns a csv string with all header fields
        '''
        return ','.join(self.fields())

    def rowcsv(self):
        '''
        Returns a csv string with all data fields
        '''
        values = [self.spill_count]
        values.extend(self.stage_times)
        return ','.join(values)

    def headerhtml(self, fields=None):
        '''
        Returns an HTML string all header fields
        '''
        if not fields:
            fields=self.fields()
        row = '<tr>\n<th>%s</th>\n</tr>\n' % ('</th>\n<th>'.join(fields))

        return row

    def addfield(self, name=None, value=None):
        if name not in self.fields():
            self._expected_length += 1
        setattr(self, name, value)

    def htmlclass(self):
        return "warning" if int(self.spill_count) != 0 else ""

    def rowhtml(self, fields=None, rowclass=None):
        ''' Returns an html formatted string with all td cells in row '''
        if not fields:
            fields = self.fields()
        if not rowclass:
            rowclass = self.htmlclass()

        values = [self.spill_count]
        values.extend(self.stage_times)

        html_row = '<tr class="%s">\n<td>' % (rowclass)
        html_row += '</td>\n<td>'.join(values)
        html_row += '</td>\n</tr>\n'
        return html_row

    def is_valid(self):
        return len(self.fields()) == self._expected_length

    def parse(self, spark_fn):
        '''
        This parses the output of the spark stderr file
        '''
        try:
            with open(spark_fn, 'r') as f:
                blob = f.read()
            num_stages = len(blob.split('finished in ')[1:])
            stage_times = ['' for i in range(num_stages)]
            i = 0
            total_time = 0
            for a in blob.split('finished in ')[1:]:
                stage_times[i] = a.split(' s\n')[0]
                total_time += float(stage_times[i])
                i += 1
            stage_times.append(str(total_time))
            self.stage_times = stage_times
            self.spill_count = str(blob.lower().count('spill'))
            if not self.is_valid():
                sys.stderr.write('Not a valid spark file %s\n' % spark_fn)
                assert False
        except Exception as err:
            sys.stderr.write('Problem parsing time file %s\n' % spark_fn)
            sys.stderr.write(str(err) + '\n')

def main(spark_fn):
    # Wrapper to print to stdout
    m = Measurement()
    m.parse(spark_fn)
    sys.stdout.write('%s\n%s\n' % (m.headercsv(), m.rowcsv()))




if __name__ == '__main__':
    main(sys.argv[1])
