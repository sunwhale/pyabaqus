# -*- coding: utf-8 -*-
# Do not delete the following import lines
from abaqus import *
from abaqusConstants import *


def create_sketch(model_name, sketch_name, l1, l2, l3, l4):
    s = mdb.models[model_name].ConstrainedSketch(name='__profile__', sheetSize=200.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)
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
    mdb.models[model_name].sketches.changeKey(fromName='__profile__', toName=sketch_name)
    s.unsetPrimaryObject()


def create_part_3D(model_name, sketch_name, part_name, l1, l2, l5):
    s1 = mdb.models[model_name].ConstrainedSketch(name='__profile__', sheetSize=200.0)
    g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
    s1.setPrimaryObject(option=STANDALONE)
    s1.sketchOptions.setValues(gridOrigin=(l1 / 2, l2 / 2))
    s1.retrieveSketch(sketch=mdb.models[model_name].sketches[sketch_name])
    p = mdb.models[model_name].Part(name=part_name, dimensionality=THREE_D, type=DEFORMABLE_BODY)
    p = mdb.models[model_name].parts[part_name]
    p.BaseSolidExtrude(sketch=s1, depth=l5)  # different
    s1.unsetPrimaryObject()
    del mdb.models[model_name].sketches['__profile__']


def create_part_2D(model_name, sketch_name, part_name, l1, l2):
    s1 = mdb.models[model_name].ConstrainedSketch(name='__profile__', sheetSize=200.0)
    g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
    s1.setPrimaryObject(option=STANDALONE)
    s1.sketchOptions.setValues(gridOrigin=(l2 / 2, l1 / 2))
    s1.retrieveSketch(sketch=mdb.models[model_name].sketches[sketch_name])
    p = mdb.models[model_name].Part(name=part_name, dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
    p = mdb.models[model_name].parts[part_name]
    p.BaseShell(sketch=s1)
    s1.unsetPrimaryObject()
    del mdb.models[model_name].sketches['__profile__']


def create_material(model_name, material_name, dens, Ymodulus, Pratio, DLdisplacement,
                    DLdistance):
    mdb.models[model_name].Material(name=material_name)
    mdb.models[model_name].materials[material_name].Density(table=((dens,),))
    mdb.models[model_name].materials[material_name].Elastic(table=((Ymodulus, Pratio),))
    mdb.models[model_name].materials[material_name].Plastic(table=(
        (1161.5, 0.0), (1198.5, 0.00985), (1231.9, 0.01961), (1262.6, 0.02927), (1289.4, 0.03884),
        (1313.3, 0.04832), (1332.7, 0.05771), (1350.0, 0.06701)))
    mdb.models[model_name].materials[material_name].DuctileDamageInitiation(table=((
                                                                                       DLdisplacement, 0.0, 0.0),))
    mdb.models[model_name].materials[material_name].ductileDamageInitiation.DamageEvolution(
        type=DISPLACEMENT, table=((DLdistance,),))


def creat_section_3D(model_name, part_name, section_name, material_name):
    import regionToolset
    mdb.models[model_name].HomogeneousSolidSection(name=section_name, material=material_name, thickness=None)
    p = mdb.models[model_name].parts[part_name]
    c = p.cells
    cells = c.getSequenceFromMask(mask=('[#1 ]',), )
    region = regionToolset.Region(cells=cells)
    p.SectionAssignment(region=region, sectionName=section_name, offset=0.0, offsetType=MIDDLE_SURFACE,
                        offsetField='', thicknessAssignment=FROM_SECTION)


def create_section_2D(model_name, material_name, part_name, section_name, l5):
    import regionToolset
    mdb.models[model_name].HomogeneousSolidSection(name=section_name,
                                                   material=material_name, thickness=l5)
    p = mdb.models[model_name].parts[part_name]
    f = p.faces
    faces = f.getSequenceFromMask(mask=('[#1 ]',), )
    region = regionToolset.Region(faces=faces)
    p.SectionAssignment(region=region, sectionName=section_name, offset=0.0,
                        offsetType=MIDDLE_SURFACE, offsetField='',
                        thicknessAssignment=FROM_SECTION)


def create_assemble(model_name, part_name, assemble_name):
    a = mdb.models[model_name].rootAssembly
    a.DatumCsysByDefault(CARTESIAN)
    p = mdb.models[model_name].parts[part_name]
    a.Instance(name=assemble_name, part=p, dependent=ON)


def create_step(model_name, step_name, output_time, step_time, initial_time):
    mdb.models[model_name].StaticStep(name=step_name, previous='Initial', timePeriod=step_time, initialInc=initial_time,
                                      minInc=0.0001, maxInc=1)
    mdb.models[model_name].fieldOutputRequests['F-Output-1'].setValues(variables=(
        'S', 'PE', 'PEEQ', 'PEMAG', 'LE', 'U', 'RF', 'CF', 'CSTRESS', 'CDISP',
        'STATUS'), timeInterval=output_time)


def create_sets_3D(model_name, assemble_name, set_fixed_name, set_tensile_name):
    a = mdb.models[model_name].rootAssembly
    f1 = a.instances[assemble_name].faces
    faces1 = f1.getSequenceFromMask(mask=('[#202 ]',), )
    a.Set(faces=faces1, name=set_fixed_name)
    faces2 = f1.getSequenceFromMask(mask=('[#88 ]',), )
    a.Set(faces=faces2, name=set_tensile_name)


def create_sets_2D(model_name, assemble_name, set_fixed_name, set_tensile_name):
    a = mdb.models[model_name].rootAssembly
    e1 = a.instances[assemble_name].edges
    edges1 = e1.getSequenceFromMask(mask=('[#404 ]',), )
    a.Set(edges=edges1, name=set_fixed_name)
    edges2 = e1.getSequenceFromMask(mask=('[#110 ]',), )
    a.Set(edges=edges2, name=set_tensile_name)


def create_boundary(model_name, set_fixed_name, set_tensile_name, bd_fixed_name, bd_tensile_name, step_name, Amp_name):
    a = mdb.models[model_name].rootAssembly
    region = a.sets[set_fixed_name]
    mdb.models[model_name].EncastreBC(name=bd_fixed_name, createStepName='Initial', region=region, localCsys=None)
    mdb.models[model_name].TabularAmplitude(name=Amp_name, timeSpan=STEP,
                                            smooth=SOLVER_DEFAULT, data=((0.0, 0.0), (1.0, 1.0)))
    region = a.sets[set_tensile_name]
    mdb.models[model_name].DisplacementBC(name=bd_tensile_name, createStepName=step_name,
                                          region=region, u1=5.0, u2=0.0, u3=0.0, amplitude=Amp_name, fixed=OFF,
                                          distributionType=UNIFORM, fieldName='', localCsys=None)


def create_plane(model_name, part_name, l1, l2, l3, l4):
    p = mdb.models[model_name].parts[part_name]
    p.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=l1 / 2)
    p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=(l2 - l3) / 2 * 4 / 5)
    p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=((l2 - l3) / 2 + l4))
    p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=((l2 + l3) / 2 - l4))
    p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=l2 * 100.0 / 120)


def mesh_3D(model_name, part_name, longwide_number, shortwide_number, deep_number):
    import mesh
    p = mdb.models[model_name].parts[part_name]
    c = p.cells
    pickedCells = c.getSequenceFromMask(mask=('[#1 ]',), )
    d = p.datums
    p.PartitionCellByDatumPlane(datumPlane=d[4], cells=pickedCells)
    pickedCells = c.getSequenceFromMask(mask=('[#2 ]',), )
    p.PartitionCellByDatumPlane(datumPlane=d[5], cells=pickedCells)
    pickedCells = c.getSequenceFromMask(mask=('[#1 ]',), )
    p.PartitionCellByDatumPlane(datumPlane=d[6], cells=pickedCells)
    pickedCells = c.getSequenceFromMask(mask=('[#2 ]',), )
    p.PartitionCellByDatumPlane(datumPlane=d[7], cells=pickedCells)
    pickedCells = c.getSequenceFromMask(mask=('[#8 ]',), )
    p.PartitionCellByDatumPlane(datumPlane=d[3], cells=pickedCells)
    pickedCells = c.getSequenceFromMask(mask=('[#2e ]',), )
    p.PartitionCellByDatumPlane(datumPlane=d[3], cells=pickedCells)

    pickedRegions = c.getSequenceFromMask(mask=('[#3c0 ]',), )
    p.setMeshControls(regions=pickedRegions, elemShape=QUAD, technique=SWEEP)
    e = p.edges
    p.setSweepPath(region=c[6], edge=e[10], sense=FORWARD)
    p.setSweepPath(region=c[8], edge=e[10], sense=FORWARD)
    p.setSweepPath(region=c[4], edge=e[22], sense=REVERSE)
    p.setSweepPath(region=c[0], edge=e[0], sense=FORWARD)
    p.setSweepPath(region=c[3], edge=e[0], sense=REVERSE)

    pickedEdges = e.getSequenceFromMask(mask=('[#52aaa000 #21000080 #1046 ]',), )
    p.seedEdgeByNumber(edges=pickedEdges, number=shortwide_number, constraint=FINER)  # shortwide_number
    pickedEdges = e.getSequenceFromMask(mask=('[#8010000 #208201 #82000 ]',), )
    p.seedEdgeByNumber(edges=pickedEdges, number=longwide_number, constraint=FINER)  # longwide_number=8
    pickedEdges = e.getSequenceFromMask(mask=('[#0 #10810000 #200 ]',), )
    p.seedEdgeByNumber(edges=pickedEdges, number=deep_number, constraint=FINER)  # deep_number=6

    p.generateMesh(meshTechniqueOverride=ON)

    elemType1 = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD,
                              kinematicSplit=AVERAGE_STRAIN, secondOrderAccuracy=OFF,
                              hourglassControl=DEFAULT, distortionControl=DEFAULT)
    elemType2 = mesh.ElemType(elemCode=C3D6, elemLibrary=STANDARD)
    elemType3 = mesh.ElemType(elemCode=C3D4, elemLibrary=STANDARD)

    cells = c.getSequenceFromMask(mask=('[#3ff ]',), )
    pickedRegions = (cells,)
    p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2,
                                                       elemType3))


def mesh_2D(model_name, part_name, longwide_number, shortwide_number):
    import mesh
    p = mdb.models[model_name].parts[part_name]
    f = p.faces
    pickedFaces = f.getSequenceFromMask(mask=('[#1 ]',), )
    d = p.datums
    p.PartitionFaceByDatumPlane(datumPlane=d[4], faces=pickedFaces)
    pickedFaces = f.getSequenceFromMask(mask=('[#2 ]',), )
    p.PartitionFaceByDatumPlane(datumPlane=d[5], faces=pickedFaces)
    pickedFaces = f.getSequenceFromMask(mask=('[#4 ]',), )
    p.PartitionFaceByDatumPlane(datumPlane=d[6], faces=pickedFaces)
    pickedFaces = f.getSequenceFromMask(mask=('[#8 ]',), )
    p.PartitionFaceByDatumPlane(datumPlane=d[7], faces=pickedFaces)
    pickedFaces = f.getSequenceFromMask(mask=('[#1f ]',), )
    p.PartitionFaceByDatumPlane(datumPlane=d[3], faces=pickedFaces)

    e = p.edges
    p.setSweepPath(region=f[8], edge=e[0], sense=FORWARD)
    p.setSweepPath(region=f[9], edge=e[8], sense=REVERSE)

    pickedRegions = f.getSequenceFromMask(mask=('[#b2 ]',), )
    p.setMeshControls(regions=pickedRegions, elemShape=QUAD, technique=STRUCTURED)

    pickedEdges = e.getSequenceFromMask(mask=('[#29080a0a ]',), )
    p.seedEdgeByNumber(edges=pickedEdges, number=longwide_number, constraint=FINER)

    pickedEdges = e.getSequenceFromMask(mask=('[#25520a0 ]',), )
    p.seedEdgeByNumber(edges=pickedEdges, number=shortwide_number, constraint=FINER)

    p.generateMesh()
    elemType1 = mesh.ElemType(elemCode=CPS4R, elemLibrary=STANDARD,
                              secondOrderAccuracy=OFF, hourglassControl=DEFAULT,
                              distortionControl=DEFAULT)
    elemType2 = mesh.ElemType(elemCode=CPS3, elemLibrary=STANDARD)

    faces = f.getSequenceFromMask(mask=('[#3ff ]',), )
    pickedRegions = (faces,)
    p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2))


def create_job_3D(model_name, job_name, save_address):
    a = mdb.models[model_name].rootAssembly
    a.regenerate()
    mdb.Job(name=job_name, model=model_name, description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0,
            queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
            explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF,
            modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='',
            scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=2,
            numDomains=2, numGPUs=0)
    mdb.jobs[job_name].submit(consistencyChecking=OFF)
    mdb.saveAs(pathName=save_address)


def create_job_2D(model_name, job_name, save_address):
    a1 = mdb.models[model_name].rootAssembly
    a1.regenerate()
    mdb.Job(name=job_name, model=model_name, description='', type=ANALYSIS,
            memoryUnits=PERCENTAGE, explicitPrecision=SINGLE,
            nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF,
            contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='',
            resultsFormat=ODB, parallelizationMethodExplicit=DOMAIN, numDomains=2,
            activateLoadBalancing=False, multiprocessingMode=DEFAULT, numCpus=2)
    mdb.jobs[job_name].submit(consistencyChecking=OFF)
    mdb.saveAs(pathName=save_address)


##############
# part,section,set,mesh,job
if __name__ == "__main__":
    # =============================================================================
    # constants
    # =============================================================================
    # General paramenters
    model_name = 'Model-1'
    sketch_name = 'Sketch-1'
    part_name = 'PART-1'
    material_name = 'Ti-6Al-4V'
    section_name = 'Section_1'
    assemble_name = 'Part-1-1'
    step_name = 'Step-1'
    set_fixed_name = 'Set-Fixed'
    set_tensile_name = 'Set-Tensile'
    bd_fixed_name = 'BC-1'
    bd_tensile_name = 'BC-2'
    Amp_name = 'Amp-1'
    job_name = 'Job-1'

    l1 = 22
    l2 = 120
    l3 = 70
    l4 = 6
    l5 = 10
    dens = 4.43e-9
    Ymodulus = 115000
    Pratio = 0.343
    DLdisplacement = 0.06701
    DLdistance = 0.2
    step_time = 1
    initial_time = 0.0001
    output_time = 0.02
    longwide_number = 10
    shortwide_number = 6
    # =============================================================================

    # Special paramenters
    # 3D
    deep_number = None  # 6
    # 2d
    scale_factor = 1e-5  # 1e-5
    # =============================================================================
    if scale_factor:
        # This region will create 2D model
        save_address = 'E:/Users/ning/Desktop/3/2D-St'
        create_sketch(model_name=model_name, sketch_name=sketch_name, l1=l1, l2=l2, l3=l3, l4=l4)
        create_part_2D(model_name=model_name, sketch_name=sketch_name, part_name=part_name, l1=l1, l2=l2, )
        create_material(model_name=model_name, material_name=material_name, dens=dens, Ymodulus=Ymodulus,
                        Pratio=Pratio, DLdisplacement=DLdisplacement, DLdistance=DLdistance)
        create_section_2D(model_name=model_name, material_name=material_name, part_name=part_name,
                          section_name=section_name, l5=l5)
        create_assemble(model_name=model_name, part_name=part_name, assemble_name=assemble_name)
        create_step(model_name=model_name, step_name=step_name, step_time=step_time, output_time=output_time,
                    initial_time=initial_time)
        create_sets_2D(model_name=model_name, assemble_name=assemble_name, set_fixed_name=set_fixed_name,
                       set_tensile_name=set_tensile_name)
        create_boundary(model_name=model_name, set_fixed_name=set_fixed_name,
                        set_tensile_name=set_tensile_name, bd_fixed_name=bd_fixed_name, bd_tensile_name=bd_tensile_name,
                        step_name=step_name, Amp_name=Amp_name)
        create_plane(model_name=model_name, part_name=part_name, l1=l1, l2=l2, l3=l3, l4=l4)
        mesh_2D(model_name=model_name, part_name=part_name, longwide_number=longwide_number,
                shortwide_number=shortwide_number)
        create_job_2D(model_name=model_name, job_name=job_name, save_address=save_address)

    elif deep_number:
        # This region will create 3D model
        save_address = 'E:/Users/ning/Desktop/3/3D-St'
        create_sketch(model_name=model_name, sketch_name=sketch_name, l1=l1, l2=l2, l3=l3, l4=l4)
        create_part_3D(model_name=model_name, sketch_name=sketch_name, part_name=part_name, l1=l1, l2=l2, l5=l5)
        create_material(model_name=model_name, material_name=material_name,
                        dens=dens, Ymodulus=Ymodulus, Pratio=Pratio, DLdisplacement=DLdisplacement,
                        DLdistance=DLdistance)
        creat_section_3D(model_name=model_name, part_name=part_name, section_name=section_name,
                         material_name=material_name)
        create_assemble(model_name=model_name, part_name=part_name, assemble_name=assemble_name)
        create_step(model_name=model_name, step_name=step_name, step_time=step_time, output_time=output_time,
                    initial_time=initial_time)
        create_sets_3D(model_name=model_name, assemble_name=assemble_name, set_fixed_name=set_fixed_name,
                       set_tensile_name=set_tensile_name)
        create_boundary(model_name=model_name, set_fixed_name=set_fixed_name,
                        set_tensile_name=set_tensile_name, bd_fixed_name=bd_fixed_name, bd_tensile_name=bd_tensile_name,
                        step_name=step_name, Amp_name=Amp_name)
        create_plane(model_name=model_name, part_name=part_name, l1=l1, l2=l2, l3=l3, l4=l4)
        mesh_3D(model_name=model_name, part_name=part_name, longwide_number=longwide_number,
                shortwide_number=shortwide_number, deep_number=deep_number)
        create_job_3D(model_name=model_name, job_name=job_name, save_address=save_address)
