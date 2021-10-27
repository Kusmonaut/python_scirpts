import numpy as np
C_METER_PER_SECONDS	= 299702547				#Speed of Light m/s

class MultiLateration:
    def __init__(self) -> None:
        pass
        self.__numNodes = 0
        self.__S = 0
        self.__R = 0
        self.__Sw = 0
        self.__SwTSw = 0
        self.__refNodeCoords = 0

    def __calculateSwTSw(self):

        _x = np.dot(self.__S.T, self.__S)

        det = np.linalg.det(_x)

        if det == np.nan:
            return 0

        _r = np.linalg.inv(_x)
        
        self.__R = np.sqrt(np.sum(np.square(self.__S), 1, keepdims=True))
        self.__Sw = np.dot(_r , self.__S.T)
        self.__SwTSw = np.dot(self.__Sw.T, self.__Sw)

        return 1

    def setNodes(self, node_coords, cleSolver3D):

        self.__numNodes, _ = np.shape(node_coords)

        if cleSolver3D:
            self.__refNodeCoords = np.array(node_coords[0,:3])
            self.__S = np.empty((self.__numNodes-1, 3))
        else:
            self.__refNodeCoords = np.array(node_coords[0,:2])
            self.__S = np.empty((self.__numNodes-1, 2))

        for i, pos in enumerate(node_coords):
            if i == 0:
                refNodePos = pos
            else:
                self.__S[(i-1),:] =  (pos - refNodePos)

        return self.__calculateSwTSw()

    def multilaterate(self, tdoa, cleSolver3D):
        
        ddoa = np.dot((tdoa.T- tdoa[0, 0]), C_METER_PER_SECONDS)
        ddoa = ddoa[ 1: self.__numNodes]
        delta = np.square(self.__R) - np.square(ddoa)

        a = np.dot(np.dot(ddoa.T, self.__SwTSw), ddoa)
        a = 4 - 4 * a
        b = np.dot(np.dot(ddoa.T, self.__SwTSw), delta)
        b = 4 * b
        c = np.dot(np.dot(delta.T, self.__SwTSw), delta)
        c = -1 * c

        t = b * b - (4 * a * c)

        if t < 0:
            result1 = np.empty((1,1))
            result1[0, 0] = 0
        else:

            rs1 = (-b + np.sqrt(t)) / (2 * a)

            if rs1 < 0:
                result1 = np.empty((1,1))
                result1[0, 0] = 0
            else:

                delta2rsd1 = delta - ddoa * 2.0 * rs1

                result1 = (self.__refNodeCoords.T + (np.dot(self.__Sw, delta2rsd1) * 0.5)).T
                
                if not cleSolver3D:
                    # return result as array with x, y, z if 2D solver append a zero for axe z
                    result1 = np.append(result1, [[0]], axis=1)


        if (np.isnan(result1)).any():
            result1 = np.empty((1,1))
            result1[0, 0] = 0
        
        return result1