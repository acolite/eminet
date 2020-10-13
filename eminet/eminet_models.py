## def eminet_models
## retrieves L8/TIRS B10 and B11 emissivity from neural network
## written by Quinten Vanhellemont, RBINS
## 2020-10-12
## last updates QV 2020-10-13 added support for LaSRC output reflectances from EE on demand processing

def eminet_models(inp,
                  output = None,
                  sub = None,
                  netname = 'Net2', normalize_inputs = True,
                  use_water_defaults = True, ew_b10=0.9926, ew_b11=0.9877, water_threshold = 0.02,
                  return_result = False, write_result = True, verbosity = 0):

    import glob, os, sys
    import numpy as np
    import json, time

    ## set keras settings
    os.environ['MKL_THREADING_LAYER'] = 'GNU'
    os.environ['KERAS_BACKEND'] = 'tensorflow'

    import keras
    from keras.models import Sequential
    from keras.layers import Dense
    from keras.models import load_model

    from osgeo import gdal
    import eminet as em

    ## select model
    model_file = None
    model_dir = '{}/nets'.format(em.config['data_path'])
    if netname == 'Net1':
        model_file = 'ECOSTRESS_manmade_rock_soil_vegetation_water_1234567_64x4.h5'
    elif netname == 'Net2':
        model_file = 'ECOSTRESS_manmade_soil_vegetation_water_1234567_64x4.h5'
    else:
        model_file = '{}'.format(netname)
    ## open model
    model_path = '{}/{}'.format(model_dir, model_file)
    if verbosity > 2: print('Opening model file {}'.format(model_path))
    model = load_model(model_path)
    ## read metadata
    mfile = model_path.replace('.h5', '_meta.json')
    if verbosity > 2: print('Opening model metadata {}'.format(mfile))
    meta = json.load(open(mfile, 'r'))

    ## set spectrum to None
    spect = None
    ## input type not yet known
    inp_type = None
    ## if string then inp is likely a file or directory
    if type(inp) is str:
        if inp_type is None:
            try:
                gatts = em.nc_gatts(inp)
                inp_type = gatts['generated_by']
                datasets = em.nc_datasets(inp)
                print(inp_type)
            except:
                inp_type = None
        if inp_type is None:
            try:
                files = glob.glob('{}/*_sr_band[1-7].tif'.format(inp))
                if len(files) == 7:
                    inp_type = 'LaSRC'
                    files.sort()
            except:
                inp_type = None
        if inp_type is None:
            if verbosity > 1: print('Input {} not recognised.'.format(inp))
            return(1)

    ## read image data
    if inp_type in ['ACOLITE', 'LaSRC']:
        if verbosity > 2: print('Reading {} data'.format(inp_type))
        if inp_type == 'LaSRC':
            for fi, file in enumerate(files):
                gdal.UseExceptions()
                band = gdal.Open(file)
                data = band.ReadAsArray() * 0.0001 # from LSDS-1368_L8_C1-LandSurfaceReflectanceCode-LASRC_ProductGuide-v3.pdf


                if fi == 0:
                    GeoTransform = band.GetGeoTransform()
                    Projection = band.GetProjection()
                    data_dim = data.shape
                    spect = data.flatten()
                else:
                    spect = np.vstack((spect, data.flatten()))
        elif inp_type == 'ACOLITE':
            di = 0
            for ds in datasets:
                if 'rhos_' not in ds: continue
                data = em.nc_data(inp,ds)

                if di == 0:
                    data_dim = data.shape
                    spect = data.flatten()
                else:
                    spect = np.vstack((spect, data.flatten()))
                di+=1

        ## transpose to n,7
        spect = spect.T
    else:
        ## if a spectrum is given, convert to array and stack if needed
        if (type(inp) is list) or (type(inp) is np.ndarray):
                if type(inp) is list:
                    tmp = np.asarray(inp)
                    tmp.astype(float)

                if len(tmp.shape) == 1:
                    spect = tmp[np.newaxis,]
                else:
                    spect = tmp

    ## use water emissivity defaults for pixels with low swir reflectance
    if use_water_defaults:
        water_sub = np.where(spect[:, -2] < water_threshold)[0]

    ## mask scene edges
    if inp_type == 'ACOLITE':
        edge_sub = np.where(np.isnan(spect[:, -2]))[0]
    if inp_type == 'LaSRC':
        edge_sub = np.where(spect[:, -2] == -9999*0.0001)[0]

    ## reflectance to percent
    spect *= 100

    ## normalise to input distribution
    for ik in range(spect.shape[1]):
        spect[:,ik] = (spect[:,ik]-meta['xmean'][ik])/meta['xstd'][ik]

    ## run prediction
    if verbosity > 0: print('Running emissivity retrieval for {} ({} spectra)'.format(netname, spect.shape[0]))
    tir_pred = model.predict(spect)

    ## mask reflectance <0 and >100
    tir_pred[tir_pred<0] = np.nan
    tir_pred[tir_pred>100] = np.nan

    ## convert reflectance to emissivity 0--1
    r10 = tir_pred[:,0]
    em10 = 1-r10/100

    r11 = tir_pred[:,1]
    em11 = 1-r11/100

    ## set water values
    if use_water_defaults:
        if len(water_sub)>0:
            em10[water_sub] = ew_b10
            em11[water_sub] = ew_b11

    ## mask edges
    if inp_type in ['ACOLITE', 'LaSRC']:
        if len(edge_sub)>0:
            em10[edge_sub] = np.nan
            em11[edge_sub] = np.nan

        ## reform to 2D
        em10 = em10.reshape(data_dim)
        em11 = em11.reshape(data_dim)

        if inp_type == 'ACOLITE':
            out = inp.replace('L2R.nc', 'L2R_em.nc')
        elif inp_type == 'LaSRC':
            out = file.replace('band7.tif', 'em.tif')

        if output is not None:
            out = '{}/{}'.format(output, os.path.basename(out))
        if not os.path.exists(os.path.dirname(out)):
            os.makedirs(os.path.exists(os.path.dirname(out)))

        ## write outputs
        if write_result:
            if verbosity > 2: print('Writing results to {}'.format(out))
            if inp_type == 'ACOLITE':
                ## write output file
                lat = em.nc_data(inp, 'lat')
                em.nc_write(out, 'lat', lat, new=True)
                lat = None

                lon = em.nc_data(inp, 'lon')
                em.nc_write(out, 'lon', lon)
                lon = None

                em.nc_write(out, 'em10', em10)
                em.nc_write(out, 'em11', em11)
            elif inp_type == 'LaSRC':
                driver = gdal.GetDriverByName("GTiff")
                dso = driver.Create(out, data_dim[1], data_dim[0], 2, gdal.GDT_Float32)
                dso.SetGeoTransform(GeoTransform)
                dso.SetProjection(Projection)
                dso.GetRasterBand(1).WriteArray(em10)
                dso.GetRasterBand(2).WriteArray(em11)
                dso.FlushCache()
                dso = None


    if inp_type is None:
        return(em10, em11)
    else:
        if return_result:
            return(em10, em11)
