/**
 * @file bob/io/SoxReader.h
 * @date Tue Nov 12 11:54:30 CET 2013
 * @author Elie Khoury <elie.khoury@idiap.ch>
 *
 * @brief A class to help you read audio. This code is based on Sox 
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

#ifndef SOX_READER_H
#define SOX_READER_H

#include <string>
#include <blitz/array.h>
#include <stdint.h>

#include <bob/core/array.h>
extern "C" {
#include <sox.h>
}


namespace xbob { namespace sox {

  /**
   * SoxReader objects can read data from audio files. The current
   * implementation uses SOX which is a stable freely available
   * implementation for these tasks. You can read an entire audio in memory by
   * using the "load()" method.
   */
  class SoxReader {

    public:

      /**
       * Opens a new Sox stream for reading. The audio will be loaded if the
       * combination of format and codec are known to work and have been
       * tested, otherwise an exception is raised. If you set 'check' to
       * 'false', though, we will ignore this check.
       */
      SoxReader(const std::string& filename);

      /**
       * Destructor virtualization
       */
      virtual ~SoxReader();

      /**
       * Returns the name of the file I'm reading
       */
      inline const std::string& filename() const { return m_filename; }

      /**
       * Returns the sampling rate of the audio stream.
       */
      inline double rate() const { return m_rate; }

      /**
       * Returns the number of channels.
       */
      inline unsigned numberOfChannels() const { return m_nchannels; }
      
      /**
       * Returns the number of channels.
       */
      inline unsigned bitsPerSample() const { return m_bits_per_sample; }


      /**
       * Returns the number of samples.
       */
      inline unsigned numberOfSamples() const { return m_nsamples; }

      /**
       * Returns the flags: lossless (0), lossy once (1) or lossy twice (2).
       */
      //inline unsigned flags() const { return m_flags; }

      /**
       * Duration of the audio stream, in seconds
       */
      inline double duration() const { return m_duration; }

      /**
       * Returns the encoding name
       */
      inline const std::string& encodingName() const { return m_encoding_name; }
      
      /**
       * Returns the compression factor
       */
      inline double compressionFactor() const { return m_compression_factor; }

      /**
       * Returns the typing information for the audio file
       */
      inline const bob::core::array::typeinfo& type() const 
      { return m_typeinfo; }

      /**
       * Loads all of the audio stream in a blitz array organized in this way:
       * (rate, samples). The 'data' parameter will be
       * resized if required.
       *
       * The flag 'throw_on_error' controls the error reporting behavior when
       * reading. By default it is 'false', which means we **won't** report
       * problems reading this stream. We just silently truncate the file. If
       * you set it to 'true', we will report any errors through exceptions. No
       * matter what you chose here, it is your task to verify the return value
       * of this method matches the number of frames indicated by
       * numberOfFrames().
       *
       * The op
       */
      double load(blitz::Array<float,2>& data);

      /**
       * Loads all of the video stream in a buffer. Resizes the buffer if
       * the space and type are not good.
       *
       *
       * The flag 'throw_on_error' controls the error reporting behavior when
       * reading. By default it is 'false', which means we **won't** report
       * problems reading this stream. We just silently truncate the file. If
       * you set it to 'true', we will report any errors through exceptions. No
       * matter what you chose here, it is your task to verify the return value
       * of this method matches the number of frames indicated by
       * numberOfFrames().
       */
      double load(bob::core::array::interface& b);
      
      /**
      * Closes the file
      */
      void reset();
      

    private: //methods

      /**
       * Opens the previously set up Sox stream for the reader
       */
      void open(const std::string& filename);

    private: //our representation

      std::string m_filename; ///< the name of the file we are manipulating
      double m_rate; ///< sampling rate of the audio stream
      double m_duration; ///< in seconds, for the whole audio
      unsigned m_nchannels; ///< the number of channels 
      unsigned m_nsamples; ///< the number of samples
      unsigned m_bits_per_sample; ///< the number of bits per sample
      //unsigned m_flags; ///< flags for encoding type: lossless (0), lossy once (1) or lossy twice (2).
      std::string m_encoding_name; ///< encoding name of the audio file
      double m_compression_factor;
      bob::core::array::typeinfo m_typeinfo; ///< read the audio type
      sox_format_t *m_infile_cache; /* input file */
      sox_signalinfo_t m_signal_cache;
      uint64_t m_offset;
  };

}}

#endif //SOX_READER_H
