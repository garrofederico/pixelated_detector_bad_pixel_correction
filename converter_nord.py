import os
import pyxem as pxm

def save_signal(filename, filename_output, probe_x, probe_y, flyback):
    try:
        if not os.path.exists(filename_output):
            print(filename)
            frames = (probe_x + flyback) * probe_y
            s = pxm.load_mib(filename, reshape=False)
            data_reshape = s.data[0:frames].reshape((probe_y, probe_x + flyback, 256, 256))
            s1 = pxm.signals.LazyElectronDiffraction2D(data_reshape)
            s2 = s1.inav[0:probe_x, 0:probe_y]
            s2.change_dtype("uint16")
            s2.save(filename_output)# chunks=(32,32,32,32))
        else:
            print("{0} already exist".format(filename))
    except ValueError as err:
        print(filename, "failed due to:", err)

# save_signal("20220482048204820486 204830820/default.mib", "002048_STEM_DPC_256_256.hspy", 256, 256, 0)
