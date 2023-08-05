#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
# @date: Wed May 8 19:42:39 CEST 2013
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

class Database():
  """Wrapper class for the MNIST database of handwritten digits (http://yann.lecun.com/exdb/mnist/).
  """

  def __init__(self, data_dir = None):
    """Creates the database. The data_dir argument should be the path to the directory
    containing the four binary files available from http://yann.lecun.com/exdb/mnist/"""
    # initialize members
    import os
    self.m_labels = set(range(0,10))
    self.m_groups = ('train', 'test')
    self.m_data_dir = data_dir
    self.m_train_fname_images = os.path.join(self.m_data_dir, 'train-images-idx3-ubyte.gz')
    self.m_train_fname_labels = os.path.join(self.m_data_dir, 'train-labels-idx1-ubyte.gz')
    self.m_test_fname_images  = os.path.join(self.m_data_dir, 't10k-images-idx3-ubyte.gz')
    self.m_test_fname_labels  = os.path.join(self.m_data_dir, 't10k-labels-idx1-ubyte.gz')

  def __read_labels__(self, fname):
    """Reads the labels from the original MNIST label binary file"""
    import struct, gzip, numpy
    with gzip.GzipFile(fname, 'rb') as f: 
      # reads 2 big-ending integers 
      magic_nr, n_examples = struct.unpack(">II", f.read(8)) 
      # reads the rest, using an uint8 dataformat (endian-less) 
      labels = numpy.fromstring(f.read(), dtype='uint8')
    return labels
  
  def __read_images__(self, fname):
    """Reads the images from the original MNIST label binary file"""
    import struct, gzip, numpy
    with gzip.GzipFile(fname, 'rb') as f: 
      # reads 4 big-ending integers 
      magic_nr, n_examples, rows, cols = struct.unpack(">IIII", f.read(16)) 
      shape = (n_examples, rows*cols) 
      # reads the rest, using an uint8 dataformat (endian-less) 
      images = numpy.fromstring(f.read(), dtype='uint8').reshape(shape)
    return images

  def __check_parameters_for_validity__(self, parameters, parameter_description, valid_parameters, default_parameters = None):
    """Checks the given parameters for validity, i.e., if they are contained in the set of valid parameters.
    It also assures that the parameters form a tuple or a list.
    If parameters is 'None' or empty, the default_parameters will be returned (if default_parameters is omitted, all valid_parameters are returned).

    This function will return a tuple or list of parameters, or raise a ValueError.

    Keyword parameters:

    parameters
      The parameters to be checked.
      Might be a string, a list/tuple of strings, or None.

    parameter_description
      A short description of the parameter.
      This will be used to raise an exception in case the parameter is not valid.

    valid_parameters
      A list/tuple of valid values for the parameters.

    default_parameters
      The list/tuple of default parameters that will be returned in case parameters is None or empty.
      If omitted, all valid_parameters are used.
    """
    if not parameters:
      # parameters are not specified, i.e., 'None' or empty lists
      parameters = default_parameters if default_parameters is not None else valid_parameters

    if not isinstance(parameters, (list, tuple, set)):
      # parameter is just a single element, not a tuple or list -> transform it into a tuple
      parameters = (parameters,)

    # perform the checks
    for parameter in parameters:
      if parameter not in valid_parameters:
        raise ValueError, "Invalid %s '%s'. Valid values are %s, or lists/tuples of those" % (parameter_description, parameter, valid_parameters)

    # check passed, now return the list/tuple of parameters
    return parameters

  def labels(self):
    """Returns the vector of labels
    """
    return self.m_labels

  def groups(self):
    """Returns the vector of groups
    """
    return self.m_groups

  def data(self, groups=None, labels=None):
    """Loads the MNIST samples and labels and returns them in NumPy arrays

    Keyword Parameters:

    groups
      One of the groups 'train' or 'test' or a list with both of them (which is the default).

    labels
      A subset of the labels (digits 0 to 9) (everything is the default).

    Returns: A tuple  composed of images and labels as 2D numpy arrays considering
      all the filtering criteria and organized as follows:

    images
      A 2D numpy.ndarray with as many rows as examples in the dataset, as many
      columns as pixels (actually, there are 28x28 = 784 rows). The pixels of each
      image are unrolled in C-scan order (i.e., first row 0, then row 1, etc.).

    labels
      A 1D numpy.ndarray with as many elements as examples in the dataset.
    """

    # check if groups set are valid
    groups = self.__check_parameters_for_validity__(groups, "group", self.m_groups)
    vlabels = self.__check_parameters_for_validity__(labels, "label", self.m_labels)

    # Reads data from the groups
    import numpy
    if 'train' in groups and 'test' in groups:
      images1 = self.__read_images__(self.m_train_fname_images)
      labels1 = self.__read_labels__(self.m_train_fname_labels)
      images2 = self.__read_images__(self.m_test_fname_images)
      labels2 = self.__read_labels__(self.m_test_fname_labels)
      images = numpy.hstack([images1,images2])
      labels = numpy.hstack([labels1,labels2])
    elif 'train' in groups:
      images = self.__read_images__(self.m_train_fname_images)
      labels = self.__read_labels__(self.m_train_fname_labels)
    elif 'test' in groups:
      images = self.__read_images__(self.m_test_fname_images)
      labels = self.__read_labels__(self.m_test_fname_labels)
    else:
      images = numpy.ndarray(shape=(0,784), dtype=numpy.uint8)
      labels = numpy.ndarray(shape=(0,), dtype=numpy.uint8)

    # List of indices for which the labels are in the list of requested labels
    indices = numpy.where(numpy.in1d(labels, vlabels))[0]
    images = images[indices,:]
    labels = labels[indices]

    return images, labels

