/**
 * @file bob/io/SoxReader.h
 * @date Thu Nov 14 20:46:52 CET 2013
 * @author Elie Khoury <elie.khoury@idiap.ch>
 *
 * @brief A class for some utilities using sox. This code is based on Sox 
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


#include <stdexcept>
#include <boost/format.hpp>
#include <boost/preprocessor.hpp>
#include <limits>
#include <bob/core/check.h>
#include <bob/core/blitz_array.h>
#include <bob/core/logging.h>
#include <assert.h>
extern "C" {
#include <sox.h>
}

#include "utilities.h"


void xbob::sox::encoderTypeToString(const sox_encoding_t encoding, std::string& encoding_name) { 
  switch (encoding) {
      case SOX_ENCODING_SIGN2       :   encoding_name = "SIGN2";     break;
      case SOX_ENCODING_UNSIGNED    :   encoding_name = "UNSIGNED";     break;
      case SOX_ENCODING_FLOAT       :   encoding_name = "FLOAT";     break;
      case SOX_ENCODING_FLOAT_TEXT  :   encoding_name = "FLOAT_TEXT";     break;
      case SOX_ENCODING_FLAC        :   encoding_name = "FLAC";     break;
      case SOX_ENCODING_HCOM        :   encoding_name = "HCOM";     break;
      case SOX_ENCODING_WAVPACK     :   encoding_name = "WAVPACK";     break;
      case SOX_ENCODING_WAVPACKF    :   encoding_name = "WAVPACKF";     break;
      case SOX_ENCODING_ULAW        :   encoding_name = "ULAW";     break;
      case SOX_ENCODING_ALAW        :   encoding_name = "ALAW";     break;
      case SOX_ENCODING_G721        :   encoding_name = "G721";     break;
      case SOX_ENCODING_G723        :   encoding_name = "G723";     break;
      case SOX_ENCODING_CL_ADPCM    :   encoding_name = "CL_ADPCM";     break;
      case SOX_ENCODING_CL_ADPCM16  :   encoding_name = "CL_ADPCM16";     break;
      case SOX_ENCODING_MS_ADPCM    :   encoding_name = "MS_ADPCM";     break;
      case SOX_ENCODING_IMA_ADPCM   :   encoding_name = "IMA_ADPCM";     break;
      case SOX_ENCODING_OKI_ADPCM   :   encoding_name = "OKI_ADPCM";     break;
      case SOX_ENCODING_DPCM        :   encoding_name = "DPCM";     break;
      case SOX_ENCODING_DWVW        :   encoding_name = "DWVW";     break;
      case SOX_ENCODING_DWVWN       :   encoding_name = "DWVWN";     break;
      case SOX_ENCODING_GSM         :   encoding_name = "GSM";     break;
      case SOX_ENCODING_MP3         :   encoding_name = "MP3";     break;
      case SOX_ENCODING_VORBIS      :   encoding_name = "VORBIS";     break;
      case SOX_ENCODING_AMR_WB      :   encoding_name = "AMR_WB";     break;
      case SOX_ENCODING_AMR_NB      :   encoding_name = "AMR_NB";     break;
      case SOX_ENCODING_CVSD        :   encoding_name = "CVSD";     break;
      case SOX_ENCODING_LPC10       :   encoding_name = "LPC10";     break;
      case SOX_ENCODING_UNKNOWN     :   encoding_name = "Unknown";     break;      
      default                       :   encoding_name = "Unknown";
  }    
} 

void xbob::sox::encoderStringToType(const std::string& encoding_name, sox_encoding_t* encoding ) {
      if (encoding_name =="SIGN2")      *encoding = SOX_ENCODING_SIGN2 ;     
      if (encoding_name =="UNSIGNED")   *encoding = SOX_ENCODING_UNSIGNED  ;     
      if (encoding_name =="FLOAT")      *encoding =SOX_ENCODING_FLOAT  ;     
      if (encoding_name =="FLOAT_TEXT") *encoding = SOX_ENCODING_FLOAT_TEXT  ;     
      if (encoding_name =="FLAC")       *encoding = SOX_ENCODING_FLAC  ;     
      if (encoding_name =="HCOM")       *encoding = SOX_ENCODING_HCOM  ;     
      if (encoding_name =="WAVPACK" )   *encoding = SOX_ENCODING_WAVPACK  ;     
      if (encoding_name =="WAVPACKF" )  *encoding = SOX_ENCODING_WAVPACKF  ;     
      if (encoding_name =="ULAW" )      *encoding = SOX_ENCODING_ULAW;     
      if (encoding_name =="ALAW" )      *encoding = SOX_ENCODING_ALAW ;     
      if (encoding_name =="G721" )      *encoding = SOX_ENCODING_G721 ;     
      if (encoding_name =="G723" )      *encoding = SOX_ENCODING_G723 ;     
      if (encoding_name =="CL_ADPCM")   *encoding = SOX_ENCODING_CL_ADPCM ;     
      if (encoding_name =="CL_ADPCM16") *encoding = SOX_ENCODING_CL_ADPCM16;     
      if (encoding_name =="MS_ADPCM")   *encoding = SOX_ENCODING_MS_ADPCM ;     
      if (encoding_name =="IMA_ADPCM")  *encoding = SOX_ENCODING_IMA_ADPCM ;     
      if (encoding_name =="OKI_ADPCM")  *encoding = SOX_ENCODING_OKI_ADPCM ;     
      if (encoding_name =="DPCM")       *encoding = SOX_ENCODING_DPCM ;     
      if (encoding_name =="DWVW")       *encoding = SOX_ENCODING_DWVW  ;     
      if (encoding_name =="DWVWN")      *encoding = SOX_ENCODING_DWVWN ;     
      if (encoding_name =="GSM")        *encoding = SOX_ENCODING_GSM ;     
      if (encoding_name =="MP3")        *encoding = SOX_ENCODING_MP3;     
      if (encoding_name =="VORBIS")     *encoding = SOX_ENCODING_VORBIS ;     
      if (encoding_name =="AMR_WB")     *encoding = SOX_ENCODING_AMR_WB;     
      if (encoding_name =="AMR_NB")     *encoding = SOX_ENCODING_AMR_NB;     
      if (encoding_name =="CVSD")       *encoding = SOX_ENCODING_CVSD;     
      if (encoding_name =="LPC10")      *encoding = SOX_ENCODING_LPC10;     
      if (encoding_name =="Unknown" )   *encoding = SOX_ENCODING_UNKNOWN;                   
} 

