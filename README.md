About freecad-feedstock
=======================

Feedstock license: [BSD-3-Clause](https://github.com/conda-forge/freecad-feedstock/blob/main/LICENSE.txt)

Home: https://www.freecad.org/

Package license: LGPL-2.1-or-later

Summary: FreeCAD is a parametric 3D modeler made primarily to design real-life objects of any size.

Development: https://github.com/FreeCAD/FreeCAD

Documentation: https://wiki.freecad.org/Main_Page

FreeCAD is a general purpose feature-based, parametric 3D modeler for
CAD, MCAD, CAx, CAE and PLM, aimed directly at mechanical engineering
and product design but also fits a wider range of uses in engineering,
such as architecture or other engineering specialties. It is 100% Open
Source (LGPL2+ license) and extremely modular, allowing for very
advanced extension and customization.
FreeCAD is based on OpenCASCADE, a powerful geometry kernel, features an
Open Inventor-compliant 3D scene representation model provided by the
Coin 3D library, and a broad Python API. The interface is built with Qt.
FreeCAD runs exactly the same way on Windows, Mac OSX, BSD and Linux
platforms.

Current build status
====================


<table><tr>
    <td>GitHub Actions</td>
    <td>
      <a href="https://github.com/conda-forge/freecad-feedstock/actions/workflows/conda-build.yml">
        <img src="https://github.com/conda-forge/freecad-feedstock/actions/workflows/conda-build.yml/badge.svg?event=push&branch=main">
      </a>
    </td>
  </tr>
    
  <tr>
    <td>Azure</td>
    <td>
      <details>
        <summary>
          <a href="https://dev.azure.com/conda-forge/feedstock-builds/_build/latest?definitionId=5916&branchName=main">
            <img src="https://dev.azure.com/conda-forge/feedstock-builds/_apis/build/status/freecad-feedstock?branchName=main">
          </a>
        </summary>
        <table>
          <thead><tr><th>Variant</th><th>Status</th></tr></thead>
          <tbody><tr>
              <td>osx_64_python3.10.____cpython</td>
              <td>
                <a href="https://dev.azure.com/conda-forge/feedstock-builds/_build/latest?definitionId=5916&branchName=main">
                  <img src="https://dev.azure.com/conda-forge/feedstock-builds/_apis/build/status/freecad-feedstock?branchName=main&jobName=osx&configuration=osx%20osx_64_python3.10.____cpython" alt="variant">
                </a>
              </td>
            </tr><tr>
              <td>osx_64_python3.11.____cpython</td>
              <td>
                <a href="https://dev.azure.com/conda-forge/feedstock-builds/_build/latest?definitionId=5916&branchName=main">
                  <img src="https://dev.azure.com/conda-forge/feedstock-builds/_apis/build/status/freecad-feedstock?branchName=main&jobName=osx&configuration=osx%20osx_64_python3.11.____cpython" alt="variant">
                </a>
              </td>
            </tr><tr>
              <td>osx_64_python3.12.____cpython</td>
              <td>
                <a href="https://dev.azure.com/conda-forge/feedstock-builds/_build/latest?definitionId=5916&branchName=main">
                  <img src="https://dev.azure.com/conda-forge/feedstock-builds/_apis/build/status/freecad-feedstock?branchName=main&jobName=osx&configuration=osx%20osx_64_python3.12.____cpython" alt="variant">
                </a>
              </td>
            </tr><tr>
              <td>osx_64_python3.13.____cp313</td>
              <td>
                <a href="https://dev.azure.com/conda-forge/feedstock-builds/_build/latest?definitionId=5916&branchName=main">
                  <img src="https://dev.azure.com/conda-forge/feedstock-builds/_apis/build/status/freecad-feedstock?branchName=main&jobName=osx&configuration=osx%20osx_64_python3.13.____cp313" alt="variant">
                </a>
              </td>
            </tr><tr>
              <td>osx_64_python3.14.____cp314</td>
              <td>
                <a href="https://dev.azure.com/conda-forge/feedstock-builds/_build/latest?definitionId=5916&branchName=main">
                  <img src="https://dev.azure.com/conda-forge/feedstock-builds/_apis/build/status/freecad-feedstock?branchName=main&jobName=osx&configuration=osx%20osx_64_python3.14.____cp314" alt="variant">
                </a>
              </td>
            </tr>
          </tbody>
        </table>
      </details>
    </td>
  </tr>
</table>

Current release info
====================

| Name | Downloads | Version | Platforms |
| --- | --- | --- | --- |
| [![Conda Recipe](https://img.shields.io/badge/recipe-freecad-green.svg)](https://anaconda.org/freecad/freecad) | [![Conda Downloads](https://img.shields.io/conda/dn/freecad/freecad.svg)](https://anaconda.org/freecad/freecad) | [![Conda Version](https://img.shields.io/conda/vn/freecad/freecad.svg)](https://anaconda.org/freecad/freecad) | [![Conda Platforms](https://img.shields.io/conda/pn/freecad/freecad.svg)](https://anaconda.org/freecad/freecad) |

Installing freecad
==================

Installing `freecad` from the `freecad/label/` channel can be achieved by adding `freecad/label/` to your channels with:

```
conda config --add channels freecad/label/
conda config --set channel_priority strict
```

How to use
----------

<details>
<summary>With conda</summary>

```
conda install freecad
```

</details>

<details>
<summary>With mamba</summary>

```
mamba install freecad
```

</details>

<details>
<summary>With pixi</summary>

```
# for adding to your local project
pixi add freecad
# for installing globally
pixi global install freecad
```

</details>

Search package versions
-----------------------

It is possible to list all of the versions of `freecad` available on your platform:

<details>
<summary>With conda</summary>

```
conda search freecad --channel freecad/label/
```

</details>

<details>
<summary>With mamba</summary>

```
mamba search freecad --channel freecad/label/
```

</details>

<details>
<summary>With pixi</summary>

```
pixi search freecad --channel freecad/label/
```

</details>

<details>
<summary>With mamba repoquery, which may provide more information</summary>

```
# Search all versions available on your platform:
mamba repoquery search freecad --channel freecad/label/

# List packages depending on `freecad`:
mamba repoquery whoneeds freecad --channel freecad/label/

# List dependencies of `freecad`:
mamba repoquery depends freecad --channel freecad/label/
```

</details>




Updating freecad-feedstock
==========================

If you would like to improve the freecad recipe or build a new
package version, please fork this repository and submit a PR. Upon submission,
your changes will be run on the appropriate platforms to give the reviewer an
opportunity to confirm that the changes result in a successful build. Once
merged, the recipe will be re-built and uploaded automatically to the
`freecad` channel, whereupon the built conda packages will be available for
everybody to install and use from the `freecad` channel.
Note that all branches in the conda-forge/freecad-feedstock are
immediately built and any created packages are uploaded, so PRs should be based
on branches in forks, and branches in the main repository should only be used to
build distinct package versions.

In order to produce a uniquely identifiable distribution:
 * If the version of a package **is not** being increased, please add or increase
   the [``build/number``](https://docs.conda.io/projects/conda-build/en/latest/resources/define-metadata.html#build-number-and-string).
 * If the version of a package **is** being increased, please remember to return
   the [``build/number``](https://docs.conda.io/projects/conda-build/en/latest/resources/define-metadata.html#build-number-and-string)
   back to 0.

Feedstock Maintainers
=====================

* [@adrianinsaval](https://github.com/adrianinsaval/)
* [@looooo](https://github.com/looooo/)

