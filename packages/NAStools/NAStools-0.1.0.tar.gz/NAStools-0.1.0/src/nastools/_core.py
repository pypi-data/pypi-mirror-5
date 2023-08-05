# _core.py
# NAStools core utilities for reading ICARRT and NASA Ames files



##### MODULES ###
import numpy as np
import pandas
import datetime
import gzip, bz2
import os, re, struct, warnings



##### CLASS DEFINITIONS #####      
        
class Naspy(object): 
    """Naspy class to generate naspy objects containing header and filetype information.
    
    """ 
    def __init__(self, fname, data_format='auto'):
        """Generates a Naspy object.
        
        This function is the entry point to working with ICARRT or NASA Ames files. An 
        object is created which contains header information and internal data specifying 
        information about the file.
        
        PARAMETERS
        ----------
        fname : str
            Absolute or relative path to input file. File may be uncompressed or 
            compressed (bz2 or gzip); gzipped files are not fully supported by numpy.
        data_format : {'auto', 'ict', 'nas'}, default 'auto'
            Specifies file format of input file; default behavior is for nastools to 
            determine this automatically, however this can be manually over-ridden by 
            specifying either 'ict' or 'nas' explicitly.
            
        RETURNS
        -------
        naspy : object
            A naspy object containing information about the file and methods to generate 
            numpy.arrays or pandas.DataFrames.
        
        EXAMPLES
        --------
        # Generate a header object
        import nastools as nt
        naspy = nt.Naspy(fname)
        
        # Get PI(s)
        print naspy.header.PI

        """
        if data_format not in ['auto', 'ict', 'nas']:
            raise AttributeError("data_format='%s' is unknown; "
                                 "must be 'auto', 'ict' or 'nas'" % data_format)
        
        self._data_format = data_format
        self._fileAbsPath_ = os.path.abspath(fname) # full path to file
        self._file = Fifo(self) # File object instance
        self.header = Header(self) # self passed into Header, to derive attrs
        self.time = Time(self)  # Get time functionality
        Fifo(self).filetype_warnings() # Issue gzip warning
        
        return None
        
    def make_numpy(self, masked=False, missing_values='auto'):
        """Generates a numpy.ndarray.
        
        PARAMETERS
        ----------
        masked : bool, default False
            Species whether to return a masked array; must be True to convert missing 
            values to nans in the returned array.
        missing_values : 'auto' or list, default 'auto'
            A list of strings specifying additional field names in the header file 
            (e.g. 'LLOD_FLAG') which indicate missing values. The default behavior is 
            'auto' which automatically searches for 'LLOD_FLAG' and 'ULOD_FLAG' fields in 
            the header. Note that the missing data flags for the dependent variables 
            (e.g. -99999) do not need to be specified.
            
        RETURNS
        -------
        arr : numpy.ndarray
        
        EXAMPLES
        --------
        # Generate a numpy.ndarray representing data in file
        arr = naspy.make_numpy()
        
        # Generate a masked array with missing values as np.nan
        arr = naspy.make_numpy(masked=True)
        
        """
        # Get variable names
        names = [ self.header.INDEPENDENT_VARIABLE['NAME'] ]
        for i in range(len(self.header.DEPENDENT_VARIABLE)):
            names.append(self.header.DEPENDENT_VARIABLE[i]['NAME'])
        
        # Get a dictionary of missingVals on a per column basis
        if missing_values == 'auto':
            missingVals = self.missing_values()
        else:
            missingVals = self.missing_values(missing_values)
        
        # Read the lines into numpy object
        arr = np.genfromtxt(
                    self._fileAbsPath_,
                    delimiter = ',',  # Comma seperated (ICT/AMES style?),
                    names = names,
                    skip_header = self.header.HEADER_LINES,
                    missing_values = missingVals,
                    usemask=masked,
                    dtype = None,
                    case_sensitive = False,
                    unpack=True
                    )
        # TODO: Future feature, numpy array with datetime64 support
        # KNOWN DEFECT: can't append datetime64 to an existing array using:
        #   numpy.lib.recfunctions.append_fields
        #  fixed in Numpy 1.7.0 
        #  (see: http://projects.scipy.org/numpy/ticket/1912)
        #  (github: https://github.com/numpy/numpy/issues/2505)
        
        return arr
    
    def make_DataFrame(self, case_sensitive='upper', convert_missing=True, 
                        make_datetime=True, datetime_asindex=True, drop_datetime=True,
                        missing_values='auto'):
        """Generates a pandas.DataFrame from a Naspy object.
        
        PARAMETERS
        ----------
        case_sensitive : string or bool, default 'upper'
            Formatting option of columns names; choices are 'upper' (default), 'lower', or
            'as-is' in addition to True or False. With no format specified, column names 
            will be returned in upper case; 'as-is' or True returns variables in the case 
            as they are specified in the file.
        convert_missing : bool, default True
            Option to convert specified missing values to np.nan
        make_datetime : bool, default True
            Option to generate a datetime column
        datetime_asindex : bool, default True
            Option to reindex DataFrame by datatime column; note that make_datetime must 
            be True for this option to be meaningful.
        drop_datetime: bool, default True
            Whether or not to remove the datetime column from the DataFrame; note that 
            both make_datetime and datetime_asindex must be True for this option to to be 
            meaningful.
        missing_values : 'auto' or list, default 'auto'
            A list of strings specifying additional field names in the header file 
            (e.g. 'LLOD_FLAG') which indicate missing values. The default behavior is 
            'auto' which automatically searches for 'LLOD_FLAG' and 'ULOD_FLAG' fields in 
            the header. Note that the missing data flags for the dependent variables 
            (e.g. -99999) do not need to be specified.
        compression : {'auto', 'gzip', 'bz2', None}, default 'auto'
            For on-the-fly decompression of on-disk data; 'auto' will try and detect 
            filetype based on extension. Use other options to manually override 'auto'.
        
        RETURNS
        -------
        df : pandas.DataFrame
            A pandas.DataFrame containing data from the naspy object
        
        EXAMPLES
        --------
        # Generate a DataFrame object
        df = naspy.make_DataFrame()
        
        """
      
        # TODO: [QUICK FIX] implement get_filetype tuple, instead of doing it again
        # Compressed file?
        ext = Fifo(self).get_filetype()[1]
        if ext not in ['gzip', 'bz2']:
            ext = None
        
        df = pandas.io.parsers.read_table(
                 self._fileAbsPath_, 
                 skiprows = self.header.HEADER_LINES, 
                 delimiter = ',', 
                 names = self.get_column_names(case_sensitive),
                 dtype = np.float64, # Allow for nans
                 compression = ext
                 )
        
        if convert_missing:
             df = self.dataframe_nans(df, missing_values)
        
        if make_datetime:
            DATETIME = 'DATETIME'
            df[DATETIME] = ( np.timedelta64(df[df.columns[0]]*1E6) + 
                             np.datetime64(self.header.START_UTC.isoformat()) )
            if datetime_asindex:
                df = df.set_index(DATETIME, drop=drop_datetime)
        
        return df
    
    def get_column_names(self, case_sensitive='upper'):
        """Returns a list of column names from a Naspy object.
        
        PARAMETERS
        ----------
        case_sensitive : string or bool, default 'upper'
            Formatting option of columns names; choices are 'upper' (default), 'lower', or
            'as-is' in addition to True or False. With no format specified, column names 
            will be returned in upper case; 'as-is' or True returns variables in the case 
            as they are specified in the file.
            
        """
        names = [ self.header.INDEPENDENT_VARIABLE['NAME'] ]
        for i in range(len(self.header.DEPENDENT_VARIABLE)):
            names.append(self.header.DEPENDENT_VARIABLE[i]['NAME'])
        
        if case_sensitive in ['upper', False]:
            names = [name.upper() for name in names]
        elif case_sensitive == 'lower':
            names = [name.lower() for name in names]
        elif case_sensitive in ['as-is', True]:
            pass
        else:
            raise ValueError("case_sensitive option '%s' is undefined." % case_sensitive)
        
        return names
    
    def dataframe_nans(self, df, missing_values='auto'):
        """missing_values is a dictionary.
        """
        # MAKE SURE COLUMN IS A FLOAT IF WE WANT TO INSERT NANS
        
        # Get a dictionary of missingVals on a per column basis
        if missing_values == 'auto':
            missingVals = self.missing_values()
        else:
            missingVals = self.missing_values(missing_values)
        
        for key, val in missingVals.iteritems():
            df[df.columns[key]] = df[df.columns[key]].replace(val, np.nan)
        
        return df
    
    def missing_values(self, flags=['LLOD_FLAG', 'ULOD_FLAG']):
        """Generates a dictionary of missing values on a per column basis.
        Option: flags; a list of strings with attribute names of missing data flags
                        that reside inside in a numpy object. The default flags
                        should work in most cases, and if they don't exist they are
                        ignored gracefully.
                        
        Returns: missingVals (dict); a per column list of missing values, with index
                                    value as key (int)
        
        key : string
            'int' or 'names'; 'int' returns integer key and 'names' returns column names.
        
        """
        # Make sure attributes exist
        otherFlags = []
        [flag.upper() for flag in flags]  # Ensure uppercase
        for flag in flags:
            try:
                otherFlags.append(str(getattr(self.header, flag)))
            except AttributeError:
                pass # Attribute doesn't exist
        
        # Column specific missing values
        missingVals = {} # Time column is never missing!
        for i, flag in enumerate(self.header.MISSING_DATA_FLAGS):
            # if key == 'names':
            key = i+1
            # elif key == 'int':
                # key = i+1
            missingVals[key] = str(flag).strip()
        
        # append missing flags to each column
        for key, value in missingVals.iteritems():
            j = list(otherFlags) # Copy list
            j.insert(0, value) # insert default missing flag first
            missingVals[key] = j # Reassign
        
        return missingVals
    
    def __repr__(self):
        return ("%s Data File (FFI = %i)\n%s" % 
                (self._file.data_format.upper(),
                 self.header.FFI,
                 self.header.FILENAME) )



class Header(object):
    "Generates header information for a Naspy object, requires Naspy object."
    def __init__(self, Naspy):
        
        fname = Naspy._fileAbsPath_
        self._fileObj_ = Naspy._file.open_file() # Attach fileObject
        self._fileAbsPath_ = os.path.abspath(fname) # full path to file
        self.FILENAME = os.path.split(fname)[1]
        self.parse_header(Naspy) # parse the header
        # self._parse_normal_comments_() # additional comments
        self._fileObj_.close()  # Make sure the file is closed when done
        return None
        
    # Entry point to header parser
    def parse_header(self, Naspy):
        if Naspy._file.data_format == 'ict':
            self.parse_header_ict()
            self._parse_normal_comments_()
        if Naspy._file.data_format == 'nas':
            raise AttributeError("NASA Ames file format is not currently supported")
        
        return None
        
    
    # TODO: create similar to parse NAS header; there are a few subtle differences between the NAS and ICT, so a seperate nas function is best
    def parse_header_ict(self):
        """Parses an ICT header and returns a naspy.header object. """
        # get the filetype and specify the seperator
        
        f = self._fileObj_
        self.HEADER_LINES, self.FFI = map(int, f.readline().split(','))
        self.PI = f.readline().strip()
        self.ORGANIZATION = f.readline().strip()
        self.DATA_DESCRIPTION = f.readline().strip()
        self.MISSION = f.readline().strip()
        self.FILE_VOL_NO, self.NO_VOL = map(int, f.readline().split(','))

        i = map(int, f.readline().split(','))
        self.START_UTC = datetime.datetime(i[0],i[1],i[2]) # UTC date when data begin
        self.REV_UTC =  datetime.date(i[3],i[4],i[5]) # UTC date of data red or rev

        self.DATA_INTERVAL = float(f.readline())
        
        # Generate a dictionary for INDEPENDENT_VARIABLE
        j = f.readline().strip().split(',') # Read Indepent_Variable line
        for k in range(len(j),3):  # Ensure all fields are filled
            try:
                j[k] = None
            except IndexError:
                j.append(None)
        self.INDEPENDENT_VARIABLE = {'NAME':j[0], 'UNITS':j[1], 'DESC':j[2]}  
        
        self.TOTAL_NUM_VARIABLES = int(f.readline().strip())+1
        self.SCALE_FACTORS = self.SCALE_FACTORS = map(float, f.readline().split(','))
        # self.MISSING_DATA_FLAGS = map(float, f.readline().split(','))
        self.MISSING_DATA_FLAGS = f.readline().strip().replace(" ","").split(',')

        # Create a dictionary for dependent variables
        DEP_VAR = []
        for i in range(1,self.TOTAL_NUM_VARIABLES):
            j = f.readline().strip().split(',')
            for k in range(len(j),3):  # Ensure all fields are filled
                try:
                    j[k] = None
                except IndexError:
                    j.append(None)
            DEP_VAR.append({'NAME':j[0], 'UNITS':j[1], 'DESC':j[2]})
        self.DEPENDENT_VARIABLE = DEP_VAR

        self.SPECIAL_COMMENT_LINES = int(f.readline().strip())

        SPECIAL_COMMENTS = []
        for i in range(self.SPECIAL_COMMENT_LINES):
            SPECIAL_COMMENTS.append(f.readline().strip())
        self.SPECIAL_COMMENTS = SPECIAL_COMMENTS

        self.NORMAL_COMMENT_LINES = int(f.readline().strip())

        NORMAL_COMMENTS = []
        for i in range(self.NORMAL_COMMENT_LINES):
            NORMAL_COMMENTS.append(f.readline().strip())
        self.NORMAL_COMMENTS = NORMAL_COMMENTS

        return None


    def _parse_normal_comments_(self):
        for i in self.NORMAL_COMMENTS:
            comment = i.split(':',1)
            if len(comment) == 2:
                setattr(self, comment[0].upper().strip(), comment[1].strip())
        return None
    
    ### ADDITIONAL HEADER FUNCTIONS
    # TODO: build up header funtions 
    
    def contact_info(self):
        print """
        PRIMARY INVESTIGATOR(S)
        ----------------------- 
        %s
        
        AFFILIATION
        ----------- 
        %s
        
        CONTACT INFO
        ------------
        %s
        """ % (self.PI, self.ORGANIZATION, self.PI_CONTACT_INFO)
        return None

    def data_description(self):
        pass
            


class Time(object):  # I don't know how to inherit properly here!
    """Class for time based methods."""
    def __init__(self, Naspy):
        self._fname = Naspy._fileAbsPath_
        self._START_UTC = Naspy.header.START_UTC
        self._HEADER_LINES = Naspy.header.HEADER_LINES
        
        return None
     
    def start_time(self):
        """Returns a datetime object of first datapoint."""
        startDate = self._START_UTC
        f = Fifo(self._fname).open_file()
        firstDataLine = f.readline()
        startOffset = datetime.timedelta(0, int(firstDataLine.split(',')[0]))
        startTime = startDate + startOffset
        f.close()
        return startTime
    
    """Returns datetime object of last datapoint."""    
    def end_time(self):
        startDate = self._START_UTC

        f = Fifo(self._fname).open_file()
        firstDataLine = f.readline()
        
        # Can't read backwards in a gzip file, so jury-rig it:
        if Fifo(self._fname).get_filetype()[1] == 'gzip':
            fsize = Fifo(self._fname).gzipFileSize()
            f.seek((fsize-fsize/20))
        else:
            f.seek(-len(firstDataLine)*10, 2)
        lastLine = f.readlines()[-1]
        endOffset = datetime.timedelta(0, int(lastLine.split(',')[0]))
        endTime = startDate + endOffset
        f.close()
        return endTime


        
class Fifo(object):
    """File input / File output handler class."""
    def __init__(self, Naspy):
        
        # may be redundant
        self.fileAbsPath = Naspy._fileAbsPath_
        self._userDefined_data_format = Naspy._data_format 
        self.filename = os.path.split(self.fileAbsPath)[1]
        # Bind file info to Naspy object
        comp, ext, dt = self.get_filetype()
        self.is_compressed = comp
        self.ext = ext
        self.data_format = dt
        return None
    
    # TODO: Redunant function, this functionality resides in get_filetype
    def is_compressed(self):
        """Determines whether the input file is compressed, returns a boolean object."""
        fname = self.fileAbsPath
        ext = os.path.splitext(fname)[-1].lower().lstrip('.')
        if ext in ['gzip', 'gz', 'bz2']:
            return True
        return False
        
    def get_filetype(self):
        """Returns a tuple (is_compressed, ext, data_format) {bool, 'str', 'str'} 
        indicating if the file is compressed, the file extension, and the data file type.
        
        RETURNS
        -------
        fileType : tuple, {is_compressed, ext, data_format}
            Filetype information of Naspy object:
            is_compressed : bool; compressed filetype
            ext : str; final extension of the file
            data_format : str; data file format type, regardless of compression
            
        """
        fname = self.fileAbsPath
        ext = os.path.splitext(fname)[-1].lower().lstrip('.') # force lower case
        if ext in ['gzip', 'gz', 'bz2']:
            is_compressed = True
        else:
            is_compressed = False
        
        # Always refer to 'gz' as 'gzip'
        if ext == 'gz':
            ext = 'gzip'
        
        # NOW the hard part, whether file is icarrt or nas
        # data_format = os.path.splitext(fname)[-2].lower().lstrip('.')
        # if self._userDefined_data_format == 'auto': 
        if self._userDefined_data_format == 'auto':
            # we actually need to check out what's going on in the file
            # open first line and parse first line, that will tell us
            f = self.open_file()
            line = f.readline().strip()
            f.close()
            
            if bool(re.search('(\d+),(\s)(\d+)*', line)):
                data_format = 'ict'
            elif bool(re.search('(\d+)(\s)(\d+)*', line)):
                data_format = 'nas'
            else:
                data_format = None
        else:
            data_format = self._userDefined_data_format 
            
        return (is_compressed, ext, data_format)
            
    def open_file(self):
        """Generates fileObj based on extension.
        
        This creates an open fileObj, it is up to you to close it when done with it. 
        Opens plain-text, gzipped, and bz2 files and returns a fileObject where standard
        file functionality is present (e.g. `f.readline()`)
        """
        fname = self.fileAbsPath
        
        ext = os.path.splitext(fname)[-1].lower() # force lower case
        # this is returning text file! or not working
        if ext in ['.gz','.gzip']:
            f = gzip.GzipFile(filename=fname, mode='rb')
        elif ext in ('.bz2'):
            f = bz2.BZ2File(fname, 'rU')
        else:
            f = open(fname, 'rU')
        return f
        
    def filetype_warnings(self):
        # Need to issue warning re .gz file type
        warningMessage = (
          "Gzipped filetypes are not fully supported.\nHeader information is available " 
          "through the header instance, however generating numpy arrays from gzipped is "           "not currently possible. Generating pandas.DataFrames IS SUPPORTED." )
        
        fname = self.fileAbsPath
        ext = os.path.splitext(fname)[-1].lower() # force lower case
        if ext in ['.gz','.gzip']:
            warnings.warn(warningMessage)
        else:
            return None

    def gzipFileSize(self):
        """return UNCOMPRESSED filesize of a gzipped file.
        
        source: http://code.activestate.com/lists/python-list/245777/
        """
        fo = open(self.fileAbsPath, 'rb')
        fo.seek(-4, 2)
        r = fo.read()
        fo.close()
        return struct.unpack('<I', r)[0]
        

##### END OF CLASSES       


          
    