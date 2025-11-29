import os
from typing import List, Tuple
from Jws2Csv.extractor import Extractor


def main() -> None:
    """
    Read all JWS files from 'JWS' folder, extract data, and save as CSV.
    """
    for filename in os.listdir('JWS'):
        if filename.endswith('.jws'):
            print(filename)

            # Create an instance of Extractor
            extractor = Extractor("JWS/"+filename)

            # Read the header
            extractor.read_header()

            # Read the data
            unpacked_data = extractor.read_data()

            # Transpose data to group by columns
            csv_data = list(zip(*unpacked_data))

            # Write to CSV
            output_path: str = 'CSV/' + filename + '.csv'
            with open('CSV/'+filename+'.csv', 'w') as f:
                
                # write header file 1st is the sample name, 2nd is the comment
                f.write(extractor.sample_name + ',' + '' + '\n')
                f.write(extractor.comment + ',' + '' + '\n')
                f.write(filename.split('.jws')[0] + ',' + '' + '\n')
                f.write('Wavelength,Absorbance' + '\n')
                f.write('nm,au' + '\n')

                # Write data rows
                for row in csv_data:
                    f.write(','.join(map(str, row)) + '\n')

if __name__ == '__main__':
    main()