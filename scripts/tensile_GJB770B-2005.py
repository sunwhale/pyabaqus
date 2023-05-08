# -*- coding: utf-8 -*-
# Do not delete the following import lines
# from abaqus import mdb
# from abaqusConstants import *
from abaqusConstants import (CLOCKWISE, TWO_D_PLANAR, DISPLACEMENT, THREE_D, MIDDLE_SURFACE, FROM_SECTION,
                             DEFORMABLE_BODY, XZPLANE, YZPLANE, STANDARD, CPS4, CPS3, STRUCTURED, QUAD, C3D4,
                             C3D6, C3D8, STEP, UNIFORM, SOLVER_DEFAULT)
# from caeModules import mesh


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


def create_part_3d(model_name, sketch_name, part_name, depth):
    p = mdb.models[model_name].Part(name=part_name, dimensionality=THREE_D, type=DEFORMABLE_BODY)
    p.BaseSolidExtrude(sketch=mdb.models[model_name].sketches[sketch_name], depth=depth)
    p.Set(cells=p.cells, name='Set-All')


def create_part_2d(model_name, sketch_name, part_name):
    p = mdb.models[model_name].Part(name=part_name, dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
    p.BaseShell(sketch=mdb.models[model_name].sketches[sketch_name])
    p.Set(faces=p.faces, name='Set-All')


def partition_part_by_datum_plane(model_name, part_name, l1, l2, l3, l4, dimension):
    p = mdb.models[model_name].parts[part_name]
    p.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=l1 / 2.0)
    p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=(l2 - l3) / 2.0 * 4.0 / 5.0)
    p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=((l2 - l3) / 2.0 + l4))
    p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=((l2 + l3) / 2.0 - l4))
    p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=l2 * 100.0 / 120.0)
    # This section will cut the part by plane
    if dimension == 2:
        for key, datum in p.datums.items():
            p.PartitionFaceByDatumPlane(datumPlane=datum, faces=p.faces)
    elif dimension == 3:
        for key, datum in p.datums.items():
            p.PartitionCellByDatumPlane(datumPlane=datum, cells=p.cells)
    else:
        raise KeyError('Unsupported dimension %s' % dimension)


def create_material(model_name, material_name, dens, Ymodulus, Pratio, DLdisplacement, DLdistance):
    mdb.models[model_name].Material(name=material_name)
    mdb.models[model_name].materials[material_name].Density(table=((dens,),))
    mdb.models[model_name].materials[material_name].Elastic(table=((Ymodulus, Pratio),))
    mdb.models[model_name].materials[material_name].Plastic(table=(
        (1161.5, 0.0), (1198.5, 0.00985), (1231.9, 0.01961), (1262.6, 0.02927), (1289.4, 0.03884),
        (1313.3, 0.04832), (1332.7, 0.05771), (1350.0, 0.06701)))
    mdb.models[model_name].materials[material_name].DuctileDamageInitiation(table=((DLdisplacement, 0.0, 0.0),))
    mdb.models[model_name].materials[material_name].ductileDamageInitiation.DamageEvolution(
        type=DISPLACEMENT, table=((DLdistance,),))


def create_section_3d(model_name, part_name, section_name, material_name):
    mdb.models[model_name].HomogeneousSolidSection(name=section_name, material=material_name, thickness=None)
    p = mdb.models[model_name].parts[part_name]
    p.SectionAssignment(region=p.sets['Set-All'], sectionName=section_name, offset=0.0,
                        offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)


def create_section_2d(model_name, material_name, part_name, section_name, depth):
    mdb.models[model_name].HomogeneousSolidSection(name=section_name, material=material_name, thickness=depth)
    p = mdb.models[model_name].parts[part_name]
    p.SectionAssignment(region=p.sets['Set-All'], sectionName=section_name, offset=0.0,
                        offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)


def create_assemble(model_name, part_name, assemble_name):
    p = mdb.models[model_name].parts[part_name]
    mdb.models[model_name].rootAssembly.Instance(name=assemble_name, part=p, dependent=ON)


def create_step(model_name, step_name, output_time, step_time, initial_time):
    mdb.models[model_name].StaticStep(name=step_name, previous='Initial', timePeriod=step_time, initialInc=initial_time,
                                      minInc=0.0001, maxInc=1)
    mdb.models[model_name].fieldOutputRequests['F-Output-1'].setValues(variables=(
        'S', 'PE', 'PEEQ', 'PEMAG', 'LE', 'U', 'RF', 'CF', 'CSTRESS', 'CDISP', 'STATUS'), timeInterval=output_time)


def create_sets_2d(model_name, part_name, set_fixed_name1, set_fixed_name2, set_tensile_name1, set_tensile_name2, l1,
                   l2, l3, l4, depth):
    p = mdb.models[model_name].parts[part_name]
    # 通过指定cube区域拾取边
    p.Set(edges=p.edges.getByBoundingBox((l2 - l3) / 2.0, 0, 0, l2 / 2, l4, depth), name=set_fixed_name1)
    p.Set(edges=p.edges.getByBoundingBox((l2 - l3) / 2.0, l1 - l4, 0, l2 / 2, l1, depth),
          name=set_fixed_name2)  # fixed
    p.Set(edges=p.edges.getByBoundingBox(l2 / 2, 0, 0, (l2 + l3) / 2.0, l4, depth), name=set_tensile_name1)
    p.Set(edges=p.edges.getByBoundingBox(l2 / 2, l1 - l4, 0, (l2 + l3) / 2.0, l1, depth),
          name=set_tensile_name2)  # tensile


def create_sets_3d(model_name, part_name, set_fixed_name1, set_fixed_name2, set_tensile_name1, set_tensile_name2, l1,
                   l2,
                   l3, l4, depth):
    p = mdb.models[model_name].parts[part_name]
    # 通过指定cube区域拾取面
    p.Set(faces=p.faces.getByBoundingBox((l2 - l3) / 2.0, 0, 0, l2 / 2, l4, depth), name=set_fixed_name1)
    p.Set(faces=p.faces.getByBoundingBox((l2 - l3) / 2.0, l1 - l4, 0, l2 / 2, l1, depth),
          name=set_fixed_name2)  # fixed
    p.Set(faces=p.faces.getByBoundingBox(l2 / 2, 0, 0, (l2 + l3) / 2, l4, depth), name=set_tensile_name1)
    p.Set(faces=p.faces.getByBoundingBox(l2 / 2, l1 - l4, 0, (l2 + l3) / 2, l1, depth),
          name=set_tensile_name2)  # tensile


def create_boundary(model_name, assemble_name, Amp_name, step_name,
                    set_fixed_name1, set_fixed_name2, set_tensile_name1, set_tensile_name2,
                    bd_fixed_name1, bd_fixed_name2, bd_tensile_name1, bd_tensile_name2):
    # fixed_boundary
    a = mdb.models[model_name].rootAssembly
    region = a.instances[assemble_name].sets[set_fixed_name1]
    mdb.models[model_name].EncastreBC(name=bd_fixed_name1, createStepName='Initial', region=region, localCsys=None)
    region = a.instances[assemble_name].sets[set_fixed_name2]
    mdb.models[model_name].EncastreBC(name=bd_fixed_name2, createStepName='Initial', region=region, localCsys=None)
    # Amp
    mdb.models[model_name].TabularAmplitude(name=Amp_name, timeSpan=STEP,
                                            smooth=SOLVER_DEFAULT, data=((0.0, 0.0), (1.0, 1.0)))
    # tensile_boundayr
    region = a.instances[assemble_name].sets[set_tensile_name1]
    mdb.models[model_name].DisplacementBC(name=bd_tensile_name1, createStepName=step_name,
                                          region=region, u1=5.0, u2=0.0, u3=0.0, amplitude=Amp_name, fixed=OFF,
                                          distributionType=UNIFORM, fieldName='', localCsys=None)
    region = a.instances[assemble_name].sets[set_tensile_name2]
    mdb.models[model_name].DisplacementBC(name=bd_tensile_name2, createStepName=step_name,
                                          region=region, u1=5.0, u2=0.0, u3=0.0, amplitude=Amp_name, fixed=OFF,
                                          distributionType=UNIFORM, fieldName='', localCsys=None)


def create_mesh_3d(model_name, part_name, element_size):
    p = mdb.models[model_name].parts[part_name]
    p.seedPart(size=element_size, deviationFactor=0.1, minSizeFactor=0.1)
    p.generateMesh()
    elemType1 = mesh.ElemType(elemCode=C3D8, elemLibrary=STANDARD)
    elemType2 = mesh.ElemType(elemCode=C3D6, elemLibrary=STANDARD)
    elemType3 = mesh.ElemType(elemCode=C3D4, elemLibrary=STANDARD)
    p.setElementType(regions=p.sets['Set-All'], elemTypes=(elemType1, elemType2, elemType3))


def create_mesh_2d(model_name, part_name, element_size):
    p = mdb.models[model_name].parts[part_name]
    p.setMeshControls(regions=p.faces, elemShape=QUAD, technique=STRUCTURED)
    p.seedPart(size=element_size, deviationFactor=0.1, minSizeFactor=0.1)
    p.generateMesh()
    elemType1 = mesh.ElemType(elemCode=CPS4, elemLibrary=STANDARD)
    elemType2 = mesh.ElemType(elemCode=CPS3, elemLibrary=STANDARD)
    p.setElementType(regions=p.sets['Set-All'], elemTypes=(elemType1, elemType2))


def create_job(model_name, job_name, cae_name):
    mdb.models[model_name].rootAssembly.regenerate()
    job = mdb.Job(name=job_name, model=model_name)
    job.writeInput()
    mdb.saveAs(pathName=cae_name)

if __name__ == "__main__":
    # =============================================================================
    # General parameters
    model_name = 'Model-1'
    sketch_name = 'Sketch-1'
    part_name = 'PART-1'
    material_name = 'Ti-6Al-4V'
    section_name = 'Section-1'
    assemble_name = 'Part-1-1'
    step_name = 'Step-1'
    set_fixed_name1 = 'Set-Fixed-1'
    set_fixed_name2 = 'Set-Fixed-2'
    set_tensile_name1 = 'Set-Tensile-1'
    set_tensile_name2 = 'Set-Tensile-2'
    bd_fixed_name1 = 'BC-Fixed-1'
    bd_fixed_name2 = 'BC-Fixed-2'
    bd_tensile_name1 = 'BC-Tensile-1'
    bd_tensile_name2 = 'BC-Tensile-2'
    Amp_name = 'Amp-1'
    job_name = 'Job-1'
    l1 = 22
    l2 = 120
    l3 = 70
    l4 = 6
    depth = 10
    dens = 4.43e-9
    Ymodulus = 115000
    Pratio = 0.343
    DLdisplacement = 0.06701
    DLdistance = 0.2
    step_time = 1
    initial_time = 0.0001
    output_time = 0.02
    element_size = 1
    # =============================================================================
    # Special parameters
    deep_number = 6  # 3D
    scale_factor = 1e-5  # 2d
    cae_name = 'tensile.cae'
    # =============================================================================
    # If calculating a 3D model, enter "3"; if calculating a 2D model, enter "2".
    dimension = 3

    if dimension == 2:
        # This region will create 2D model
        create_sketch(model_name=model_name, sketch_name=sketch_name, l1=l1, l2=l2, l3=l3, l4=l4)
        create_part_2d(model_name=model_name, sketch_name=sketch_name, part_name=part_name)
        partition_part_by_datum_plane(model_name=model_name, part_name=part_name, l1=l1, l2=l2, l3=l3, l4=l4,
                                      dimension=dimension)
        create_material(model_name=model_name, material_name=material_name, dens=dens, Ymodulus=Ymodulus,
                        Pratio=Pratio, DLdisplacement=DLdisplacement, DLdistance=DLdistance)
        create_section_2d(model_name=model_name, part_name=part_name, section_name=section_name,
                          material_name=material_name, depth=depth)

        create_assemble(model_name=model_name, part_name=part_name, assemble_name=assemble_name)
        create_step(model_name=model_name, step_name=step_name, step_time=step_time, output_time=output_time,
                    initial_time=initial_time)
        create_sets_2d(model_name=model_name, part_name=part_name, set_fixed_name1=set_fixed_name1,
                       set_fixed_name2=set_fixed_name2,
                       set_tensile_name1=set_tensile_name1, set_tensile_name2=set_tensile_name2, l1=l1, l2=l2, l3=l3,
                       l4=l4, depth=depth)
        create_boundary(model_name=model_name, set_fixed_name1=set_fixed_name1, set_fixed_name2=set_fixed_name2,
                        set_tensile_name1=set_tensile_name1, set_tensile_name2=set_tensile_name2,
                        bd_fixed_name1=bd_fixed_name1, bd_fixed_name2=bd_fixed_name2, bd_tensile_name1=bd_tensile_name1,
                        bd_tensile_name2=bd_tensile_name2,
                        step_name=step_name, Amp_name=Amp_name, assemble_name=assemble_name)
        create_mesh_2d(model_name=model_name, part_name=part_name, element_size=element_size)
        create_job(model_name=model_name, job_name=job_name, cae_name=cae_name)

    elif dimension == 3:
        # This region will create 3D model
        create_sketch(model_name=model_name, sketch_name=sketch_name, l1=l1, l2=l2, l3=l3, l4=l4)
        create_part_3d(model_name=model_name, sketch_name=sketch_name, part_name=part_name, depth=depth)
        partition_part_by_datum_plane(model_name=model_name, part_name=part_name, l1=l1, l2=l2, l3=l3, l4=l4,
                                      dimension=dimension)
        create_material(model_name=model_name, material_name=material_name,
                        dens=dens, Ymodulus=Ymodulus, Pratio=Pratio, DLdisplacement=DLdisplacement,
                        DLdistance=DLdistance)
        create_section_3d(model_name=model_name, material_name=material_name, part_name=part_name,
                          section_name=section_name)
        create_assemble(model_name=model_name, part_name=part_name, assemble_name=assemble_name)
        create_step(model_name=model_name, step_name=step_name, step_time=step_time, output_time=output_time,
                    initial_time=initial_time)
        create_sets_3d(model_name=model_name, part_name=part_name, set_fixed_name1=set_fixed_name1,
                       set_fixed_name2=set_fixed_name2,
                       set_tensile_name1=set_tensile_name1, set_tensile_name2=set_tensile_name2, l1=l1, l2=l2, l3=l3,
                       l4=l4, depth=depth)
        create_boundary(model_name=model_name, set_fixed_name1=set_fixed_name1, set_fixed_name2=set_fixed_name2,
                        set_tensile_name1=set_tensile_name1, set_tensile_name2=set_tensile_name2,
                        bd_fixed_name1=bd_fixed_name1, bd_fixed_name2=bd_fixed_name2, bd_tensile_name1=bd_tensile_name1,
                        bd_tensile_name2=bd_tensile_name2, step_name=step_name, Amp_name=Amp_name,
                        assemble_name=assemble_name)
        create_mesh_3d(model_name=model_name, part_name=part_name, element_size=element_size)
        create_job(model_name=model_name, job_name=job_name, cae_name=cae_name)
    else:
        raise KeyError('Unsupported dimension %s' % dimension)
