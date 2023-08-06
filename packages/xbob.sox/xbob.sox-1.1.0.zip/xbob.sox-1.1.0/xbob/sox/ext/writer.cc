/**
 * @file io/cxx/SoxWriter.cc
 * @date Tue Nov 12 11:54:30 CET 2013
 * @author Elie Khoury <elie.khoury@idiap.ch>
 *
 * @brief A class to help you write audio. This code is based on Sox 
 * <http://sox.sourceforge.net/>.
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

#include <boost/format.hpp>
#include <boost/preprocessor.hpp>
#include <bob/core/blitz_array.h>
#include <bob/core/logging.h>
#include <limits>
extern "C" {
#include <sox.h>
}

#include "utilities.h"
#include "writer.h"


xbob::sox::SoxWriter::SoxWriter(
    const std::string& filename,
    double       rate, 
    const std::string& encoding_name,
    unsigned bits_per_sample
) :
  
  m_filename(filename),
  m_opened(false),
  m_rate(rate),
  m_encoding_name(encoding_name),
  m_bits_per_sample(bits_per_sample)
{

  m_signal_cache.rate = m_rate;
  m_signal_cache.precision=m_bits_per_sample;
  m_signal_cache.channels=0;  
  m_signal_cache.length=0;
  m_nsamples=0;
  m_nchannels=0;

  sox_encodinginfo_t encoding_info; 
  encoderStringToType(m_encoding_name, &m_encoding_cache);
  encoding_info.encoding = m_encoding_cache; 
  encoding_info.bits_per_sample = m_bits_per_sample;
  encoding_info.compression =HUGE_VAL;
  
#if SOX_LIB_VERSION_CODE >= SOX_LIB_VERSION(14,4,0)
  encoding_info.reverse_bytes = sox_option_default;
  encoding_info.reverse_nibbles = sox_option_default;
  encoding_info.reverse_bits = sox_option_default;
#else
  encoding_info.reverse_bytes = SOX_OPTION_DEFAULT;
  encoding_info.reverse_nibbles = SOX_OPTION_DEFAULT;
  encoding_info.reverse_bits = SOX_OPTION_DEFAULT;
#endif
  
  
  
  if (encoding_info.encoding == SOX_ENCODING_UNKNOWN)
  {
    const char *filetype=lsx_find_file_extension(m_filename.c_str()); 
    m_outfile_cache = sox_open_write(m_filename.c_str(), &m_signal_cache, NULL, filetype, NULL, NULL);
  }
  else
    m_outfile_cache = sox_open_write(m_filename.c_str(), &m_signal_cache, &encoding_info, NULL, NULL, NULL);
  
  m_compression_factor = encoding_info.compression;
  m_opened = true; ///< file is now considered opened for business
}


void xbob::sox::SoxWriter::append(const blitz::Array<float,2>& data) {

  m_nchannels = data.extent(0);
  m_nsamples =  m_nsamples + data.extent(1);
  m_typeinfo.update_strides();

  m_signal_cache.channels = (unsigned) m_nchannels;
  m_signal_cache.length = m_nsamples * m_nchannels;
  
  sox_sample_t *row_pointer= (sox_sample_t *) malloc(sizeof(sox_sample_t) *m_nchannels);
   
  for (int i=0; i<(int)m_nsamples; i++)
  {
    //now we copy from one container to the other, using our Blitz++ technique
    for (int j=0; j<(int)m_nchannels; j++)
    {
      row_pointer[j] = (sox_sample_t) (int)(data(j, i) * SOX_CONVERSION_COEF);
    }
    sox_write(m_outfile_cache, row_pointer, m_nchannels);
  }
  m_duration = (double)m_nsamples/m_rate;
  free(row_pointer);
  
}

xbob::sox::SoxWriter::~SoxWriter() {
  close();
}

void xbob::sox::SoxWriter::close() {

  if (!m_opened) return;
  sox_close(m_outfile_cache);
  m_opened = false; ///< file is now considered closed
}


