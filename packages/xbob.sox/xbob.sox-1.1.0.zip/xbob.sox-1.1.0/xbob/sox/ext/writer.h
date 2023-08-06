/**
 * @file bob/io/SoxWriter.h
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

#ifndef SOX_WRITER_H
#define SOX_WRITER_H

#include <bob/core/array.h>
extern "C" {
#include <sox.h>
}

namespace xbob { namespace sox {

  /**
   * Use objects of this class to create and write video files.
   */
  class SoxWriter {

    public:

      /**
       * Default constructor, creates a new output file given the input
       * parameters. The codec to be used will be derived from the filename
       * extension.
       *
       * @param filename The name of the file that will contain the video
       * output. If it exists, it will be truncated.
       * @param height The height of the video
       * @param width The width of the video
       * @param framerate The number of frames per second
       * @param bitrate The estimated bitrate of the output video
       * @param gop Group-of-Pictures (emit one intra frame every `gop' frames
       * at most)
       * @param codec If you must, specify a valid FFmpeg codec name here and
       * that will be used to encode the video stream on the output file.
       * @param format If you must, specify a valid FFmpeg output format name
       * and that will be used to encode the video on the output file. Leave
       * it empty to guess from the filename extension.
       * @param check The video will be created if the combination of format
       * and codec are known to work and have been tested, otherwise an
       * exception is raised. If you set 'check' to 'false', though, we will
       * ignore this check.
       */
      SoxWriter(const std::string& filename, double rate, const std::string& encoding_name="Unknown", unsigned bits_per_sample=16);

      /**
       * Destructor virtualization
       */
      virtual ~SoxWriter();

      /**
       * Closes the current video stream and forces writing the trailer. After
       * this point the video becomes invalid.
       */
      void close();

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
      inline unsigned numberOfChannels() { return m_nchannels; }
      
      /**
       * Returns the number of channels.
       */
      inline unsigned bitsPerSample() { return m_bits_per_sample; }

      /**
       * Returns the number of samples.
       */
      inline unsigned numberOfSamples() { return m_nsamples; }

      /**
       * Duration of the audio stream, in seconds
       */
      inline double duration() { return m_duration; }

      /**
       * Returns the encoding name
       */
      inline const std::string& encodingName() const { return m_encoding_name; }
      
      /**
       * Returns the compression factor
       */
      inline double compressionFactor() { return m_compression_factor; }

      /**
       * Returns the typing information for the audio file
       */
      inline const bob::core::array::typeinfo& type() { return m_typeinfo; }

      /**
       * Returns if the video is currently opened for writing
       */
      inline bool is_opened() { return m_opened; }
      
      /**
       * Writes a set of samples to the file. The sample set should be setup as a
       * blitz::Array<> with 2 dimensions.
       * 
       *
       * \warning At present time we only support arrays that have C-style
       * storages (if you pass reversed arrays or arrays with Fortran-style
       * storage, the result is undefined).
       */
      void append(const blitz::Array<float,2>& data);
    
      /**
       * Writes a set of frames to the file.
       */
      void append(bob::core::array::interface& data);
      

    private: //representation
      
      std::string m_filename; ///< the name of the file we are manipulating
      bool m_opened; ///< is the file currently opened?
      bool m_check; ///< shall I check for compatibility when opening?
      double m_rate; ///< sampling rate of the audio stream
      double m_duration; ///< in seconds, for the whole audio
      unsigned m_nchannels; ///< the number of channels 
      unsigned m_nsamples; ///< the number of samples
      std::string m_encoding_name; ///< encoding name of the audio file
      unsigned m_bits_per_sample; ///< the number of bits per sample
      //unsigned m_flags; ///< flags for encoding type: lossless (0), lossy once (1) or lossy twice (2).
      double m_compression_factor;
      bob::core::array::typeinfo m_typeinfo; ///< read the audio type
      sox_format_t *m_outfile_cache; /* input file */
      sox_signalinfo_t m_signal_cache;
      sox_encoding_t m_encoding_cache;
  };

}}

#endif /* SOX_WRITER_H */
