import os
from extractor import Extractor


# read all files in jws folder
def main():
    for filename in os.listdir('JWS'):
        if filename.endswith('.jws'):
            print(filename)
            extractor = Extractor("JWS/"+filename)
            extractor.read_header()
            unpacked_data = extractor.read_data()
            csv_data = list(zip(*unpacked_data))
            with open('CSV/'+filename+'.csv', 'w') as f:
                # write header file 1st is the sample name, 2nd is the comment
                f.write(extractor.sample_name + ',' + '' + '\n')
                f.write(extractor.comment + ',' + '' + '\n')
                f.write(filename.split('.jws')[0] + ',' + '' + '\n')
                f.write('Wavelength,Absorbance' + '\n')
                f.write('nm,au' + '\n')
                for row in csv_data:
                    f.write(','.join(map(str, row)) + '\n')

if __name__ == '__main__':
    main()