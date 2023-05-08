# -*- coding: utf-8 -*-
# Do not delete the following import lines
# from abaqus import *
# from abaqusConstants import *

from abaqus import mdb
from abaqusConstants import (CLOCKWISE, TWO_D_PLANAR, THREE_D, MIDDLE_SURFACE, FROM_SECTION,
                             DEFORMABLE_BODY, XZPLANE, YZPLANE, STANDARD, CPS4, CPS3, STRUCTURED, QUAD, C3D4,
                             C3D6, C3D8, STEP, UNIFORM, SOLVER_DEFAULT, HEX, ON, OFF, UNSET, PRESELECT)
from caeModules import mesh


def create_sketch(model_name, sketch_name, l1, l2, l3, l4):
    s = mdb.models[model_name].ConstrainedSketch(name=sketch_name, sheetSize=200.0)
    s.Line(point1=(0.0, 0.0), point2=((l2 - l3) / 2.0, 0.0))
    s.ArcByCenterEnds(center=((l2 - l3) / 2 + l4, 0.0), point1=((l2 - l3) / 2.0, 0.0), point2=((l2 - l3) / 2 + l4, l4),
                      direction=CLOCKWISE)
    s.Line(point1=((l2 - l3) / 2 + l4, l4), point2=((l2 + l3) / 2 - l4, l4))
    s.ArcByCenterEnds(center=((l2 + l3) / 2 - l4, 0.0), point1=((l2 + l3) / 2 - l4, l4), point2=((l2 + l3) / 2, 0.0),
                      direction=CLOCKWISE)
    s.Line(point1=((l2 + l3) / 2, 0.0), point2=(l2, 0.0))
    s.Line(point1=(l2, 0.0), point2=(l2, l1))
    s.Line(point1=(l2, l1), point2=((l2 + l3) / 2, l1))
    s.ArcByCenterEnds(center=((l2 + l3) / 2 - l4, l1), point1=((l2 + l3) / 2, l1), point2=((l2 + l3) / 2 - l4, l1 - l4),
                      direction=CLOCKWISE)
    s.Line(point1=((l2 + l3) / 2 - l4, l1 - l4), point2=((l2 - l3) / 2 + l4, l1 - l4))
    s.ArcByCenterEnds(center=((l2 - l3) / 2 + l4, l1), point1=((l2 - l3) / 2 + l4, l1 - l4),
                      point2=((l2 - l3) / 2.0, l1), direction=CLOCKWISE)
    s.Line(point1=((l2 - l3) / 2.0, l1), point2=(0.0, l1))
    s.Line(point1=(0.0, l1), point2=(0.0, 0.0))


def create_part(model_name, sketch_name, part_name, dimension, thickness=1.0):
    if dimension == 2:
        p = mdb.models[model_name].Part(name=part_name, dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
        p.BaseShell(sketch=mdb.models[model_name].sketches[sketch_name])
        p.Set(faces=p.faces, name='Set-All')
    elif dimension == 3:
        p = mdb.models[model_name].Part(name=part_name, dimensionality=THREE_D, type=DEFORMABLE_BODY)
        p.BaseSolidExtrude(sketch=mdb.models[model_name].sketches[sketch_name], depth=thickness)
        p.Set(cells=p.cells, name='Set-All')
    else:
        raise KeyError('Unsupported dimension %s' % dimension)


def partition_part_by_datum_plane(model_name, part_name, l1, l2, l3, l4, dimension):
    p = mdb.models[model_name].parts[part_name]
    p.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=l1 / 2.0)
    p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=(l2 - l3) / 2.0 * 4.0 / 5.0)
    p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=((l2 - l3) / 2.0 + l4))
    p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=((l2 + l3) / 2.0 - l4))
    p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=l2 * 100.0 / 120.0)
    p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=l2 / 2.0)

    if dimension == 2:
        for key, datum in p.datums.items():
            p.PartitionFaceByDatumPlane(datumPlane=datum, faces=p.faces)
    elif dimension == 3:
        for key, datum in p.datums.items():
            p.PartitionCellByDatumPlane(datumPlane=datum, cells=p.cells)
    else:
        raise KeyError('Unsupported dimension %s' % dimension)


def create_section(model_name, part_name, section_name, material_name, thickness=None):
    mdb.models[model_name].HomogeneousSolidSection(name=section_name, material=material_name, thickness=thickness)
    p = mdb.models[model_name].parts[part_name]
    p.SectionAssignment(region=p.sets['Set-All'], sectionName=section_name, offset=0.0,
                        offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)


def create_assembly(model_name, part_name, assembly_name):
    p = mdb.models[model_name].parts[part_name]
    mdb.models[model_name].rootAssembly.Instance(name=assembly_name, part=p, dependent=ON)


def create_step(model_name, step_name, previous_step_name, total_step_time, max_number_of_increment,
                initial_time_increment, min_time_increment, max_time_increment):
    mdb.models[model_name].StaticStep(name=step_name,
                                      previous=previous_step_name,
                                      timePeriod=total_step_time,
                                      maxNumInc=max_number_of_increment,
                                      initialInc=initial_time_increment,
                                      minInc=min_time_increment,
                                      maxInc=max_time_increment)


def create_output(model_name, step_name, output_name, time_interval):
    mdb.models[model_name].FieldOutputRequest(name=output_name, createStepName=step_name, variables=PRESELECT,
                                              timeInterval=time_interval)


def create_sets(model_name, part_name, set_fixed_name, set_tensile_name, l1, l2, l3, l4, thickness, dimension):
    p = mdb.models[model_name].parts[part_name]

    if dimension == 2:
        e = p.edges.getByBoundingBox((l2 - l3) / 2.0, 0, 0, l2 / 2, l4, thickness)
        e += p.edges.getByBoundingBox((l2 - l3) / 2.0, l1 - l4, 0, l2 / 2, l1, thickness)
        p.Set(edges=e, name=set_fixed_name)

        e = p.edges.getByBoundingBox(l2 / 2, 0, 0, (l2 + l3) / 2.0, l4, thickness)
        e += p.edges.getByBoundingBox(l2 / 2, l1 - l4, 0, (l2 + l3) / 2.0, l1, thickness)
        p.Set(edges=e, name=set_tensile_name)

    elif dimension == 3:
        f = p.faces.getByBoundingBox((l2 - l3) / 2.0, 0, 0, l2 / 2, l4, thickness)
        f += p.faces.getByBoundingBox((l2 - l3) / 2.0, l1 - l4, 0, l2 / 2, l1, thickness)
        p.Set(faces=f, name=set_fixed_name)

        f = p.faces.getByBoundingBox(l2 / 2, 0, 0, (l2 + l3) / 2.0, l4, thickness)
        f += p.faces.getByBoundingBox(l2 / 2, l1 - l4, 0, (l2 + l3) / 2.0, l1, thickness)
        p.Set(faces=f, name=set_tensile_name)

    else:
        raise KeyError('Unsupported dimension %s' % dimension)


def create_bc(model_name, assembly_name, amp_name, step_name, set_fixed_name, set_tensile_name, bc_fixed_name,
              bc_tensile_name, displacement):
    a = mdb.models[model_name].rootAssembly

    region = a.instances[assembly_name].sets[set_fixed_name]
    mdb.models[model_name].DisplacementBC(name=bc_fixed_name, createStepName=step_name,
                                          region=region, u1=0.0, u2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF,
                                          distributionType=UNIFORM, fieldName='', localCsys=None)

    mdb.models[model_name].TabularAmplitude(name=amp_name, timeSpan=STEP,
                                            smooth=SOLVER_DEFAULT, data=((0.0, 0.0), (1.0, 1.0)))

    region = a.instances[assembly_name].sets[set_tensile_name]
    mdb.models[model_name].DisplacementBC(name=bc_tensile_name, createStepName=step_name,
                                          region=region, u1=displacement, u2=UNSET, ur3=UNSET, amplitude=amp_name,
                                          fixed=OFF,
                                          distributionType=UNIFORM, fieldName='', localCsys=None)


def create_mesh(model_name, part_name, element_size, dimension):
    p = mdb.models[model_name].parts[part_name]
    p.seedPart(size=element_size, deviationFactor=0.1, minSizeFactor=0.1)

    if dimension == 2:
        p.setMeshControls(regions=p.faces, elemShape=QUAD, technique=STRUCTURED)
        p.generateMesh()
        elemType1 = mesh.ElemType(elemCode=CPS4, elemLibrary=STANDARD)
        elemType2 = mesh.ElemType(elemCode=CPS3, elemLibrary=STANDARD)
        p.setElementType(regions=p.sets['Set-All'], elemTypes=(elemType1, elemType2))

    elif dimension == 3:
        p.setMeshControls(regions=p.cells, elemShape=HEX, technique=STRUCTURED)
        p.generateMesh()
        elemType1 = mesh.ElemType(elemCode=C3D8, elemLibrary=STANDARD)
        elemType2 = mesh.ElemType(elemCode=C3D6, elemLibrary=STANDARD)
        elemType3 = mesh.ElemType(elemCode=C3D4, elemLibrary=STANDARD)
        p.setElementType(regions=p.sets['Set-All'], elemTypes=(elemType1, elemType2, elemType3))

    else:
        raise KeyError('Unsupported dimension %s' % dimension)


def create_job(model_name, job_name, cae_name):
    mdb.models[model_name].rootAssembly.regenerate()
    job = mdb.Job(name=job_name, model=model_name)
    job.writeInput()
    mdb.saveAs(pathName=cae_name)


def create_material_Ti6Al4V(model_name):
    density = 4.43e-9
    E = 115000
    nu = 0.343
    plastic_table = (
        (1161.5, 0.0),
        (1198.5, 0.00985),
        (1231.9, 0.01961),
        (1262.6, 0.02927),
        (1289.4, 0.03884),
        (1313.3, 0.04832),
        (1332.7, 0.05771),
        (1350.0, 0.06701)
    )
    mdb.models[model_name].Material(name=material_name)
    mdb.models[model_name].materials[material_name].Density(table=((density,),))
    mdb.models[model_name].materials[material_name].Elastic(table=((E, nu),))
    mdb.models[model_name].materials[material_name].Plastic(table=plastic_table)
    return 'Ti-6Al-4V'


if __name__ == "__main__":
    model_name = 'Model-1'

    # sketch
    sketch_name = 'Sketch-1'
    l1 = 22
    l2 = 120
    l3 = 70
    l4 = 6
    thickness = 10

    # part
    part_name = 'PART-1'
    dimension = 3

    # set
    set_fixed_name = 'Set-Fixed'
    set_tensile_name = 'Set-Tensile'

    # mesh
    element_size = 1

    # material
    material_name = create_material_Ti6Al4V(model_name)

    # section
    section_name = 'Section-1'

    # assembly
    assembly_name = 'Part-1-1'

    # step
    previous_step_name = 'Initial'
    step_name = 'Step-1'
    total_step_time = 1.0
    max_number_of_increment = 1000000
    initial_time_increment = 0.05
    min_time_increment = 1e-6
    max_time_increment = 0.1

    # output
    output_name = 'F-Output-1'
    time_interval = 0.1

    # bc
    bc_fixed_name = 'BC-Fixed'
    bc_tensile_name = 'BC-Tensile'
    amp_name = 'Amp-1'
    displacement = 5.0

    # job
    job_name = 'Job-1'
    cae_name = 'tensile.cae'

    create_sketch(model_name, sketch_name, l1, l2, l3, l4)

    create_part(model_name, sketch_name, part_name, dimension, thickness)

    partition_part_by_datum_plane(model_name, part_name, l1, l2, l3, l4, dimension)

    create_sets(model_name, part_name, set_fixed_name, set_tensile_name, l1, l2, l3, l4, thickness, dimension)

    create_mesh(model_name, part_name, element_size, dimension)

    create_section(model_name, part_name, section_name, material_name, thickness)

    create_assembly(model_name, part_name, assembly_name)

    create_step(model_name, step_name, previous_step_name, total_step_time, max_number_of_increment,
                initial_time_increment, min_time_increment, max_time_increment)

    create_output(model_name, step_name, output_name, time_interval)

    create_bc(model_name, assembly_name, amp_name, step_name, set_fixed_name, set_tensile_name, bc_fixed_name,
              bc_tensile_name, displacement)

    create_job(model_name, job_name, cae_name)
