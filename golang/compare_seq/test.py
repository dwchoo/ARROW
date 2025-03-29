
import ctypes
lib_path = '/root/volume/golang/workspace/compare_seq/library.so'


class GoString(ctypes.Structure):
    _fields_ = [("p", ctypes.c_char_p), ("n", ctypes.c_longlong)]


class GoSlice(ctypes.Structure):
    _fields_ = [("data", ctypes.POINTER(ctypes.c_void_p)),
                ("len", ctypes.c_longlong), ("cap", ctypes.c_longlong)]


library = ctypes.cdll.LoadLibrary(lib_path)
result_path = "save.csv"
query = 'ACAGAAGCCTTTCCGTGCCTNGG'
data_path = '/root/volume/golang/workspace/compare_seq/data.csv'


result_path_go = GoString(result_path.encode('utf-8'), len(result_path))
query_go = GoString(query.encode('utf-8'), len(query))
data_path_go = GoString(data_path.encode('utf-8'), len(data_path))

library.ResultSaveCSV.argtypes = [GoString, GoString, GoString]
library.ResultSaveCSV.restype = GoString

results = library.ResultSaveCSV(result_path_go, query_go, data_path_go)
print(str(results.p[:results.n]))
