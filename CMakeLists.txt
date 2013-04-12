cmake_minimum_required( VERSION 2.6 )
BRAINVISA_PROJECT()

find_package( brainvisa-cmake REQUIRED )

find_package( python )
find_package( Numpy )

BRAINVISA_COPY_PYTHON_DIRECTORY( "${CMAKE_CURRENT_SOURCE_DIR}/python"
                                 ${PROJECT_NAME} )
BRAINVISA_COPY_DIRECTORY( "${CMAKE_CURRENT_SOURCE_DIR}/bin"
                          bin
                          ${PROJECT_NAME} )
BRAINVISA_COPY_PYTHON_DIRECTORY( "${CMAKE_CURRENT_SOURCE_DIR}/brainvisa"
                                 ${PROJECT_NAME} )

