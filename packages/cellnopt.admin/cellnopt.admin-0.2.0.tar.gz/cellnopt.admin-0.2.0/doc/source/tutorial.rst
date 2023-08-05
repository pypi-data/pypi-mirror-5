
Distribute CellNOptR package
===============================


Imagine you want to distribute the CellNOptR package that is available in this
SVN repository: https://svn.ebi.ac.uk/sysbiomed/trunk. In order to create a
distribution, you could go manually in the directory and type::

    R CMD build . 

However, there is no SVN versioning in the filename that has been created. You would first need to figure out the revision and then rename the file apropriately. 
With the :func:`~cellnopt.admin.distribute.DistributeRPackage` function you can
do that as follows::


    d = distribute.DistributeRPackage("CellNOptR", revision="HEAD", 
              url='https://svn.ebi.ac.uk/sysbiomed/trunk') 
    d.distribute()


Distribute several packages at once
=======================================

If you want to distribute several packages, you can call the previous code
several times or use the :class:`~cellnopt.admin.multidistribute.MultiDistributeRPackage`::

    d = MultiDistributeRPackage(packages=["CNORdt", "CellNOptR"], revision="HEAD")
    d.distribute()



