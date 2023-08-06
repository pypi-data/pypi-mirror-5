#include <boost/python.hpp>

#include <bob/config.h>
#ifdef BOB_API_VERSION
#  include <bob/python/ndarray.h>
#else
#  include <bob/core/python/ndarray.h>
#endif

#include "vtkThinPlateSplineTransform.h"
#include "vtkIterativeClosestPointTransform.h"
#include "vtkDoubleArray.h"
#include "vtkDelaunay2D.h"
#include "vtkOBJReader.h"
#include "vtkDataSetTriangleFilter.h"
#include "vtkUnstructuredGrid.h"
#include "vtkGeometryFilter.h"
#include "vtkCleanPolyData.h"
#include "vtkIdList.h"
#include <vtkTransform.h>
#include <vtkTransformPolyDataFilter.h>
#include <vtkLandmarkTransform.h>

class TPSTransformWP : public vtkThinPlateSplineTransform
{
public:
	static TPSTransformWP *New();
  boost::python::object getMatrixW();
};

boost::python::object TPSTransformWP::getMatrixW()
{

  bob::python::py_array wp(bob::core::array::t_float64,NumberOfPoints,3);
  double *wp2 = reinterpret_cast<double *>(wp.ptr());
  for(int i=0; i<NumberOfPoints; i++)
  {
    double *pt = MatrixW[i];
    wp2[i*3] = pt[0];
    wp2[(i*3)+1] = pt[1];
    wp2[(i*3)+2] = pt[2];
  }

	return wp.pyobject();
};

TPSTransformWP *TPSTransformWP::New()
{
	return (TPSTransformWP*)vtkThinPlateSplineTransform::New();
};

static boost::python::object extractWP(bob::python::const_ndarray shape, //input face shape 
                       boost::python::str filename, //filename for generic model 
                       bob::python::const_ndarray pointArray)  //points on generic face 
{
  // convert shape to polydata1
	vtkPoints *points = vtkPoints::New();
	vtkPolyData *polydata1 = vtkPolyData::New();
  vtkDelaunay2D *delaunay = vtkDelaunay2D::New();
  
  blitz::Array<double,3> bzShape = shape.bz<double,3>();
  for(int i=0; i<bzShape.extent(1); i++)
    for(int j=0; j<bzShape.extent(2); j++)
      if(bzShape(2,j,i) != 0)
        points->InsertNextPoint(-1*bzShape(0,j,i),-1*bzShape(1,j,i),-1*bzShape(2,j,i));

  polydata1->SetPoints(points);  
  delaunay->SetInput(polydata1); //Since we only have 3D points, triangulation is done using vtkDelaunay2D.
  delaunay->Update();
  polydata1->DeepCopy(delaunay->GetOutput());
  
  // read generic model to polydata2 and points to points2
  vtkOBJReader *meshReader = vtkOBJReader::New();
  vtkDataSetTriangleFilter *tFilter = vtkDataSetTriangleFilter::New();
  vtkUnstructuredGrid *uGrid = vtkUnstructuredGrid::New();
  vtkGeometryFilter *geom = vtkGeometryFilter::New();
  vtkCleanPolyData *cleaner = vtkCleanPolyData::New();
  vtkPolyData *polydata2 = vtkPolyData::New();
  vtkIdList *points2 = vtkIdList::New();
  
  meshReader->SetFileName(boost::python::extract<const char*>(filename)); //Read polydata from obj file
  meshReader->Update();
  tFilter->SetInput(meshReader->GetOutput());
  tFilter->Update();
  uGrid = tFilter->GetOutput();
  geom->SetInput(uGrid);
  geom->Update();
  cleaner->SetInput(geom->GetOutput());
  cleaner->PointMergingOn();
  cleaner->Update();
  polydata2->DeepCopy(cleaner->GetOutput());
  
  blitz::Array<double,2> bzArray = pointArray.bz<double,2>(); //Read and locate the control points on generic model for TPS warping
  int NumberOfPoints = bzArray.extent(0);
   
  for(int i=0; i<bzArray.extent(0); i++)
    points2->InsertNextId(polydata2->FindPoint(bzArray(i,0),bzArray(i,1),bzArray(i,2)));
  
  // rescale polydata2
  double *sourceBounds = polydata2->GetBounds();
  double *targetBounds = polydata1->GetBounds();
  
  double x = (targetBounds[0]-targetBounds[1])/(sourceBounds[0]-sourceBounds[1]);
  double y = (targetBounds[2]-targetBounds[3])/(sourceBounds[2]-sourceBounds[3]);
  double z = (targetBounds[4]-targetBounds[5])/(sourceBounds[4]-sourceBounds[5]);    
  double t = (x+y+z)/3;

  vtkTransform *scaleTr = vtkTransform::New();
  vtkTransformPolyDataFilter *scaleFilter = vtkTransformPolyDataFilter::New();
  scaleTr->Scale(t,t,t);
  scaleFilter->SetInput(polydata2);
  scaleFilter->SetTransform(scaleTr);
  scaleFilter->Update();
  polydata2->DeepCopy(scaleFilter->GetOutput());
  
  // align polydata2 to polydata1 using ICP     
  vtkIterativeClosestPointTransform *icp = vtkIterativeClosestPointTransform::New();
  vtkTransformPolyDataFilter *tpdf = vtkTransformPolyDataFilter::New();

  icp->SetSource(polydata2);
  icp->SetTarget(polydata1);
  icp->GetLandmarkTransform()->SetModeToRigidBody();
  icp->SetMaximumNumberOfIterations(50);
  icp->StartByMatchingCentroidsOn();
  icp->Modified();
  icp->Update();
  tpdf->SetInput(polydata2);
  tpdf->SetTransform(icp);
  tpdf->Update();
  polydata2->DeepCopy(tpdf->GetOutput());
  
  // apply TPS transformation using 140 points and extract warping parameters
  vtkIdList *points1 = vtkIdList::New();
  vtkPoints *targetCoordinates = vtkPoints::New();
  vtkPoints *sourceCoordinates = vtkPoints::New();
  TPSTransformWP *tps = TPSTransformWP::New();
  tpdf = vtkTransformPolyDataFilter::New();
  int numPt = points2->GetNumberOfIds();
  bob::python::py_array wp(bob::core::array::t_float64,NumberOfPoints,3);
  
  for(int pt=0; pt<numPt; pt++)
    points1->InsertNextId(polydata1->FindPoint(polydata2->GetPoint(points2->GetId(pt))));
  for(int pt=0; pt<numPt; pt++)
  {
    targetCoordinates->InsertNextPoint(polydata1->GetPoint(points1->GetId(pt)));
    sourceCoordinates->InsertNextPoint(polydata2->GetPoint(points2->GetId(pt)));
  } 
  tps->SetSourceLandmarks(sourceCoordinates);
  tps->SetTargetLandmarks(targetCoordinates);
  tps->SetBasisToR();
  tpdf->SetInput(polydata2);
  tpdf->SetTransform(tps);
  tpdf->Update();  
    
  points->Delete();
  polydata1->Delete();
  delaunay->Delete();
  meshReader->Delete();
  tFilter->Delete();
  geom->Delete();
  cleaner->Delete();
  polydata2->Delete();
  points2->Delete();
  scaleTr->Delete();
  scaleFilter->Delete();
  icp->Delete();
  tpdf->Delete();
  points1->Delete();
  targetCoordinates->Delete();
  sourceCoordinates->Delete();

  return tps->getMatrixW();  
}

  BOOST_PYTHON_MODULE(_tps) {
  bob::python::setup_python("Bindings to TPS warping parameter extraction using VTK");

  boost::python::def("extractWP", extractWP, (boost::python::arg("shape"),boost::python::arg("filename"),boost::python::arg("pointArray")),
  "shape:       Numpy array for the model under analysis of shape 3xMxN where M and N are the size of the mesh grid of x, y and z values.\
   filename:    The path to the .obj file of the generic face model to be warped.\
   pointArray:  Numpy array of control points to be used for TPS warping. The warping parameters are calculated at those points and used as a feature vector.");
  }
