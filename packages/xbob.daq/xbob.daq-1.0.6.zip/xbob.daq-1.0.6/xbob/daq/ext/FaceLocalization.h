/**
 * @file FaceLocalization.h
 * @date Thu Feb 2 11:22:57 2012 +0100
 * @author Francois Moulin <Francois.Moulin@idiap.ch>
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
#ifndef FACERECOGNTION_H
#define FACERECOGNTION_H

#include "Callbacks.h"
#include <vector>

namespace xbob { namespace daq {

/**
 * @c FaceLocalization is an abstract class which provides face localization
 */
class FaceLocalization : public ControllerCallback {
public:
  FaceLocalization();
  virtual ~FaceLocalization();

  /**
   * Start the face localization of incoming frames
   */
  virtual bool start() = 0;
  
  void addFaceLocalizationCallback(FaceLocalizationCallback& callback);
  void removeFaceLocalizationCallback(FaceLocalizationCallback& callback);
  
protected:
  std::vector<FaceLocalizationCallback*> callbacks;
  pthread_mutex_t callbacks_mutex;
};

}}
#endif // FACERECOGNTION_H
