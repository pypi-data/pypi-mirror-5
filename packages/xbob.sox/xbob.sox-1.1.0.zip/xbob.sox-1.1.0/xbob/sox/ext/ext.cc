/**
 * @file io/python/sox.cc
 * @date Thu Nov 14 22:20:18 CET 2013
 * @author Elie Khoury <elie.khoury@idiap.ch>
 *
 * @brief Binds Sox constructions to python
 *
 * Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, version 3 of the License.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <boost/python.hpp>
#include <boost/python/slice.hpp>

#include <bob/config.h>
#include <bob/python/exception.h>
#include <bob/python/ndarray.h>
#include <bob/python/gil.h>


#include "reader.h"
#include "writer.h"
extern "C" {
#include <sox.h>
}

using namespace boost::python;

static object soxreader_load(xbob::sox::SoxReader& reader) {
  bob::python::py_array tmp(reader.type());
  float sampling_rate = 0.;
  sampling_rate = reader.load(tmp);
  return make_tuple(sampling_rate, tmp.pyobject());
}

BOOST_PYTHON_FUNCTION_OVERLOADS(soxreader_load_overloads, soxreader_load, 1, 1)


static void soxwriter_append(xbob::sox::SoxWriter& writer, bob::python::const_ndarray input_samples) {
  // Gets the shape of the input 
  const blitz::Array<float,2> input_ = input_samples.bz<float,2>();
  writer.append(input_);
}

static void soxwriter_save(xbob::sox::SoxWriter& writer, bob::python::const_ndarray input_samples) {
  // Gets the shape of the input 
  const blitz::Array<float,2> input_ = input_samples.bz<float,2>();
  writer.append(input_);
  //Then close
  writer.close();
}



BOOST_PYTHON_MODULE(_ext) {
  bob::python::setup_python("Audio reader and writer using sox for bob and python");
  
  class_<xbob::sox::SoxReader, boost::shared_ptr<xbob::sox::SoxReader> >("reader", 
  "SoxReader objects can read data from audio files. The current implementation uses `Sox <http://sox.sourceforge.net/>`_.", 
  init<const std::string& >((arg("self"), arg("filename")), 
  "Initializes a new SoxReader object by giving the input file path to read. Information related to the audio file (encoding, rate, etc.) will be extracted from the audio metadata, automatically, by ``Sox``."))
    .add_property("filename", make_function(&xbob::sox::SoxReader::filename, return_value_policy<copy_const_reference>()), "The full path to the file that will be decoded by this object")
    .add_property("rate", &xbob::sox::SoxReader::rate, "The sampling rate of the audio file")
    .add_property("duration", &xbob::sox::SoxReader::duration, "The total duration of the audio file")
    .add_property("number_of_samples", &xbob::sox::SoxReader::numberOfSamples, "The number of samples in this audio file")
    .def("__len__", &xbob::sox::SoxReader::numberOfSamples, "The number of samples in this audio file")
    .add_property("nchannels", &xbob::sox::SoxReader::numberOfChannels, "The number of channels in the audio file")
    .add_property("bits_per_sample", &xbob::sox::SoxReader::bitsPerSample, "the number of bits per sample of the audio file")
    .add_property("encoding_name", make_function(&xbob::sox::SoxReader::encodingName, return_value_policy<copy_const_reference>()), "The name of the encoder of the audio file")
    .add_property("compression_factor", &xbob::sox::SoxReader::compressionFactor, "The compression factor of the audio file")
    .def("reset", &xbob::sox::SoxReader::reset, (arg("self")), "reset the current sox stream.")
    
    //.add_property("type", make_function(&xbob::sox::SoxReader::type, return_value_policy<copy_const_reference>()), "Typing information to load the file")
    .def("load", &soxreader_load, soxreader_load_overloads((arg("self")), "Loads the audio stream in a numpy ndarray organized in this way:  I'll dynamically allocate the output array and return it to you. The flag ``raise_on_error``, which is set to ``False`` by default influences the error reporting in case problems are found with the sox file. If you set it to ``True``, we will report problems raising exceptions. If you either don't set it or set it to ``False``, we will truncate the file at the frame with problems and will not report anything. It is your task to verify if the number of frames returned matches the expected number of frames as reported by the property ``number_of_frames`` in this object."))
    ;

  class_<xbob::sox::SoxWriter, boost::shared_ptr<xbob::sox::SoxWriter>, boost::noncopyable>("writer",
     "Use objects of this class to create and write sox files using `Sox <http://sox.sourceforge.net/>.`_.",
     init<const std::string&, const float, optional<const std::string&, const unsigned> >((arg("self"), arg("filename"), arg("rate"), arg("encoding_name")="Unknown", arg("bits_per_sample")=16), "Creates a new output file given the input parameters. The format and codec to be used will be derived from the filename extension unless the encoding is precised in the optional argument. \n\n The possible file extensions:\nvoc , smp , wve, gsrt, amr-wb, prc , sph , amr-nb, txw , sndt , vorbis, speex , hcom , wav , aiff , aifc , 8svx , maud , xa , au , flac , avr , caf , wv , paf , sf , sox. \n \n The possible encoding names are:\nSIGN2, UNSIGNED, FLOAT, FLOAT_TEXT, FLAC, HCOM, WAVPACK, WAVPACKF, ULAW, ALAW, G721, G723, CL_ADPCM, CL_ADPCM16, MS_ADPCM, IMA_ADPCM, OKI_ADPCM, DPCM, DWVW, DWVWN, GSM, MP3, VORBIS, AMR_WB, AMR_NB, CVSD, LPC10.\n"))
    .add_property("filename", make_function(&xbob::sox::SoxWriter::filename, return_value_policy<copy_const_reference>()), "The full path to the file that will be decoded by this object")
    .add_property("rate", &xbob::sox::SoxWriter::rate, "The sampling rate of the audio file")
    .add_property("bits_per_sample", &xbob::sox::SoxWriter::bitsPerSample, "the number of bits per sample of the audio file")
    .add_property("encoding_name", make_function(&xbob::sox::SoxWriter::encodingName, return_value_policy<copy_const_reference>()), "The name of the encoder of the audio file")
    .add_property("duration", &xbob::sox::SoxWriter::duration, "The total duration of the audio file")
    .add_property("number_of_samples", &xbob::sox::SoxWriter::numberOfSamples, "The number of samples in this audio file")
    .def("__len__", &xbob::sox::SoxWriter::numberOfSamples, "The number of samples in this audio file")
    .add_property("nchannels", make_function(&xbob::sox::SoxWriter::numberOfChannels), "The number of channels in the audio file")
    .add_property("compression_factor", &xbob::sox::SoxWriter::compressionFactor, "The compression factor of the audio file")
    .add_property("type", make_function(&xbob::sox::SoxWriter::type, return_value_policy<copy_const_reference>()), "Typing information to load the file")
    .add_property("is_opened", &xbob::sox::SoxWriter::is_opened, "A boolean flag, indicating if the sox is still opened for writing (or has already been closed by the user using ``close()``)")
    .def("close", &xbob::sox::SoxWriter::close, (arg("self")), "Closes the current sox stream and forces writing the trailer. After this point the sox is finalized and cannot be written to anymore.")
    .def("append", &soxwriter_append, (arg("self"), arg("samples")), "Writes a new sample or set of samples to the file. The set of samples should be setup as an array with 2 dimensions.\n\n.. note::\n\n  At present time we only support arrays that have C-style storages (if you pass reversed arrays or arrays with Fortran-style storage, the result is undefined).")
    .def("save", &soxwriter_save, (arg("self"), arg("samples")), "Writes a new sample or set of samples to the file. The set of samples should be setup as an array with 2 dimensions.\n\n.. note::\n\n  At present time we only support arrays that have C-style storages (if you pass reversed arrays or arrays with Fortran-style storage, the result is undefined).")
    ;
 
  scope().attr("version") = sox_version();
}
