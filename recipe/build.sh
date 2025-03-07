if [[ ${FEATURE_DEBUG} = 1 ]]; then
      BUILD_TYPE="Debug"
else
      BUILD_TYPE="Release"
fi

declare -a CMAKE_PLATFORM_FLAGS

if [[ ${HOST} =~ .*linux.* && ${USE_QT6} = "0" ]]; then
  echo "adding hacks for linux"

  # temporary workaround for qt-cmake:
  sed -i 's|_qt5gui_find_extra_libs(EGL.*)|_qt5gui_find_extra_libs(EGL "EGL" "" "")|g' $PREFIX/lib/cmake/Qt5Gui/Qt5GuiConfigExtras.cmake
  sed -i 's|_qt5gui_find_extra_libs(OPENGL.*)|_qt5gui_find_extra_libs(OPENGL "GL" "" "")|g' $PREFIX/lib/cmake/Qt5Gui/Qt5GuiConfigExtras.cmake
  CMAKE_PLATFORM_FLAGS+=(-DCMAKE_TOOLCHAIN_FILE="${RECIPE_DIR}/cross-linux.cmake")
fi


if [[ ${HOST} =~ .*darwin.* && ${USE_QT6} = "0" ]]; then
  # add hacks for osx here!
  echo "adding hacks for osx"
  
  ln -s /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.13.sdk /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.9.sdk
  ln -s /Applications/Xcode.app /Applications/Xcode_11.7.app

  # install space-mouse
  if [[ ${target_platform} =~ osx-64 ]]; then
    /usr/bin/curl -o /tmp/3dFW.dmg -L 'https://download.3dconnexion.com/drivers/mac/10-6-6_360DF97D-ED08-4ccf-A55E-0BF905E58476/3DxWareMac_v10-6-6_r3234.dmg'
  else
    /usr/bin/curl -o /tmp/3dFW.dmg -L 'https://download.3dconnexion.com/drivers/mac/10-7-0_B564CC6A-6E81-42b0-82EC-418EA823B81A/3DxWareMac_v10-7-0_r3411.dmg'
  fi
  hdiutil attach -readonly /tmp/3dFW.dmg
  sudo installer -package /Volumes/3Dconnexion\ Software/Install\ 3Dconnexion\ software.pkg -target /
  diskutil eject /Volumes/3Dconnexion\ Software
  CMAKE_PLATFORM_FLAGS+=(-DFREECAD_USE_3DCONNEXION:BOOL=ON)
  CMAKE_PLATFORM_FLAGS+=(-D3DCONNEXIONCLIENT_FRAMEWORK:FILEPATH="/Library/Frameworks/3DconnexionClient.framework")
fi

if [[ ${HOST} =~ .*darwin.* ]]; then
  CXXFLAGS="${CXXFLAGS} -D_LIBCPP_DISABLE_AVAILABILITY"
fi

# Ensure the build uses the correct Qt tools
if [[ "${target_platform}" =~ osx-arm64 && ${USE_QT6} = "1" ]]; then
    rm -f "${PREFIX}/lib/qt6/moc"
    rm -f "${PREFIX}/lib/qt6/uic"
    rm -f "${PREFIX}/lib/qt6/rcc"
    rm -f "${PREFIX}/lib/qt6/bin/lrelease"
    ln -s "${BUILD_PREFIX}/lib/qt6/moc" "${PREFIX}/lib/qt6/moc"
    ln -s "${BUILD_PREFIX}/lib/qt6/uic" "${PREFIX}/lib/qt6/uic"
    ln -s "${BUILD_PREFIX}/lib/qt6/rcc" "${PREFIX}/lib/qt6/rcc"
    ln -s "${BUILD_PREFIX}/lib/qt6/bin/lrelease" "${PREFIX}/lib/qt6/bin/lrelease"
    
    # Additional debugging information
    echo "Adjusted Qt tools for osx-arm64 with build variant qt6"
    echo "Removed: ${PREFIX}/lib/qt6/moc"
    echo "Linked to: ${BUILD_PREFIX}/lib/qt6/moc"
    echo "Removed: ${PREFIX}/lib/qt6/uic"
    echo "Linked to: ${BUILD_PREFIX}/lib/qt6/uic"
    echo "Removed: ${PREFIX}/lib/qt6/rcc"
    echo "Linked to: ${BUILD_PREFIX}/lib/qt6/rcc"
    echo "Removed: ${PREFIX}/lib/qt6/bin/lrelease"
    echo "Linked to: ${BUILD_PREFIX}/lib/qt6/bin/lrelease"
else
    echo "Skipping Qt tools adjustment. Target platform: ${target_platform}, Build variant: $build_variant"
fi

cmake -G "Ninja" -B build -S . \
      -D BUILD_WITH_CONDA:BOOL=ON \
      -D CMAKE_BUILD_TYPE=${BUILD_TYPE} \
      -D CMAKE_INSTALL_PREFIX:FILEPATH="$PREFIX" \
      -D CMAKE_PREFIX_PATH:FILEPATH="$PREFIX" \
      -D CMAKE_LIBRARY_PATH:FILEPATH="$PREFIX/lib" \
      -D CMAKE_INSTALL_LIBDIR:FILEPATH="$PREFIX/lib" \
      -D CMAKE_INCLUDE_PATH:FILEPATH="$PREFIX/include" \
      -D FREECAD_USE_OCC_VARIANT="Official Version" \
      -D OCC_INCLUDE_DIR:FILEPATH="$PREFIX/include" \
      -D USE_BOOST_PYTHON:BOOL=OFF \
      -D FREECAD_USE_PYBIND11:BOOL=ON \
      -D SMESH_INCLUDE_DIR:FILEPATH="$PREFIX/include/smesh" \
      -D FREECAD_USE_EXTERNAL_SMESH=ON \
      -D FREECAD_USE_EXTERNAL_FMT:BOOL=OFF \
      -D BUILD_FLAT_MESH:BOOL=ON \
      -D BUILD_WITH_CONDA:BOOL=ON \
      -D Python_EXECUTABLE:FILEPATH="$PYTHON" \
      -D Python3_EXECUTABLE:FILEPATH="$PYTHON" \
      -D BUILD_FEM_NETGEN:BOOL=ON \
      -D BUILD_SHIP:BOOL=OFF \
      -D OCCT_CMAKE_FALLBACK:BOOL=OFF \
      -D FREECAD_USE_QT_DIALOG:BOOL=ON \
      -D BUILD_DYNAMIC_LINK_PYTHON:BOOL=OFF \
      -D Boost_NO_BOOST_CMAKE:BOOL=ON \
      -D FREECAD_USE_PCL:BOOL=ON \
      -D FREECAD_USE_PCH:BOOL=OFF \
      -D INSTALL_TO_SITEPACKAGES:BOOL=ON \
      -D QT_HOST_PATH="${PREFIX}" \
      -D FREECAD_USE_SHIBOKEN:BOOL=OFF \
      -D FREECAD_USE_PYSIDE:BOOL=OFF \
      -D FREECAD_CHECK_PIVY:BOOL=OFF \
      ${CMAKE_PLATFORM_FLAGS[@]}

echo "FREECAD_USE_3DCONNEXION=${FREECAD_USE_3DCONNEXION}"

ninja -C build install
rm -r ${PREFIX}/share/doc/FreeCAD     # smaller size of package!
mv ${PREFIX}/bin/FreeCAD ${PREFIX}/bin/freecad
mv ${PREFIX}/bin/FreeCADCmd ${PREFIX}/bin/freecadcmd
