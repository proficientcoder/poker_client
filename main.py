import requests
from multiprocessing import Process
import time

from inc.table import tableMain
from inc.lobby import lobbyMain
import inc.support as support


if __name__ == '__main__':
    tables = []

    lobby = Process(target=lobbyMain, args=())
    lobby.start()

    # while True:
    #     time.sleep(5)

    ###########################

    while lobby.is_alive():
        results = requests.get(f'{support.host}/poker/listMyTables/', params={'key': support.key})
        results = results.json()
        results = results['tables']

        nt = []
        for t in tables:
            if t[1].is_alive():
                nt.append(t)
        tables = nt

        for r in results:
            found = False
            for t in tables:
                if t[0] == r:
                    found = True

            if found == False:
                tableId = r
                tableProcess = Process(target=tableMain, args=(tableId,))
                tableProcess.start()
                tables.append([tableId, tableProcess])

        time.sleep(5)