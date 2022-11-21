cmake_minimum_required( VERSION 3.10 )

find_package( brainvisa-cmake REQUIRED )
BRAINVISA_FIND_PACKAGE( brainvisa-share REQUIRED )
BRAINVISA_FIND_PACKAGE( axon REQUIRED )
BRAINVISA_PROJECT()

BRAINVISA_DEPENDENCY( RUN DEPENDS "axon" RUN "= ${axon_VERSION}" )
BRAINVISA_DEPENDENCY( RUN RECOMMENDS "anatomist-gpl" RUN "= ${anatomist-gpl_VERSION}" )
BRAINVISA_DEPENDENCY( DEV RECOMMENDS "anatomist-gpl" DEV "= ${anatomist-gpl_VERSION}" )
BRAINVISA_DEPENDENCY( RUN RECOMMENDS "constellation-nonfree" RUN "= ${constellation-nonfree_VERSION}" )

BRAINVISA_COPY_PYTHON_DIRECTORY( "${CMAKE_CURRENT_SOURCE_DIR}/python"
                                 ${PROJECT_NAME} )

BRAINVISA_COPY_DIRECTORY( "${CMAKE_CURRENT_SOURCE_DIR}/bin"
                          bin
                          ${PROJECT_NAME} )

BRAINVISA_COPY_PYTHON_DIRECTORY( "${CMAKE_CURRENT_SOURCE_DIR}/brainvisa"
                                 ${PROJECT_NAME} )

BRAINVISA_COPY_DIRECTORY( "${CMAKE_CURRENT_SOURCE_DIR}/share/doc/images"
                          share/doc/axon-${axon_VERSION_MAJOR}.${axon_VERSION_MINOR}/images
                          ${PROJECT_NAME} )

BRAINVISA_COPY_DIRECTORY( "${CMAKE_CURRENT_SOURCE_DIR}/share-data"
                          share/brainvisa-share-${brainvisa-share_VERSION_MAJOR}.${brainvisa-share_VERSION_MINOR}
                          ${PROJECT_NAME} )

set( CONSTEL_ATLAS_DOWNLOAD_SOURCE "ftp:///ftp.cea.fr/pub/dsv/anatomist/data" CACHE FILEPATH "URL for Constellation atlas data download" )

set( get_models_cmd
  "${CMAKE_CURRENT_SOURCE_DIR}/scripts/bv_get_constel_atlas.py" )
add_custom_target( get-constel-atlas ALL
  COMMAND "${PYTHON_HOST_EXECUTABLE}" "${get_models_cmd}" "-o" "${CMAKE_BINARY_DIR}/share/constellation-${BRAINVISA_PACKAGE_VERSION_MAJOR}.${BRAINVISA_PACKAGE_VERSION_MINOR}" "-i" "${CONSTEL_ATLAS_DOWNLOAD_SOURCE}"
  "--timeout" "5" "--silent" "--check"
  )
add_custom_target( install-constel-atlas
  COMMAND "${CMAKE_COMMAND}" "-E" "copy_directory" "${CMAKE_BINARY_DIR}/share/constellation-${BRAINVISA_PACKAGE_VERSION_MAJOR}.${BRAINVISA_PACKAGE_VERSION_MINOR}/constellation_atlas_hcp_200s" "$(BRAINVISA_INSTALL_PREFIX)/share/constellation-${BRAINVISA_PACKAGE_VERSION_MAJOR}.${BRAINVISA_PACKAGE_VERSION_MINOR}/constellation_atlas_hcp_200s"
  )

add_dependencies( install-constellation-gpl install-constel-atlas )

# ensure the installed database file is newer than the rest - rebuild it after
# all toolboxes are installed
add_custom_target( constel_install_shared_index
    COMMAND if [ -f \"$(BRAINVISA_INSTALL_PREFIX)/bin/bv_env\" ] \; then "$(BRAINVISA_INSTALL_PREFIX)/bin/bv_env" "axon-runprocess" "--enabledb" "updateDatabases" "databases=[\\'$(BRAINVISA_INSTALL_PREFIX)/share/constellation-${BRAINVISA_PACKAGE_VERSION_MAJOR}.${BRAINVISA_PACKAGE_VERSION_MINOR}/constellation_atlas_hcp_200s/constellation_matrix\\', \\'$(BRAINVISA_INSTALL_PREFIX)/share/constellation-${BRAINVISA_PACKAGE_VERSION_MAJOR}.${BRAINVISA_PACKAGE_VERSION_MINOR}/constellation_atlas_hcp_200s/freesurfer_gyri\\']" \; fi
)

add_dependencies( post-install constel_install_shared_index )

BRAINVISA_CREATE_CMAKE_CONFIG_FILES()
